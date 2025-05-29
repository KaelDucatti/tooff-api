from functools import wraps
from flask import request, jsonify, g
from typing import Callable, Any, Dict, Optional, Union
import sys
import os
import jwt

# Adiciona o diretório pai ao path para permitir imports relativos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database.crud import obter_usuario, obter_grupo, obter_evento
from api.database.models import TipoUsuario, Usuario

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

def extrair_usuario_id_do_token() -> Optional[int]:
    """Extrai o user_id do JWT token"""
    return get_current_user_id()

def verificar_permissao_empresa(usuario_id: int, empresa_id: int) -> bool:
    """Verifica se o usuário tem permissão para acessar dados da empresa"""
    usuario = obter_usuario(usuario_id)
    if not usuario:
        return False
    
    # RH tem acesso apenas à sua própria empresa
    if usuario.tipo_usuario == TipoUsuario.RH:
        if not usuario.grupo_id:
            return False
        grupo = obter_grupo(usuario.grupo_id)
        return bool(grupo and grupo.empresa_id == empresa_id)
    
    # Gestores e usuários comuns também só acessam sua empresa
    if usuario.grupo_id:
        grupo = obter_grupo(usuario.grupo_id)
        return bool(grupo and grupo.empresa_id == empresa_id)
    
    return False

def verificar_permissao_grupo(usuario_id: int, grupo_id: int) -> bool:
    """Verifica se o usuário tem permissão para acessar dados do grupo"""
    usuario = obter_usuario(usuario_id)
    if not usuario:
        return False
    
    grupo = obter_grupo(grupo_id)
    if not grupo:
        return False
    
    # RH pode acessar qualquer grupo da sua empresa
    if usuario.tipo_usuario == TipoUsuario.RH:
        if not usuario.grupo_id:
            return False
        grupo_usuario = obter_grupo(usuario.grupo_id)
        return bool(grupo_usuario and grupo_usuario.empresa_id == grupo.empresa_id)
    
    # Gestores só podem acessar seu próprio grupo
    if usuario.tipo_usuario == TipoUsuario.GESTOR:
        return usuario.grupo_id == grupo_id
    
    # Usuários comuns só podem visualizar seu próprio grupo
    if usuario.tipo_usuario == TipoUsuario.COMUM:
        return usuario.grupo_id == grupo_id
    
    return False

def verificar_permissao_usuario_target(usuario_id: int, usuario_target_id: int) -> bool:
    """Verifica se o usuário tem permissão para acessar dados de outro usuário"""
    usuario = obter_usuario(usuario_id)
    usuario_target = obter_usuario(usuario_target_id)
    
    if not usuario or not usuario_target:
        return False
    
    # Usuário pode sempre acessar seus próprios dados
    if usuario_id == usuario_target_id:
        return True
    
    # RH pode acessar usuários da mesma empresa
    if usuario.tipo_usuario == TipoUsuario.RH:
        if not usuario.grupo_id or not usuario_target.grupo_id:
            return False
        grupo_rh = obter_grupo(usuario.grupo_id)
        grupo_target = obter_grupo(usuario_target.grupo_id)
        return bool(grupo_rh and grupo_target and grupo_rh.empresa_id == grupo_target.empresa_id)
    
    # Gestores podem acessar usuários do mesmo grupo
    if usuario.tipo_usuario == TipoUsuario.GESTOR:
        return usuario.grupo_id == usuario_target.grupo_id
    
    # Usuários comuns só podem visualizar usuários do mesmo grupo
    if usuario.tipo_usuario == TipoUsuario.COMUM:
        return usuario.grupo_id == usuario_target.grupo_id
    
    return False

def verificar_permissao_evento(usuario_id: int, evento_id: int) -> bool:
    """Verifica se o usuário tem permissão para acessar um evento"""
    usuario = obter_usuario(usuario_id)
    evento = obter_evento(evento_id)
    
    if not usuario or not evento:
        return False
    
    # Usuário pode sempre acessar seus próprios eventos
    if evento.usuario_id == usuario_id:
        return True
    
    # RH pode acessar eventos de usuários da mesma empresa
    if usuario.tipo_usuario == TipoUsuario.RH:
        return verificar_permissao_usuario_target(usuario_id, evento.usuario_id)
    
    # Gestores podem acessar eventos de usuários do mesmo grupo
    if usuario.tipo_usuario == TipoUsuario.GESTOR:
        return verificar_permissao_usuario_target(usuario_id, evento.usuario_id)
    
    # Usuários comuns só podem acessar eventos de usuários do mesmo grupo (visualização)
    if usuario.tipo_usuario == TipoUsuario.COMUM:
        return verificar_permissao_usuario_target(usuario_id, evento.usuario_id)
    
    return False

# Decoradores para aplicar nas rotas
def requer_permissao_empresa(f: Callable) -> Callable:
    """Decorator para verificar permissão de empresa"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        empresa_id = kwargs.get('empresa_id') or (request.json.get('empresa_id') if request.json else None)
        if empresa_id and not verificar_permissao_empresa(usuario_id, empresa_id):
            return jsonify({"erro": "Sem permissão para acessar dados desta empresa"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def requer_permissao_grupo(f: Callable) -> Callable:
    """Decorator para verificar permissão de grupo"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        grupo_id = kwargs.get('grupo_id') or (request.json.get('grupo_id') if request.json else None)
        if grupo_id and not verificar_permissao_grupo(usuario_id, grupo_id):
            return jsonify({"erro": "Sem permissão para acessar dados deste grupo"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def requer_permissao_usuario(f: Callable) -> Callable:
    """Decorator para verificar permissão de usuário"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        usuario_target_id = kwargs.get('usuario_id') or kwargs.get('usuario_target_id')
        if usuario_target_id and not verificar_permissao_usuario_target(usuario_id, usuario_target_id):
            return jsonify({"erro": "Sem permissão para acessar dados deste usuário"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def requer_permissao_evento(f: Callable) -> Callable:
    """Decorator para verificar permissão de evento"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        evento_id = kwargs.get('evento_id')
        if evento_id and not verificar_permissao_evento(usuario_id, evento_id):
            return jsonify({"erro": "Sem permissão para acessar este evento"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def filtrar_por_escopo_usuario(usuario_id: int) -> Optional[Dict[str, Union[int, None]]]:
    """Retorna filtros baseados no escopo do usuário"""
    usuario = obter_usuario(usuario_id)
    if not usuario:
        return None
    
    if usuario.tipo_usuario == TipoUsuario.RH:
        # RH vê apenas sua empresa
        if usuario.grupo_id:
            grupo = obter_grupo(usuario.grupo_id)
            if grupo and grupo.empresa_id:
                return {"empresa_id": grupo.empresa_id}
        return None
    elif usuario.tipo_usuario == TipoUsuario.GESTOR:
        # Gestor vê apenas seu grupo
        if usuario.grupo_id:
            return {"grupo_id": usuario.grupo_id}
        return None
    elif usuario.tipo_usuario == TipoUsuario.COMUM:
        # Usuário comum vê apenas seu grupo
        if usuario.grupo_id:
            return {"grupo_id": usuario.grupo_id}
        return None
    
    return None
