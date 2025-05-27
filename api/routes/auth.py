from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import autenticar_usuario, usuario_para_dict

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de autenticação"""
    dados: Dict[str, Any] = request.get_json(force=True)
    email = dados.get('email')
    senha = dados.get('senha')
    
    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    
    try:
        usuario = autenticar_usuario(email, senha)
        if usuario is None:
            return jsonify({"autenticado": False, "erro": "Credenciais inválidas"}), 401
        
        return jsonify({
            "autenticado": True,
            "usuario": usuario_para_dict(usuario)
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def me():
    """Retorna informações do usuário atual (implementar autenticação JWT posteriormente)"""
    # TODO: Implementar verificação de token JWT
    return jsonify({"erro": "Endpoint não implementado"}), 501
