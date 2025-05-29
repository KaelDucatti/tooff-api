from functools import wraps
from flask import request, jsonify, g
import jwt
import os
from typing import Optional

from ..database.crud import obter_usuario
from ..database.models import Usuario

def jwt_required(f):
    """Decorator para proteger rotas com JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                # Formato: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"erro": "Formato de token inválido"}), 401
        
        if not token:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        try:
            secret_key = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            if payload.get('type') != 'access':
                return jsonify({"erro": "Tipo de token inválido"}), 401
            
            # Armazenar informações do usuário no contexto da requisição
            g.current_user_id = payload['user_id']
            g.current_user_email = payload['email']
            g.current_user_tipo = payload['tipo_usuario']
            
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401
        except Exception as e:
            return jsonify({"erro": f"Erro na validação do token: {str(e)}"}), 401
        
        return f(*args, **kwargs)
    return decorated

def get_current_user() -> Optional[Usuario]:
    """Retorna o usuário atual baseado no token JWT"""
    if hasattr(g, 'current_user_id'):
        return obter_usuario(g.current_user_id)
    return None

def get_current_user_id() -> Optional[int]:
    """Retorna o ID do usuário atual"""
    return getattr(g, 'current_user_id', None)

def get_current_user_tipo() -> Optional[str]:
    """Retorna o tipo do usuário atual"""
    return getattr(g, 'current_user_tipo', None)

def require_permission(allowed_types: list):
    """Decorator para verificar permissões específicas"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_tipo = get_current_user_tipo()
            if user_tipo not in allowed_types:
                return jsonify({"erro": "Permissão insuficiente"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# Decorators específicos para cada tipo de usuário
def rh_required(f):
    """Decorator que permite apenas usuários RH"""
    return require_permission(['rh'])(f)

def gestor_or_rh_required(f):
    """Decorator que permite gestores e RH"""
    return require_permission(['gestor', 'rh'])(f)

def authenticated_user_required(f):
    """Decorator que permite qualquer usuário autenticado"""
    return require_permission(['comum', 'gestor', 'rh'])(f)
