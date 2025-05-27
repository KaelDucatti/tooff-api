from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import (
    criar_evento, listar_eventos, obter_evento,
    atualizar_evento, deletar_evento, evento_para_dict,
    aprovar_evento, rejeitar_evento, obter_usuario
)
from ..database.models import TipoAusencia, Turno, StatusEvento

eventos_bp = Blueprint('eventos', __name__)

@eventos_bp.route('', methods=['GET'])
def listar():
    """Lista eventos com filtros opcionais"""
    try:
        usuario_id = request.args.get('usuario_id', type=int)
        grupo_id = request.args.get('grupo_id', type=int)
        status = request.args.get('status')
        
        # Converte string para enum se fornecido
        status_enum = None
        if status:
            try:
                status_enum = StatusEvento(status)
            except ValueError:
                return jsonify({"erro": "Status inválido"}), 400
        
        eventos = listar_eventos(
            usuario_id=usuario_id,
            grupo_id=grupo_id,
            status=status_enum
        )
        return jsonify([evento_para_dict(e) for e in eventos]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>', methods=['GET'])
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
def criar():
    """Cria um novo evento"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        # Converte strings para enums
        tipo_ausencia = TipoAusencia(dados["tipo_ausencia"])
        turno = None
        if dados.get("turno"):
            turno = Turno(dados["turno"])
        
        evento = criar_evento(
            usuario_id=dados["usuario_id"],
            data_inicio=dados["data_inicio"],
            data_fim=dados["data_fim"],
            tipo_ausencia=tipo_ausencia,
            turno=turno,
            descricao=dados.get("descricao")
        )
        return jsonify(evento_para_dict(evento)), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except ValueError as ve:
        return jsonify({"erro": f"Valor inválido: {ve}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>', methods=['PUT'])
def atualizar(evento_id: int):
    """Atualiza um evento"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        # Converte enums se fornecidos
        if "tipo_ausencia" in dados:
            dados["tipo_ausencia"] = TipoAusencia(dados["tipo_ausencia"])
        if "turno" in dados and dados["turno"]:
            dados["turno"] = Turno(dados["turno"])
        if "status" in dados:
            dados["status"] = StatusEvento(dados["status"])
        
        sucesso = atualizar_evento(evento_id, **dados)
        if not sucesso:
            return jsonify({"erro": "Evento não encontrado"}), 404
        return jsonify({"status": "Evento atualizado"}), 200
    except ValueError as ve:
        return jsonify({"erro": f"Valor inválido: {ve}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>', methods=['DELETE'])
def deletar(evento_id: int):
    """Deleta um evento"""
    try:
        sucesso = deletar_evento(evento_id)
        if not sucesso:
            return jsonify({"erro": "Evento não encontrado"}), 404
        return jsonify({"status": "Evento deletado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>/aprovar', methods=['POST'])
def aprovar(evento_id: int):
    """Aprova um evento"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        aprovador_id = dados["aprovador_id"]
        observacoes = dados.get("observacoes")
        
        # Verifica se o aprovador existe
        aprovador = obter_usuario(aprovador_id)
        if not aprovador:
            return jsonify({"erro": "Aprovador não encontrado"}), 404
        
        # Verifica se o evento existe
        evento = obter_evento(evento_id)
        if not evento:
            return jsonify({"erro": "Evento não encontrado"}), 404
        
        # Verifica permissão básica (implementar lógica completa posteriormente)
        # Por enquanto, apenas verifica se é gestor ou RH
        if aprovador.tipo_usuario.value not in ['gestor', 'rh']:
            return jsonify({"erro": "Sem permissão para aprovar eventos"}), 403
        
        sucesso = aprovar_evento(evento_id, aprovador_id, observacoes)
        if not sucesso:
            return jsonify({"erro": "Erro ao aprovar evento"}), 500
        
        return jsonify({"status": "Evento aprovado"}), 200
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@eventos_bp.route('/<int:evento_id>/rejeitar', methods=['POST'])
def rejeitar(evento_id: int):
    """Rejeita um evento"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        aprovador_id = dados["aprovador_id"]
        observacoes = dados.get("observacoes")
        
        # Verifica se o aprovador existe
        aprovador = obter_usuario(aprovador_id)
        if not aprovador:
            return jsonify({"erro": "Aprovador não encontrado"}), 404
        
        # Verifica se o evento existe
        evento = obter_evento(evento_id)
        if not evento:
            return jsonify({"erro": "Evento não encontrado"}), 404
        
        # Verifica permissão básica (implementar lógica completa posteriormente)
        # Por enquanto, apenas verifica se é gestor ou RH
        if aprovador.tipo_usuario.value not in ['gestor', 'rh']:
            return jsonify({"erro": "Sem permissão para rejeitar eventos"}), 403
        
        sucesso = rejeitar_evento(evento_id, aprovador_id, observacoes)
        if not sucesso:
            return jsonify({"erro": "Erro ao rejeitar evento"}), 500
        
        return jsonify({"status": "Evento rejeitado"}), 200
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
