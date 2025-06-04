"""
Verificador de integridade de dados CPF/CNPJ
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func
from datetime import datetime

from ..database.models import get_session, Usuario, Empresa, Grupo, Evento, UF
from .cpf_cnpj_validator import validar_cpf, validar_cnpj, formatar_cpf, formatar_cnpj

class IntegrityReport:
    """Classe para armazenar relatório de integridade"""
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.info: List[Dict[str, Any]] = []
        self.statistics: Dict[str, Any] = {}
        self.timestamp = datetime.now()
    
    def add_error(self, category: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Adiciona um erro ao relatório"""
        self.errors.append({
            "category": category,
            "message": message,
            "details": details if details is not None else {},
            "severity": "ERROR"
        })
    
    def add_warning(self, category: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Adiciona um aviso ao relatório"""
        self.warnings.append({
            "category": category,
            "message": message,
            "details": details if details is not None else {},
            "severity": "WARNING"
        })
    
    def add_info(self, category: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Adiciona uma informação ao relatório"""
        self.info.append({
            "category": category,
            "message": message,
            "details": details if details is not None else {},
            "severity": "INFO"
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo do relatório"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "total_info": len(self.info),
            "statistics": self.statistics
        }

class CPFCNPJIntegrityChecker:
    """Verificador de integridade para CPF e CNPJ"""
    
    def __init__(self):
        self.report = IntegrityReport()
    
    def check_cpf_format_validity(self) -> None:
        """Verifica se todos os CPFs no banco são válidos"""
        with get_session() as session:
            usuarios = session.execute(select(Usuario)).scalars().all()
            
            invalid_cpfs = []
            for usuario in usuarios:
                cpf_str = str(usuario.cpf).zfill(11)
                if not validar_cpf(cpf_str):
                    invalid_cpfs.append({
                        "cpf": usuario.cpf,
                        "cpf_formatado": formatar_cpf(usuario.cpf),
                        "nome": usuario.nome,
                        "email": usuario.email
                    })
            
            if invalid_cpfs:
                self.report.add_error(
                    "CPF_FORMAT",
                    f"Encontrados {len(invalid_cpfs)} CPFs inválidos",
                    {"invalid_cpfs": invalid_cpfs}
                )
            else:
                self.report.add_info(
                    "CPF_FORMAT",
                    "Todos os CPFs no banco são válidos"
                )
    
    def check_cnpj_format_validity(self) -> None:
        """Verifica se todos os CNPJs no banco são válidos"""
        with get_session() as session:
            empresas = session.execute(select(Empresa)).scalars().all()
            
            invalid_cnpjs = []
            for empresa in empresas:
                cnpj_str = str(empresa.cnpj).zfill(14)
                if not validar_cnpj(cnpj_str):
                    invalid_cnpjs.append({
                        "cnpj": empresa.cnpj,
                        "cnpj_formatado": formatar_cnpj(empresa.cnpj),
                        "nome": empresa.nome,
                        "email": empresa.email
                    })
            
            if invalid_cnpjs:
                self.report.add_error(
                    "CNPJ_FORMAT",
                    f"Encontrados {len(invalid_cnpjs)} CNPJs inválidos",
                    {"invalid_cnpjs": invalid_cnpjs}
                )
            else:
                self.report.add_info(
                    "CNPJ_FORMAT",
                    "Todos os CNPJs no banco são válidos"
                )
    
    def check_duplicate_cpfs(self) -> None:
        """Verifica CPFs duplicados"""
        with get_session() as session:
            duplicates = session.execute(
                select(Usuario.cpf, func.count(Usuario.cpf).label('count'))
                .group_by(Usuario.cpf)
                .having(func.count(Usuario.cpf) > 1)
            ).all()
            
            if duplicates:
                duplicate_details = []
                for cpf, count in duplicates:
                    usuarios = session.execute(
                        select(Usuario).where(Usuario.cpf == cpf)
                    ).scalars().all()
                    
                    duplicate_details.append({
                        "cpf": cpf,
                        "cpf_formatado": formatar_cpf(cpf),
                        "count": count,
                        "usuarios": [
                            {"nome": u.nome, "email": u.email, "ativo": u.ativo}
                            for u in usuarios
                        ]
                    })
                
                self.report.add_error(
                    "CPF_DUPLICATE",
                    f"Encontrados {len(duplicates)} CPFs duplicados",
                    {"duplicates": duplicate_details}
                )
            else:
                self.report.add_info(
                    "CPF_DUPLICATE",
                    "Nenhum CPF duplicado encontrado"
                )
    
    def check_duplicate_cnpjs(self) -> None:
        """Verifica CNPJs duplicados"""
        with get_session() as session:
            duplicates = session.execute(
                select(Empresa.cnpj, func.count(Empresa.cnpj).label('count'))
                .group_by(Empresa.cnpj)
                .having(func.count(Empresa.cnpj) > 1)
            ).all()
            
            if duplicates:
                duplicate_details = []
                for cnpj, count in duplicates:
                    empresas = session.execute(
                        select(Empresa).where(Empresa.cnpj == cnpj)
                    ).scalars().all()
                    
                    duplicate_details.append({
                        "cnpj": cnpj,
                        "cnpj_formatado": formatar_cnpj(cnpj),
                        "count": count,
                        "empresas": [
                            {"nome": e.nome, "email": e.email, "ativa": e.ativa}
                            for e in empresas
                        ]
                    })
                
                self.report.add_error(
                    "CNPJ_DUPLICATE",
                    f"Encontrados {len(duplicates)} CNPJs duplicados",
                    {"duplicates": duplicate_details}
                )
            else:
                self.report.add_info(
                    "CNPJ_DUPLICATE",
                    "Nenhum CNPJ duplicado encontrado"
                )
    
    def check_orphaned_usuarios(self) -> None:
        """Verifica usuários órfãos (sem grupo válido)"""
        with get_session() as session:
            orphaned = session.execute(
                select(Usuario)
                .outerjoin(Grupo, Usuario.grupo_id == Grupo.id)
                .where(Grupo.id.is_(None))
            ).scalars().all()
            
            if orphaned:
                orphaned_details = [
                    {
                        "cpf": u.cpf,
                        "cpf_formatado": formatar_cpf(u.cpf),
                        "nome": u.nome,
                        "email": u.email,
                        "grupo_id": u.grupo_id,
                        "ativo": u.ativo
                    }
                    for u in orphaned
                ]
                
                self.report.add_error(
                    "ORPHANED_USUARIOS",
                    f"Encontrados {len(orphaned)} usuários órfãos",
                    {"orphaned_usuarios": orphaned_details}
                )
            else:
                self.report.add_info(
                    "ORPHANED_USUARIOS",
                    "Nenhum usuário órfão encontrado"
                )
    
    def check_orphaned_grupos(self) -> None:
        """Verifica grupos órfãos (sem empresa válida)"""
        with get_session() as session:
            orphaned = session.execute(
                select(Grupo)
                .outerjoin(Empresa, Grupo.cnpj_empresa == Empresa.cnpj)
                .where(Empresa.cnpj.is_(None))
            ).scalars().all()
            
            if orphaned:
                orphaned_details = [
                    {
                        "id": g.id,
                        "nome": g.nome,
                        "cnpj_empresa": g.cnpj_empresa,
                        "cnpj_formatado": formatar_cnpj(g.cnpj_empresa),
                        "ativo": g.ativo
                    }
                    for g in orphaned
                ]
                
                self.report.add_error(
                    "ORPHANED_GRUPOS",
                    f"Encontrados {len(orphaned)} grupos órfãos",
                    {"orphaned_grupos": orphaned_details}
                )
            else:
                self.report.add_info(
                    "ORPHANED_GRUPOS",
                    "Nenhum grupo órfão encontrado"
                )
    
    def check_orphaned_eventos(self) -> None:
        """Verifica eventos órfãos (sem usuário válido)"""
        with get_session() as session:
            orphaned = session.execute(
                select(Evento)
                .outerjoin(Usuario, Evento.cpf_usuario == Usuario.cpf)
                .where(Usuario.cpf.is_(None))
            ).scalars().all()
            
            if orphaned:
                orphaned_details = [
                    {
                        "id": e.id,
                        "cpf_usuario": e.cpf_usuario,
                        "cpf_formatado": formatar_cpf(e.cpf_usuario),
                        "data_inicio": e.data_inicio.isoformat(),
                        "data_fim": e.data_fim.isoformat(),
                        "status": e.status
                    }
                    for e in orphaned
                ]
                
                self.report.add_error(
                    "ORPHANED_EVENTOS",
                    f"Encontrados {len(orphaned)} eventos órfãos",
                    {"orphaned_eventos": orphaned_details}
                )
            else:
                self.report.add_info(
                    "ORPHANED_EVENTOS",
                    "Nenhum evento órfão encontrado"
                )
    
    def check_invalid_uf_references(self) -> None:
        """Verifica referências inválidas de UF"""
        with get_session() as session:
            # Usuários com UF inválida
            invalid_usuarios = session.execute(
                select(Usuario)
                .outerjoin(UF, Usuario.UF == UF.uf)
                .where(UF.uf.is_(None))
            ).scalars().all()
            
            # Eventos com UF inválida
            invalid_eventos = session.execute(
                select(Evento)
                .outerjoin(UF, Evento.UF == UF.uf)
                .where(UF.uf.is_(None))
            ).scalars().all()
            
            if invalid_usuarios:
                self.report.add_error(
                    "INVALID_UF_USUARIOS",
                    f"Encontrados {len(invalid_usuarios)} usuários com UF inválida",
                    {
                        "invalid_usuarios": [
                            {
                                "cpf": u.cpf,
                                "cpf_formatado": formatar_cpf(u.cpf),
                                "nome": u.nome,
                                "uf": u.UF
                            }
                            for u in invalid_usuarios
                        ]
                    }
                )
            
            if invalid_eventos:
                self.report.add_error(
                    "INVALID_UF_EVENTOS",
                    f"Encontrados {len(invalid_eventos)} eventos com UF inválida",
                    {
                        "invalid_eventos": [
                            {
                                "id": e.id,
                                "cpf_usuario": e.cpf_usuario,
                                "uf": e.UF
                            }
                            for e in invalid_eventos
                        ]
                    }
                )
    
    def check_inconsistent_aprovadores(self) -> None:
        """Verifica aprovadores inconsistentes em eventos"""
        with get_session() as session:
            inconsistent = session.execute(
                select(Evento)
                .outerjoin(Usuario, Evento.aprovado_por == Usuario.cpf)
                .where(Usuario.cpf.is_(None))
            ).scalars().all()
            
            if inconsistent:
                inconsistent_details = [
                    {
                        "evento_id": e.id,
                        "cpf_usuario": e.cpf_usuario,
                        "aprovado_por": e.aprovado_por,
                        "aprovado_por_formatado": formatar_cpf(e.aprovado_por),
                        "status": e.status
                    }
                    for e in inconsistent
                ]
                
                self.report.add_error(
                    "INCONSISTENT_APROVADORES",
                    f"Encontrados {len(inconsistent)} eventos com aprovadores inexistentes",
                    {"inconsistent_eventos": inconsistent_details}
                )
            else:
                self.report.add_info(
                    "INCONSISTENT_APROVADORES",
                    "Todos os aprovadores de eventos são válidos"
                )
    
    def generate_statistics(self) -> None:
        """Gera estatísticas gerais do banco"""
        with get_session() as session:
            stats = {}
            
            # Contagem de registros
            stats["total_empresas"] = session.execute(select(func.count(Empresa.cnpj))).scalar()
            stats["total_grupos"] = session.execute(select(func.count(Grupo.id))).scalar()
            stats["total_usuarios"] = session.execute(select(func.count(Usuario.cpf))).scalar()
            stats["total_eventos"] = session.execute(select(func.count(Evento.id))).scalar()
            stats["total_ufs"] = session.execute(select(func.count(UF.uf))).scalar()
            
            # Usuários por tipo
            tipos_usuario = session.execute(
                select(Usuario.tipo_usuario, func.count(Usuario.cpf))
                .group_by(Usuario.tipo_usuario)
            ).all()
            stats["usuarios_por_tipo"] = {tipo: count for tipo, count in tipos_usuario}
            
            # Eventos por status
            status_eventos = session.execute(
                select(Evento.status, func.count(Evento.id))
                .group_by(Evento.status)
            ).all()
            stats["eventos_por_status"] = {status: count for status, count in status_eventos}
            
            # Empresas ativas vs inativas
            empresas_ativas = session.execute(
                select(func.count(Empresa.cnpj)).where(Empresa.ativa)
            ).scalar() or 0
            total_empresas = stats["total_empresas"] or 0
            stats["empresas_ativas"] = empresas_ativas
            stats["empresas_inativas"] = total_empresas - empresas_ativas
            
            # Usuários ativos vs inativos
            usuarios_ativos = session.execute(
                select(func.count(Usuario.cpf)).where(Usuario.ativo)
            ).scalar() or 0
            total_usuarios = stats["total_usuarios"] or 0
            stats["usuarios_ativos"] = usuarios_ativos
            stats["usuarios_inativos"] = total_usuarios - usuarios_ativos
            
            self.report.statistics = stats
    
    def run_all_checks(self) -> IntegrityReport:
        """Executa todas as verificações de integridade"""
        print("🔍 Iniciando verificação de integridade CPF/CNPJ...")
        
        print("📋 Verificando formato de CPFs...")
        self.check_cpf_format_validity()
        
        print("📋 Verificando formato de CNPJs...")
        self.check_cnpj_format_validity()
        
        print("🔍 Verificando CPFs duplicados...")
        self.check_duplicate_cpfs()
        
        print("🔍 Verificando CNPJs duplicados...")
        self.check_duplicate_cnpjs()
        
        print("👤 Verificando usuários órfãos...")
        self.check_orphaned_usuarios()
        
        print("👥 Verificando grupos órfãos...")
        self.check_orphaned_grupos()
        
        print("📅 Verificando eventos órfãos...")
        self.check_orphaned_eventos()
        
        print("🌎 Verificando referências de UF...")
        self.check_invalid_uf_references()
        
        print("✅ Verificando aprovadores de eventos...")
        self.check_inconsistent_aprovadores()
        
        print("📊 Gerando estatísticas...")
        self.generate_statistics()
        
        print("✅ Verificação de integridade concluída!")
        return self.report
