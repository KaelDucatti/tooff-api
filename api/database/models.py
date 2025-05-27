from typing import List, Optional
from pathlib import Path
from datetime import datetime, timedelta, date
from enum import Enum as PyEnum

from sqlalchemy import create_engine, String, Boolean, Integer, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped, Session, relationship
from werkzeug.security import generate_password_hash, check_password_hash

# Variável global para a engine
engine = None

class Base(DeclarativeBase):
    pass

class TipoUsuario(PyEnum):
    RH = "rh"
    GESTOR = "gestor"
    COMUM = "comum"

class StatusEvento(PyEnum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"

class TipoAusencia(PyEnum):
    FERIAS = "Férias"
    ASSIDUIDADE = "Assiduidade"
    PLANTAO = "Plantão"
    LICENCA_MATERNIDADE = "Licença Maternidade/Paternidade"
    EVENTO_ESPECIAL = "Evento Especial"
    LICENCA_GERAL = "Licença (Geral)"

class Turno(PyEnum):
    DIA = "Dia"
    NOITE = "Noite"
    MADRUGADA = "Madrugada"

class Empresa(Base):
    __tablename__ = "empresas"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    cnpj: Mapped[Optional[str]] = mapped_column(String(18), unique=True)
    endereco: Mapped[Optional[str]] = mapped_column(Text)
    telefone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    grupos: Mapped[List["Grupo"]] = relationship("Grupo", back_populates="empresa", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Empresa({self.id!r}, {self.nome!r})"

class Grupo(Base):
    __tablename__ = "grupos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    empresa: Mapped["Empresa"] = relationship("Empresa", back_populates="grupos")
    usuarios: Mapped[List["Usuario"]] = relationship("Usuario", back_populates="grupo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Grupo({self.id!r}, {self.nome!r})"

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_usuario: Mapped[TipoUsuario] = mapped_column(Enum(TipoUsuario), default=TipoUsuario.COMUM)
    grupo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("grupos.id"))
    inicio_na_empresa: Mapped[date] = mapped_column()
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos com foreign_keys especificadas
    grupo: Mapped[Optional["Grupo"]] = relationship("Grupo", back_populates="usuarios")
    eventos: Mapped[List["Evento"]] = relationship(
        "Evento", 
        back_populates="usuario", 
        foreign_keys="Evento.usuario_id",
        cascade="all, delete-orphan"
    )
    eventos_aprovados: Mapped[List["Evento"]] = relationship(
        "Evento", 
        foreign_keys="Evento.aprovado_por_id",
        back_populates="aprovado_por"
    )
    
    def __repr__(self):
        return f"Usuario({self.id!r}, {self.email!r}, {self.tipo_usuario!r})"
    
    def set_senha(self, senha: str):
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)
    
    def pode_gerenciar_grupo(self, grupo_id: int) -> bool:
        """Verifica se o usuário pode gerenciar um grupo específico"""
        if self.tipo_usuario == TipoUsuario.RH:
            return True
        if self.tipo_usuario == TipoUsuario.GESTOR:
            return self.grupo_id == grupo_id
        return False
    
    def pode_aprovar_eventos(self, grupo_id: int) -> bool:
        """Verifica se o usuário pode aprovar eventos de um grupo"""
        if self.tipo_usuario == TipoUsuario.RH:
            return True
        if self.tipo_usuario == TipoUsuario.GESTOR:
            return self.grupo_id == grupo_id
        return False
    
    def ferias_tiradas_ano_atual(self) -> int:
        """Calcula dias de férias tiradas no ano atual"""
        ano_atual = datetime.now().year
        dias = 0
        for evento in self.eventos:
            if (evento.tipo_ausencia == TipoAusencia.FERIAS and 
                evento.status == StatusEvento.APROVADO and
                evento.data_inicio.year == ano_atual):
                dias += evento.total_dias
        return dias

class Evento(Base):
    __tablename__ = "eventos"
    
    TIPO_AUSENCIA_CORES = {
        TipoAusencia.FERIAS: "red",
        TipoAusencia.ASSIDUIDADE: "grey",
        TipoAusencia.PLANTAO: "orange",
        TipoAusencia.LICENCA_MATERNIDADE: "purple",
        TipoAusencia.EVENTO_ESPECIAL: "darkblue",
        TipoAusencia.LICENCA_GERAL: "brown"
    }
    
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data_inicio: Mapped[date] = mapped_column(nullable=False)
    data_fim: Mapped[date] = mapped_column(nullable=False)
    total_dias: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_ausencia: Mapped[TipoAusencia] = mapped_column(Enum(TipoAusencia), nullable=False)
    turno: Mapped[Optional[Turno]] = mapped_column(Enum(Turno))
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[StatusEvento] = mapped_column(Enum(StatusEvento), default=StatusEvento.PENDENTE)
    aprovado_por_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id"))
    data_aprovacao: Mapped[Optional[datetime]] = mapped_column(DateTime)
    observacoes_aprovacao: Mapped[Optional[str]] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos com foreign_keys especificadas
    usuario: Mapped["Usuario"] = relationship(
        "Usuario", 
        back_populates="eventos", 
        foreign_keys=[usuario_id]
    )
    aprovado_por: Mapped[Optional["Usuario"]] = relationship(
        "Usuario", 
        back_populates="eventos_aprovados",
        foreign_keys=[aprovado_por_id]
    )
    
    def __repr__(self):
        return f"Evento({self.id!r}, {self.tipo_ausencia!r}, {self.status!r})"
    
    def to_calendar_dict(self) -> dict:
        """Converte evento para formato do calendário"""
        return {
            "id": self.id,
            "title": f"{self.tipo_ausencia.value} - {self.usuario.nome}",
            "start": self.data_inicio.isoformat(),
            "end": (self.data_fim + timedelta(days=1)).isoformat(),
            "color": self.TIPO_AUSENCIA_CORES.get(self.tipo_ausencia, "grey"),
            "extendedProps": {
                "description": self.descricao,
                "shift": self.turno.value if self.turno else None,
                "status": self.status.value,
                "usuario_id": self.usuario_id,
                "usuario_nome": self.usuario.nome,
                "total_dias": self.total_dias
            }
        }

def init_db(database_url: str):
    """Inicializa o banco de dados"""
    global engine
    
    # Cria diretório do banco se necessário
    if database_url.startswith('sqlite:///'):
        db_path = Path(database_url.replace('sqlite:///', ''))
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    
    print(f"Banco de dados inicializado: {database_url}")

def get_session() -> Session:
    """Retorna uma nova sessão do banco de dados"""
    return Session(bind=engine)
