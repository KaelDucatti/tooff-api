from functools import wraps
from flask import request, jsonify, g, current_app
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
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(" ")[1]
                else:
                    token = auth_header
            except IndexError:
                return jsonify({"erro": "Formato de token inválido"}), 401
        
        if not token:
            return jsonify({"erro": "Token de acesso necessário"}), 401
        
        try:
            # Usar a mesma secret key do .env
            secret_key = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Verificar se é um access token
            if payload.get('type') != 'access':
                return jsonify({"erro": "Tipo de token inválido"}), 401
            
            # Armazenar informações do usuário no contexto da requisição
            # Usar user_cpf em vez de user_id (nova estrutura)
            g.current_user_cpf = payload.get('user_cpf')
            g.current_user_email = payload.get('email')
            g.current_user_tipo = payload.get('tipo_usuario')
            g.current_user_flag_gestor = payload.get('flag_gestor', 'N')
            g.current_user_grupo_id = payload.get('grupo_id')
            g.current_user_uf = payload.get('uf')
            
            # Verificar se o usuário ainda existe e está ativo
            if g.current_user_cpf:
                usuario = obter_usuario(g.current_user_cpf)
                if not usuario or not usuario.ativo:
                    return jsonify({"erro": "Usuário inválido ou inativo"}), 401
            
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
    if hasattr(g, 'current_user_cpf') and g.current_user_cpf:
        return obter_usuario(g.current_user_cpf)
    return None

def get_current_user_cpf() -> Optional[int]:
    """Retorna o CPF do usuário atual"""
    return getattr(g, 'current_user_cpf', None)

def get_current_user_tipo() -> Optional[str]:
    """Retorna o tipo do usuário atual"""
    return getattr(g, 'current_user_tipo', None)

def get_current_user_flag_gestor() -> Optional[str]:
    """Retorna a flag de gestor do usuário atual"""
    return getattr(g, 'current_user_flag_gestor', 'N')

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
    @wraps(f)
    def decorated(*args, **kwargs):
        user_tipo = get_current_user_tipo()
        flag_gestor = get_current_user_flag_gestor()
        
        if user_tipo == 'rh' or flag_gestor == 'S':
            return f(*args, **kwargs)
        else:
            return jsonify({"erro": "Permissão insuficiente"}), 403
    return decorated

def authenticated_user_required(f):
    """Decorator que permite qualquer usuário autenticado"""
    return require_permission(['comum', 'gestor', 'rh'])(f)
