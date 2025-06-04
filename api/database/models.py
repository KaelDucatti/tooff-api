from typing import List, Optional
from datetime import datetime, date
from enum import Enum as PyEnum

from sqlalchemy import create_engine, String, Boolean, Integer, ForeignKey, DateTime, Text, Date, BigInteger, CHAR, text
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped, Session, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import os

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

class FlagGestor(PyEnum):
    SIM = "S"
    NAO = "N"

# ==================== NOVA ESTRUTURA DE TABELAS ====================

class UF(Base):
    __tablename__ = "uf"
    
    cod_uf: Mapped[int] = mapped_column(Integer, nullable=False)
    uf: Mapped[str] = mapped_column(CHAR(2), primary_key=True, nullable=False)
    
    # Relacionamentos
    usuarios: Mapped[List["Usuario"]] = relationship("Usuario", back_populates="estado")
    eventos: Mapped[List["Evento"]] = relationship("Evento", back_populates="estado")
    feriados_nacionais: Mapped[List["FeriadoNacional"]] = relationship("FeriadoNacional", back_populates="estado")
    feriados_estaduais: Mapped[List["FeriadoEstadual"]] = relationship("FeriadoEstadual", back_populates="estado")
    
    def __repr__(self):
        return f"UF({self.uf!r}, {self.cod_uf!r})"

