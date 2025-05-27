from flask import Blueprint, request, jsonify
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError

from ..database.crud import (
    criar_usuario, listar_usuarios, obter_usuario,
    atualizar_usuario, deletar_usuario, usuario_para_dict
)
from ..database.models import TipoUsuario

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('', methods=['GET'])
def listar():
    """Lista usuários com filtros opcionais"""
    try:
        grupo_id = request.args.get('grupo_id', type=int)
        tipo_usuario = request.args.get('tipo_usuario')
        ativos_apenas = request.args.get('ativos', 'true').lower() == 'true'
        
        # Converte string para enum se fornecido
        tipo_enum = None
        if tipo_usuario:
            try:
                tipo_enum = TipoUsuario(tipo_usuario)
            except ValueError:
                return jsonify({"erro": "Tipo de usuário inválido"}), 400
        
        usuarios = listar_usuarios(
            grupo_id=grupo_id, 
            tipo_usuario=tipo_enum, 
            ativos_apenas=ativos_apenas
        )
        return jsonify([usuario_para_dict(u) for u in usuarios]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
def obter(usuario_id: int):
    """Obtém um usuário específico"""
    try:
        usuario = obter_usuario(usuario_id)
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
        # Converte string para enum
        tipo_usuario = TipoUsuario(dados.get("tipo_usuario", "comum"))
        
        usuario = criar_usuario(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            inicio_na_empresa=dados["inicio_na_empresa"],
            tipo_usuario=tipo_usuario,
            grupo_id=dados.get("grupo_id")
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

@usuarios_bp.route('/<int:usuario_id>', methods=['PUT'])
def atualizar(usuario_id: int):
    """Atualiza um usuário"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        # Converte tipo_usuario se fornecido
        if "tipo_usuario" in dados:
            dados["tipo_usuario"] = TipoUsuario(dados["tipo_usuario"])
        
        sucesso = atualizar_usuario(usuario_id, **dados)
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

@usuarios_bp.route('/<int:usuario_id>', methods=['DELETE'])
def deletar(usuario_id: int):
    """Desativa um usuário"""
    try:
        sucesso = deletar_usuario(usuario_id)
        if not sucesso:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify({"status": "Usuário desativado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
