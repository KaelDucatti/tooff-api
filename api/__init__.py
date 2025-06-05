"""
Pacote principal da API ToOff
"""

# Versão da API
__version__ = "1.0.0"

# Importações principais para facilitar o uso
from .database.models import (
    Base, 
    TipoUsuario, 
    StatusEvento, 
    FlagGestor,
    Usuario, 
    Empresa, 
    Grupo, 
    Evento,
    UF,
    TipoAusencia,
    Turno
)

from .database.crud import (
    criar_empresa,
    criar_grupo, 
    criar_usuario,
    criar_evento,
    obter_usuario,
    listar_usuarios,
    atualizar_usuario,
    deletar_usuario,
    autenticar_usuario,
    obter_empresa,
    obter_grupo,
    obter_evento,
    listar_empresas,
    listar_grupos,
    listar_eventos
)

__all__ = [
    # Enums
    "TipoUsuario",
    "StatusEvento", 
    "FlagGestor",
    
    # Models
    "Base",
    "Usuario",
    "Empresa", 
    "Grupo",
    "Evento",
    "UF",
    "TipoAusencia",
    "Turno",
    
    # CRUD Functions - Criar
    "criar_empresa",
    "criar_grupo",
    "criar_usuario", 
    "criar_evento",
    
    # CRUD Functions - Obter
    "obter_usuario",
    "obter_empresa",
    "obter_grupo",
    "obter_evento",
    
    # CRUD Functions - Listar
    "listar_usuarios",
    "listar_empresas",
    "listar_grupos",
    "listar_eventos",
    
    # CRUD Functions - Atualizar/Deletar
    "atualizar_usuario",
    "deletar_usuario",
    
    # Auth
    "autenticar_usuario"
]