class Empresa(Base):
    __tablename__ = "empresa"
    
    cnpj: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relacionamentos
    grupos: Mapped[List["Grupo"]] = relationship("Grupo", back_populates="empresa", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Empresa({self.cnpj!r}, {self.nome!r})"

class Grupo(Base):
    __tablename__ = "grupo"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    cnpj_empresa: Mapped[int] = mapped_column(BigInteger, ForeignKey("empresa.cnpj"), nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relacionamentos
    empresa: Mapped["Empresa"] = relationship("Empresa", back_populates="grupos")
    usuarios: Mapped[List["Usuario"]] = relationship("Usuario", back_populates="grupo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Grupo({self.id!r}, {self.nome!r})"

class TipoAusencia(Base):
    __tablename__ = "tipo_ausencia"
    
    id_tipo_ausencia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    descricao_ausencia: Mapped[str] = mapped_column(String(50), nullable=False)
    usa_turno: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Relacionamentos
    eventos: Mapped[List["Evento"]] = relationship("Evento", back_populates="tipo_ausencia")
    turnos: Mapped[List["Turno"]] = relationship("Turno", secondary="ausencia_turno", back_populates="tipos_ausencia")
    
    def __repr__(self):
        return f"TipoAusencia({self.id_tipo_ausencia!r}, {self.descricao_ausencia!r})"

class Turno(Base):
    __tablename__ = "turno"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    descricao_ausencia: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Relacionamentos
    tipos_ausencia: Mapped[List["TipoAusencia"]] = relationship("TipoAusencia", secondary="ausencia_turno", back_populates="turnos")
    
    def __repr__(self):
        return f"Turno({self.id!r}, {self.descricao_ausencia!r})"

class AusenciaTurno(Base):
    __tablename__ = "ausencia_turno"
    
    id_tipo_ausencia: Mapped[int] = mapped_column(Integer, ForeignKey("tipo_ausencia.id_tipo_ausencia"), primary_key=True, nullable=False)
    id_turno: Mapped[int] = mapped_column(Integer, ForeignKey("turno.id"), primary_key=True, nullable=False)

class Usuario(Base):
    __tablename__ = "usuario"
    
    cpf: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(515), nullable=False, unique=True)
    tipo_usuario: Mapped[str] = mapped_column(String(10), nullable=False, default="")
    grupo_id: Mapped[int] = mapped_column(Integer, ForeignKey("grupo.id"), nullable=False)
    inicio_na_empresa: Mapped[date] = mapped_column(Date, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    UF: Mapped[str] = mapped_column(CHAR(2), ForeignKey("uf.uf"), nullable=False)
    flag_gestor: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    
    # Relacionamentos
    grupo: Mapped["Grupo"] = relationship("Grupo", back_populates="usuarios")
    estado: Mapped["UF"] = relationship("UF", back_populates="usuarios")
    eventos: Mapped[List["Evento"]] = relationship(
        "Evento", 
        back_populates="usuario", 
        foreign_keys="Evento.cpf_usuario",
        cascade="all, delete-orphan"
    )
    eventos_aprovados: Mapped[List["Evento"]] = relationship(
        "Evento", 
        foreign_keys="Evento.aprovado_por",
        back_populates="aprovador"
    )
    
    def __repr__(self):
        return f"Usuario({self.cpf!r}, {self.email!r}, {self.tipo_usuario!r})"
    
    def set_senha(self, senha: str):
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)
    
    def pode_gerenciar_grupo(self, grupo_id: int) -> bool:
        """Verifica se o usuário pode gerenciar um grupo específico"""
        if self.tipo_usuario == "rh":
            return True
        if self.flag_gestor == "S":
            return self.grupo_id == grupo_id
        return False
    
    def pode_aprovar_eventos(self, grupo_id: int) -> bool:
        """Verifica se o usuário pode aprovar eventos de um grupo"""
        if self.tipo_usuario == "rh":
            return True
        if self.flag_gestor == "S":
            return self.grupo_id == grupo_id
        return False

class Evento(Base):
    __tablename__ = "evento"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    cpf_usuario: Mapped[int] = mapped_column(BigInteger, ForeignKey("usuario.cpf"), nullable=False)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    total_dias: Mapped[int] = mapped_column(Integer, nullable=False)
    id_tipo_ausencia: Mapped[int] = mapped_column(Integer, ForeignKey("tipo_ausencia.id_tipo_ausencia"), nullable=False)
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="pendente")
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    UF: Mapped[str] = mapped_column(CHAR(2), ForeignKey("uf.uf"), nullable=False)
    aprovado_por: Mapped[int] = mapped_column(BigInteger, ForeignKey("usuario.cpf"), nullable=False)
    
    # Relacionamentos
    usuario: Mapped["Usuario"] = relationship(
        "Usuario", 
        back_populates="eventos", 
        foreign_keys=[cpf_usuario]
    )
    aprovador: Mapped["Usuario"] = relationship(
        "Usuario", 
        back_populates="eventos_aprovados",
        foreign_keys=[aprovado_por]
    )
    tipo_ausencia: Mapped["TipoAusencia"] = relationship("TipoAusencia", back_populates="eventos")
    estado: Mapped["UF"] = relationship("UF", back_populates="eventos")
    
    def __repr__(self):
        return f"Evento({self.id!r}, {self.status!r})"

class FeriadoNacional(Base):
    __tablename__ = "feriados_nacionais"
    
    data_feriado: Mapped[date] = mapped_column(Date, primary_key=True, nullable=False)
    uf: Mapped[str] = mapped_column(CHAR(2), ForeignKey("uf.uf"), primary_key=True, nullable=False)
    descricao_feriado: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relacionamentos
    estado: Mapped["UF"] = relationship("UF", back_populates="feriados_nacionais")
    
    def __repr__(self):
        return f"FeriadoNacional({self.data_feriado!r}, {self.uf!r})"

class FeriadoEstadual(Base):
    __tablename__ = "feriados_estaduais"
    
    data_feriado: Mapped[date] = mapped_column(Date, primary_key=True, nullable=False)
    uf: Mapped[str] = mapped_column(CHAR(2), ForeignKey("uf.uf"), primary_key=True, nullable=False)
    descricao_feriado: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relacionamentos
    estado: Mapped["UF"] = relationship("UF", back_populates="feriados_estaduais")
    
    def __repr__(self):
        return f"FeriadoEstadual({self.data_feriado!r}, {self.uf!r})"

def init_db(database_url: Optional[str] = None):
    """Inicializa o banco de dados com fallback para SQLite"""
    global engine
    
    # Se não foi fornecida URL, usa SQLite local
    if not database_url:
        database_url = "sqlite:///database/tooff_app.db"
        print("⚠️  Usando SQLite local como fallback")
    
    try:
        if database_url.startswith("mysql"):
            # Configurações específicas para MySQL
            engine = create_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "charset": "utf8mb4",
                    "autocommit": False,
                    "connect_timeout": 10,  # Timeout de 10 segundos
                }
            )
            
            # Testa a conexão MySQL
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ Conexão com MySQL estabelecida com sucesso!")
        else:
            # Configurações para SQLite
            os.makedirs("database", exist_ok=True)
            engine = create_engine(
                database_url,
                echo=False,
                connect_args={"check_same_thread": False}
            )
            
            # Testa a conexão SQLite
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ Conexão com SQLite estabelecida com sucesso!")
        
        # Cria as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/verificadas!")
        
    except Exception as e:
        print(f"❌ Erro ao conectar com {database_url.split('://')[0].upper()}: {e}")
        
        # Fallback para SQLite se MySQL falhar
        if database_url.startswith("mysql"):
            print("🔄 Tentando fallback para SQLite local...")
            return init_db("sqlite:///database/tooff_app.db")
        else:
            raise

def get_session() -> Session:
    """Retorna uma nova sessão do banco de dados"""
    return Session(bind=engine)
