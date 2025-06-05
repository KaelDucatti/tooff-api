from functools import wraps
from flask import request, jsonify, current_app, g
from typing import Optional, Dict, Any, Callable
import jwt

from ..database.crud import obter_usuario, obter_grupo, obter_evento
from ..database.models import TipoUsuario, FlagGestor

# Armazenamento simples para tokens invalidados (blacklist)
# Em produção, isso deveria ser armazenado em Redis ou outro armazenamento persistente
BLACKLISTED_TOKENS = set()

def extrair_usuario_cpf_do_token() -> Optional[int]:
    """Extrai o CPF do usuário do token JWT"""
    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return None
        
        token = token.split(' ')[1]
        
        # Verifica se o token está na blacklist
        if token in BLACKLISTED_TOKENS:
            return None
            
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload.get('user_cpf')  # Alterado para 'user_cpf' para corresponder ao payload em auth.py
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, IndexError):
        return None

def jwt_required(f):
    """Decorator que requer autenticação JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                return jsonify({"erro": "Token de acesso necessário"}), 401
            
            token = token.split(' ')[1]
            
            # Verifica se o token está na blacklist
            if token in BLACKLISTED_TOKENS:
                return jsonify({"erro": "Token invalidado"}), 401
                
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Verifica se o usuário ainda existe e está ativo
            usuario = obter_usuario(payload['user_cpf'])  # Alterado para 'user_cpf'
            if not usuario or not usuario.ativo:
                return jsonify({"erro": "Usuário inválido ou inativo"}), 401
            
            # Store user info in g for later use
            # Os valores já são strings no banco, não precisam de .value
            g.current_user_cpf = payload['user_cpf']  # Alterado para 'user_cpf'
            g.current_user_tipo = usuario.tipo_usuario
            g.current_user_flag_gestor = usuario.flag_gestor
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401
        except (KeyError, IndexError):
            return jsonify({"erro": "Token malformado"}), 401
        except Exception as e:
            return jsonify({"erro": f"Erro de autenticação: {str(e)}"}), 401
    
    return decorated

def invalidate_token(token):
    """Adiciona um token à blacklist"""
    if token and token.startswith('Bearer '):
        token = token.split(' ')[1]
    BLACKLISTED_TOKENS.add(token)
    return True

def get_current_user():
    """Retorna o usuário atual baseado no token JWT"""
    if hasattr(g, 'current_user_cpf'):
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

# Decoradores específicos para cada tipo de usuário
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


def requer_permissao_usuario(f):
    """Decorator que verifica permissão para acessar dados de usuário"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            usuario_cpf = extrair_usuario_cpf_do_token()
            if not usuario_cpf:
                return jsonify({"erro": "Token de autenticação necessário"}), 401
            
            # Obtém o CPF do usuário target da URL
            cpf_target = kwargs.get('cpf')
            if not cpf_target:
                return jsonify({"erro": "CPF não especificado"}), 400
            
            if not verificar_permissao_usuario_target(usuario_cpf, cpf_target):
                return jsonify({"erro": "Sem permissão para acessar este usuário"}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"erro": str(e)}), 500
    
    return decorated

