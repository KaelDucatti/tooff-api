from functools import wraps
from flask import request, jsonify
from typing import Callable, Any, Dict, Optional, Union
import sys
import os

# Adiciona o diretório pai ao path para permitir imports relativos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database.crud import obter_usuario, obter_grupo, obter_evento
from api.database.models import TipoUsuario

def extrair_usuario_id_do_token() -> Optional[int]:
    """
    TODO: Implementar extração do user_id do JWT token
    Por enquanto, vamos simular com um header customizado
    """
    return request.headers.get('X-User-ID', type=int)

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
