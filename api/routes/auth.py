from flask import Blueprint, request, jsonify
from typing import Dict, Any
import jwt
import datetime
import os

from ..database.crud import autenticar_usuario, usuario_para_dict, obter_usuario
from ..middleware.auth import jwt_required, get_current_user

auth_bp = Blueprint('auth', __name__)

def generate_tokens(usuario):
    """Gera tokens de acesso e refresh para o usuário"""
    secret_key = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
    
    # Token de acesso (1 hora)
    access_payload = {
        'user_id': usuario.id,
        'email': usuario.email,
        'tipo_usuario': usuario.tipo_usuario.value,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow(),
        'type': 'access'
    }
    
    # Token de refresh (7 dias)
    refresh_payload = {
        'user_id': usuario.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow(),
        'type': 'refresh'
    }
    
    access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, secret_key, algorithm='HS256')
    
    return access_token, refresh_token

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de autenticação com JWT"""
    dados: Dict[str, Any] = request.get_json(force=True)
    email = dados.get('email')
    senha = dados.get('senha')
    
    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    
    try:
        usuario = autenticar_usuario(email, senha)
        if usuario is None:
            return jsonify({"autenticado": False, "erro": "Credenciais inválidas"}), 401
        
        # Gerar tokens JWT
        access_token, refresh_token = generate_tokens(usuario)
        
        return jsonify({
            "autenticado": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # 1 hora em segundos
            "usuario": usuario_para_dict(usuario)
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Renovar token de acesso usando refresh token"""
    dados = request.get_json(force=True)
    refresh_token = dados.get('refresh_token')
    
    if not refresh_token:
        return jsonify({"erro": "Refresh token necessário"}), 400
    
    try:
        secret_key = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
        payload = jwt.decode(refresh_token, secret_key, algorithms=['HS256'])
        
        if payload.get('type') != 'refresh':
            return jsonify({"erro": "Token inválido"}), 401
        
        # Buscar usuário
        usuario = obter_usuario(payload['user_id'])
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Gerar novo token de acesso
        access_token, _ = generate_tokens(usuario)
        
        return jsonify({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({"erro": "Refresh token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"erro": "Refresh token inválido"}), 401
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """Logout (invalidar token)"""
    # Em uma implementação real, você adicionaria o token a uma blacklist
    return jsonify({"message": "Logout realizado com sucesso"}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required
def me():
    """Retorna informações do usuário atual"""
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        return jsonify({
            "usuario": usuario_para_dict(usuario_atual)
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