def requer_permissao_evento(f):
    """Decorator que verifica permissão para acessar evento"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            usuario_cpf = extrair_usuario_cpf_do_token()
            if not usuario_cpf:
                return jsonify({"erro": "Token de autenticação necessário"}), 401
            
            evento_id = kwargs.get('evento_id')
            if not evento_id:
                return jsonify({"erro": "ID do evento não especificado"}), 400
            
            evento = obter_evento(evento_id)
            if not evento:
                return jsonify({"erro": "Evento não encontrado"}), 404
            
            if not verificar_permissao_usuario_target(usuario_cpf, evento.cpf_usuario):
                return jsonify({"erro": "Sem permissão para acessar este evento"}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"erro": str(e)}), 500
    
    return decorated

def verificar_permissao_usuario_target(usuario_cpf: int, target_cpf: int) -> bool:
    """Verifica se o usuário tem permissão para acessar dados de outro usuário"""
    usuario = obter_usuario(usuario_cpf)
    if not usuario:
        return False
    
    # RH pode acessar qualquer usuário da mesma empresa
    # Compara com string diretamente (não enum)
    if usuario.tipo_usuario == TipoUsuario.RH.value:
        target_usuario = obter_usuario(target_cpf)
        if target_usuario and target_usuario.grupo_id and usuario.grupo_id:
            # Verifica se ambos pertencem à mesma empresa
            grupo_usuario = obter_grupo(usuario.grupo_id)
            grupo_target = obter_grupo(target_usuario.grupo_id)
            if grupo_usuario and grupo_target:
                return grupo_usuario.cnpj_empresa == grupo_target.cnpj_empresa
        return False
    
    # Gestores podem acessar usuários do mesmo grupo
    # Compara com string diretamente (não enum)
    if usuario.flag_gestor == FlagGestor.SIM.value:
        target_usuario = obter_usuario(target_cpf)
        if target_usuario:
            return target_usuario.grupo_id == usuario.grupo_id
        return False
    
    # Usuários comuns só podem acessar próprios dados
    return usuario_cpf == target_cpf

def verificar_permissao_grupo(usuario_cpf: int, grupo_id: int) -> bool:
    """Verifica se o usuário tem permissão para gerenciar um grupo"""
    usuario = obter_usuario(usuario_cpf)
    if not usuario:
        return False
    
    # RH pode gerenciar qualquer grupo da mesma empresa
    if usuario.tipo_usuario == TipoUsuario.RH.value:
        if not usuario.grupo_id:
            return False
        grupo_usuario = obter_grupo(usuario.grupo_id)
        grupo_target = obter_grupo(grupo_id)
        if grupo_usuario and grupo_target:
            return grupo_usuario.cnpj_empresa == grupo_target.cnpj_empresa
        return False
    
    # Gestores podem gerenciar apenas seu próprio grupo
    if usuario.flag_gestor == FlagGestor.SIM.value:
        return usuario.grupo_id == grupo_id
    
    return False

def verificar_permissao_empresa(usuario_cpf: int, cnpj_empresa: int) -> bool:
    """Verifica se o usuário tem permissão para acessar dados de uma empresa"""
    usuario = obter_usuario(usuario_cpf)
    if not usuario:
        return False
    
    # RH só pode acessar sua própria empresa
    if usuario.tipo_usuario == TipoUsuario.RH.value:
        if not usuario.grupo_id:
            return False
        grupo = obter_grupo(usuario.grupo_id)
        if grupo:
            return grupo.cnpj_empresa == cnpj_empresa
        return False
    
    return False

def get_empresa_do_usuario_rh(usuario_cpf: int) -> Optional[int]:
    """Retorna o CNPJ da empresa do usuário RH"""
    usuario = obter_usuario(usuario_cpf)
    if not usuario or usuario.tipo_usuario != TipoUsuario.RH.value:
        return None
    
    grupo = obter_grupo(usuario.grupo_id)
    return grupo.cnpj_empresa if grupo else None

def filtrar_por_escopo_usuario(usuario_cpf: int) -> Optional[Dict[str, Any]]:
    """Retorna filtros baseados no escopo do usuário"""
    usuario = obter_usuario(usuario_cpf)
    if not usuario:
        return None
    
    # RH vê dados da empresa
    if usuario.tipo_usuario == TipoUsuario.RH.value:
        grupo = obter_grupo(usuario.grupo_id)
        return {"cnpj_empresa": grupo.cnpj_empresa} if grupo else None
    
    # Gestores veem dados do grupo
    if usuario.flag_gestor == FlagGestor.SIM.value:
        return {"grupo_id": usuario.grupo_id}
    
    # Usuários comuns veem apenas próprios dados
    return {"cpf_usuario": usuario_cpf}
    
# Decoradores para aplicar nas rotas
def requer_permissao_empresa(f: Callable) -> Callable:
    """Decorator para verificar permissão de empresa"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        cnpj_empresa = kwargs.get('cnpj_empresa') or (request.json.get('cnpj_empresa') if request.json else None)
        if cnpj_empresa and not verificar_permissao_empresa(usuario_cpf, cnpj_empresa):
            return jsonify({"erro": "Sem permissão para acessar dados desta empresa"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def requer_permissao_grupo(f: Callable) -> Callable:
    """Decorator para verificar permissão de grupo"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        grupo_id = kwargs.get('grupo_id') or (request.json.get('grupo_id') if request.json else None)
        if grupo_id and not verificar_permissao_grupo(usuario_cpf, grupo_id):
            return jsonify({"erro": "Sem permissão para acessar dados deste grupo"}), 403
        
        return f(*args, **kwargs)
    return decorated_function
