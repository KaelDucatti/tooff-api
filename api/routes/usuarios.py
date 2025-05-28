from flask import Blueprint, request, jsonify
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError

from ..database.crud import (
    criar_usuario, listar_usuarios, obter_usuario,
    atualizar_usuario, deletar_usuario, usuario_para_dict
)
from ..database.models import TipoUsuario
from ..middleware.auth import (
    requer_permissao_usuario, filtrar_por_escopo_usuario,
    extrair_usuario_id_do_token, verificar_permissao_grupo
)

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('', methods=['GET'])
def listar():
    """Lista usuários com base no escopo do usuário logado"""
    try:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        grupo_id = request.args.get('grupo_id', type=int)
        tipo_usuario = request.args.get('tipo_usuario')
        ativos_apenas = request.args.get('ativos', 'true').lower() == 'true'
        
        # Aplica filtros baseados no escopo do usuário
        filtros = filtrar_por_escopo_usuario(usuario_id)
        
        # Converte string para enum se fornecido
        tipo_enum = None
        if tipo_usuario:
            try:
                tipo_enum = TipoUsuario(tipo_usuario)
            except ValueError:
                return jsonify({"erro": "Tipo de usuário inválido"}), 400
        
        # Determina o grupo_id baseado no escopo
        if filtros and 'grupo_id' in filtros:
            # Gestores e usuários comuns veem apenas seu grupo
            grupo_id_final = filtros['grupo_id']
        elif filtros and 'empresa_id' in filtros:
            # RH pode especificar grupo ou ver todos da empresa
            grupo_id_final = grupo_id  # Pode ser None para ver todos da empresa
        else:
            return jsonify([]), 200
        
        usuarios = listar_usuarios(
            grupo_id=grupo_id_final, 
            tipo_usuario=tipo_enum, 
            ativos_apenas=ativos_apenas
        )
        
        # Para RH, filtra por empresa se não especificou grupo
        if filtros and 'empresa_id' in filtros and not grupo_id:
            from ..database.crud import obter_grupo
            usuarios_filtrados = []
            for usuario in usuarios:
                if usuario.grupo_id:
                    grupo = obter_grupo(usuario.grupo_id)
                    if grupo and grupo.empresa_id == filtros['empresa_id']:
                        usuarios_filtrados.append(usuario)
            usuarios = usuarios_filtrados
        
        return jsonify([usuario_para_dict(u) for u in usuarios]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@usuarios_bp.route('/<int:usuario_target_id>', methods=['GET'])
@requer_permissao_usuario
def obter(usuario_target_id: int):
    """Obtém um usuário específico"""
    try:
        usuario = obter_usuario(usuario_target_id)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify(usuario_para_dict(usuario)), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@usuarios_bp.route('', methods=['POST'])
def criar():
    """Cria um novo usuário"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Verifica permissões baseadas no tipo de usuário
        from ..database.crud import obter_usuario as get_user
        usuario_logado = get_user(usuario_id)
        if not usuario_logado:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        grupo_id = dados.get("grupo_id")
        
        # Verifica se pode criar usuário no grupo especificado
        if grupo_id and not verificar_permissao_grupo(usuario_id, grupo_id):
            return jsonify({"erro": "Sem permissão para criar usuários neste grupo"}), 403
        
        # RH e Gestores podem criar usuários
        if usuario_logado.tipo_usuario not in [TipoUsuario.RH, TipoUsuario.GESTOR]:
            return jsonify({"erro": "Sem permissão para criar usuários"}), 403
        
        # Converte string para enum
        tipo_usuario = TipoUsuario(dados.get("tipo_usuario", "comum"))
        
        usuario = criar_usuario(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            inicio_na_empresa=dados["inicio_na_empresa"],
            tipo_usuario=tipo_usuario,
            grupo_id=grupo_id
        )
        return jsonify(usuario_para_dict(usuario)), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except ValueError as ve:
        return jsonify({"erro": f"Valor inválido: {ve}"}), 400
    except IntegrityError as ie:
        if "UNIQUE constraint failed: usuarios.email" in str(ie):
            return jsonify({"erro": "Email já cadastrado"}), 409
        else:
            return jsonify({"erro": "Erro de integridade dos dados"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@usuarios_bp.route('/<int:usuario_target_id>', methods=['PUT'])
@requer_permissao_usuario
def atualizar(usuario_target_id: int):
    """Atualiza um usuário"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_id = extrair_usuario_id_do_token()
        if usuario_id is None:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        from ..database.crud import obter_usuario as get_user
        usuario_logado = get_user(usuario_id)
        
        if not usuario_logado:
            return jsonify({"erro": "Usuário logado não encontrado"}), 404
        
        # Usuários comuns só podem atualizar alguns campos próprios
        if usuario_logado.tipo_usuario == TipoUsuario.COMUM and usuario_id == usuario_target_id:
            # Permite apenas atualização de senha e dados pessoais
            campos_permitidos = ['senha', 'nome']
            dados_filtrados = {k: v for k, v in dados.items() if k in campos_permitidos}
            dados = dados_filtrados
        elif usuario_logado.tipo_usuario == TipoUsuario.COMUM:
            return jsonify({"erro": "Usuários comuns só podem atualizar próprios dados"}), 403
        
        # Converte tipo_usuario se fornecido
        if "tipo_usuario" in dados:
            dados["tipo_usuario"] = TipoUsuario(dados["tipo_usuario"])
        
        sucesso = atualizar_usuario(usuario_target_id, **dados)
        if not sucesso:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify({"status": "Usuário atualizado"}), 200
    except ValueError as ve:
        return jsonify({"erro": f"Valor inválido: {ve}"}), 400
    except IntegrityError as ie:
        if "UNIQUE constraint failed: usuarios.email" in str(ie):
            return jsonify({"erro": "Email já cadastrado"}), 409
        else:
            return jsonify({"erro": "Erro de integridade dos dados"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@usuarios_bp.route('/<int:usuario_target_id>', methods=['DELETE'])
@requer_permissao_usuario
def deletar(usuario_target_id: int):
    """Desativa um usuário"""
    try:
        usuario_id = extrair_usuario_id_do_token()
        if usuario_id is None:
            return jsonify({"erro": "Token de autenticação necessário"}), 401

        from ..database.crud import obter_usuario as get_user
        usuario_logado = get_user(usuario_id)
        
        if not usuario_logado:
            return jsonify({"erro": "Usuário logado não encontrado"}), 404
        
        # Apenas RH e Gestores podem desativar usuários
        if usuario_logado.tipo_usuario not in [TipoUsuario.RH, TipoUsuario.GESTOR]:
            return jsonify({"erro": "Sem permissão para desativar usuários"}), 403
        
        # Usuário não pode desativar a si mesmo
        if usuario_id == usuario_target_id:
            return jsonify({"erro": "Não é possível desativar sua própria conta"}), 400
        
        sucesso = deletar_usuario(usuario_target_id)
        if not sucesso:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify({"status": "Usuário desativado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
