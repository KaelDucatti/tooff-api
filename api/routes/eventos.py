from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import (
    criar_evento, listar_eventos, obter_evento,
    atualizar_evento, deletar_evento, evento_para_dict,
    aprovar_evento, rejeitar_evento, obter_usuario
)
from ..middleware.auth import (
    jwt_required, requer_permissao_evento, filtrar_por_escopo_usuario,
    extrair_usuario_cpf_do_token, verificar_permissao_usuario_target
)

eventos_bp = Blueprint('eventos', __name__)

@eventos_bp.route('', methods=['GET'])
@jwt_required
def listar():
    """Lista eventos com base no escopo do usuário"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        usuario_target_cpf = request.args.get('cpf_usuario', type=int)
        grupo_id = request.args.get('grupo_id', type=int)
        status = request.args.get('status')
        
        # Aplica filtros baseados no escopo do usuário
        filtros = filtrar_por_escopo_usuario(usuario_cpf)
        
        # Determina os filtros baseados no escopo
        if filtros and 'grupo_id' in filtros:
            # Gestores e usuários comuns veem eventos do seu grupo
            grupo_id_final = filtros['grupo_id']
        elif filtros and 'cnpj_empresa' in filtros:
            # RH pode especificar grupo ou ver todos da empresa
            grupo_id_final = grupo_id
        else:
            return jsonify([]), 200
        
        # Se especificou usuário, verifica permissão
        if usuario_target_cpf and not verificar_permissao_usuario_target(usuario_cpf, usuario_target_cpf):
            return jsonify({"erro": "Sem permissão para ver eventos deste usuário"}), 403
        
        eventos = listar_eventos(
            cpf_usuario=usuario_target_cpf,
            grupo_id=grupo_id_final,
            status=status
        )
        
        return jsonify([evento_para_dict(e) for e in eventos]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>', methods=['GET'])
@jwt_required
@requer_permissao_evento
def obter(evento_id: int):
    """Obtém um evento específico"""
    try:
        evento = obter_evento(evento_id)
        if not evento:
            return jsonify({"erro": "Evento não encontrado"}), 404
        return jsonify(evento_para_dict(evento)), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('', methods=['POST'])
@jwt_required
def criar():
    """Cria um novo evento"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        cpf_usuario = dados["cpf_usuario"]
        
        # Verifica se pode criar evento para o usuário especificado
        if not verificar_permissao_usuario_target(usuario_cpf, cpf_usuario):
            return jsonify({"erro": "Sem permissão para criar eventos para este usuário"}), 403
        
        # Usuários comuns só podem criar eventos para si mesmos
        usuario_logado = obter_usuario(usuario_cpf)
        if (usuario_logado and usuario_logado.tipo_usuario == 'comum' and 
            usuario_logado.flag_gestor == 'N' and usuario_cpf != cpf_usuario):
            return jsonify({"erro": "Usuários comuns só podem criar eventos próprios"}), 403
        
        # Para eventos criados por usuários comuns, o aprovador inicial é o próprio usuário
        # (será alterado quando aprovado por gestor/RH)
        aprovado_por = dados.get("aprovado_por", usuario_cpf)
        
        evento = criar_evento(
            cpf_usuario=cpf_usuario,
            data_inicio=dados["data_inicio"],
            data_fim=dados["data_fim"],
            id_tipo_ausencia=dados["id_tipo_ausencia"],
            uf=dados["uf"],
            aprovado_por=aprovado_por
        )
        return jsonify(evento_para_dict(evento)), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except ValueError as ve:
        return jsonify({"erro": f"Valor inválido: {ve}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>', methods=['PUT'])
@jwt_required
@requer_permissao_evento
def atualizar(evento_id: int):
    """Atualiza um evento"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
            
        evento = obter_evento(evento_id)
        usuario_logado = obter_usuario(usuario_cpf)
        
        if not evento or not usuario_logado:
            return jsonify({"erro": "Evento ou usuário não encontrado"}), 404
        
        # Usuários comuns só podem editar próprios eventos pendentes
        if (usuario_logado.tipo_usuario == 'comum' and usuario_logado.flag_gestor == 'N' and 
            (evento.cpf_usuario != usuario_cpf or evento.status != 'pendente')):
            return jsonify({"erro": "Só é possível editar próprios eventos pendentes"}), 403
        
        sucesso = atualizar_evento(evento_id, **dados)
        if not sucesso:
            return jsonify({"erro": "Evento não encontrado"}), 404
        return jsonify({"status": "Evento atualizado"}), 200
    except ValueError as ve:
        return jsonify({"erro": f"Valor inválido: {ve}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>', methods=['DELETE'])
@jwt_required
def deletar(evento_id: int):
    """Deleta um evento"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401

        evento = obter_evento(evento_id)
        usuario_logado = obter_usuario(usuario_cpf)

        if not evento or not usuario_logado:
            return jsonify({"erro": "Evento ou usuário não encontrado"}), 404

        # Usuário comum NÃO pode deletar evento de outro
        if (usuario_logado.tipo_usuario == 'comum' and usuario_logado.flag_gestor == 'N' and 
            evento.cpf_usuario != usuario_cpf):
            return jsonify({"erro": "Só é possível deletar próprios eventos pendentes"}), 403

        # Mesmo o próprio usuário comum só deleta se o evento estiver PENDENTE
        if (usuario_logado.tipo_usuario == 'comum' and usuario_logado.flag_gestor == 'N' and 
            evento.status != 'pendente'):
            return jsonify({"erro": "Só é possível deletar próprios eventos pendentes"}), 403

        sucesso = deletar_evento(evento_id)
        if not sucesso:
            return jsonify({"erro": "Evento não encontrado"}), 404

        return jsonify({"status": "Evento deletado"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>/aprovar', methods=['POST'])
@jwt_required
@requer_permissao_evento
def aprovar(evento_id: int):
    """Aprova um evento"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        aprovador_cpf = dados["aprovador_cpf"]
        
        # Verifica se o aprovador existe e tem permissão
        aprovador = obter_usuario(aprovador_cpf)
        if not aprovador:
            return jsonify({"erro": "Aprovador não encontrado"}), 404
        
        # Verifica se o evento existe
        evento = obter_evento(evento_id)
        if not evento:
            return jsonify({"erro": "Evento não encontrado"}), 404
        
        # Verifica permissão para aprovar
        if aprovador.tipo_usuario not in ['rh'] and aprovador.flag_gestor != 'S':
            return jsonify({"erro": "Sem permissão para aprovar eventos"}), 403
        
        # Verifica se o aprovador pode aprovar eventos deste usuário
        if not verificar_permissao_usuario_target(aprovador_cpf, evento.cpf_usuario):
            return jsonify({"erro": "Sem permissão para aprovar eventos deste usuário"}), 403
        
        sucesso = aprovar_evento(evento_id, aprovador_cpf)
        if not sucesso:
            return jsonify({"erro": "Erro ao aprovar evento"}), 500
        
        return jsonify({"status": "Evento aprovado"}), 200
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>/rejeitar', methods=['POST'])
@jwt_required
@requer_permissao_evento
def rejeitar(evento_id: int):
    """Rejeita um evento"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        aprovador_cpf = dados["aprovador_cpf"]
        
        # Verifica se o aprovador existe e tem permissão
        aprovador = obter_usuario(aprovador_cpf)
        if not aprovador:
            return jsonify({"erro": "Aprovador não encontrado"}), 404
        
        # Verifica se o evento existe
        evento = obter_evento(evento_id)
        if not evento:
            return jsonify({"erro": "Evento não encontrado"}), 404
        
        # Verifica permissão para rejeitar
        if aprovador.tipo_usuario not in ['rh'] and aprovador.flag_gestor != 'S':
            return jsonify({"erro": "Sem permissão para rejeitar eventos"}), 403
        
        # Verifica se o aprovador pode rejeitar eventos deste usuário
        if not verificar_permissao_usuario_target(aprovador_cpf, evento.cpf_usuario):
            return jsonify({"erro": "Sem permissão para rejeitar eventos deste usuário"}), 403
        
        sucesso = rejeitar_evento(evento_id, aprovador_cpf)
        if not sucesso:
            return jsonify({"erro": "Erro ao rejeitar evento"}), 500
        
        return jsonify({"status": "Evento rejeitado"}), 200
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
