from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func

from .models import (
    get_session, Usuario, Empresa, Grupo, Evento, 
    TipoUsuario, StatusEvento, TipoAusencia, Turno
)

# ==================== EMPRESAS ====================

def criar_empresa(nome: str, cnpj: Optional[str] = None, **kwargs) -> Empresa:
    with get_session() as session:
        empresa = Empresa(nome=nome, cnpj=cnpj, **kwargs)
        session.add(empresa)
        session.commit()
        session.refresh(empresa)
        return empresa

def listar_empresas(ativas_apenas: bool = True) -> List[Empresa]:
    with get_session() as session:
        query = select(Empresa)
        if ativas_apenas:
            query = query.where(Empresa.ativa)
        return list(session.execute(query).scalars().all())

def obter_empresa(empresa_id: int) -> Optional[Empresa]:
    with get_session() as session:
        return session.get(Empresa, empresa_id)

def atualizar_empresa(empresa_id: int, **kwargs) -> bool:
    with get_session() as session:
        empresa = session.get(Empresa, empresa_id)
        if not empresa:
            return False
        for key, value in kwargs.items():
            setattr(empresa, key, value)
        session.commit()
        return True

def deletar_empresa(empresa_id: int) -> bool:
    with get_session() as session:
        empresa = session.get(Empresa, empresa_id)
        if not empresa:
            return False
        empresa.ativa = False
        session.commit()
        return True

# ==================== GRUPOS ====================

def criar_grupo(nome: str, empresa_id: int, descricao: Optional[str] = None, **kwargs) -> Grupo:
    with get_session() as session:
        grupo = Grupo(nome=nome, empresa_id=empresa_id, descricao=descricao, **kwargs)
        session.add(grupo)
        session.commit()
        session.refresh(grupo)
        return grupo

def listar_grupos(empresa_id: Optional[int] = None, ativos_apenas: bool = True) -> List[Grupo]:
    with get_session() as session:
        query = select(Grupo)
        if empresa_id:
            query = query.where(Grupo.empresa_id == empresa_id)
        if ativos_apenas:
            query = query.where(Grupo.ativo)
        return list(session.execute(query).scalars().all())

def obter_grupo(grupo_id: int) -> Optional[Grupo]:
    with get_session() as session:
        return session.get(Grupo, grupo_id)

def atualizar_grupo(grupo_id: int, **kwargs) -> bool:
    with get_session() as session:
        grupo = session.get(Grupo, grupo_id)
        if not grupo:
            return False
        for key, value in kwargs.items():
            setattr(grupo, key, value)
        session.commit()
        return True

def deletar_grupo(grupo_id: int) -> bool:
    with get_session() as session:
        grupo = session.get(Grupo, grupo_id)
        if not grupo:
            return False
        grupo.ativo = False
        session.commit()
        return True

# ==================== USUÁRIOS ====================

def criar_usuario(nome: str, email: str, senha: str, inicio_na_empresa: str, 
                 tipo_usuario: TipoUsuario = TipoUsuario.COMUM, 
                 grupo_id: Optional[int] = None, **kwargs) -> Usuario:
    with get_session() as session:
        # Converte string para date se necessário
        data_inicio = datetime.strptime(inicio_na_empresa, "%Y-%m-%d").date()
        
        usuario = Usuario(
            nome=nome,
            email=email.strip().lower(),
            tipo_usuario=tipo_usuario,
            grupo_id=grupo_id,
            inicio_na_empresa=data_inicio,
            **kwargs
        )
        usuario.set_senha(senha)
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario

def autenticar_usuario(email: str, senha: str) -> Optional[Usuario]:
    with get_session() as session:
        usuario = session.execute(
            select(Usuario).where(
                and_(Usuario.email == email.strip().lower(), Usuario.ativo)
            )
        ).scalar_one_or_none()
        
        if usuario and usuario.verificar_senha(senha):
            return usuario
        return None

def listar_usuarios(grupo_id: Optional[int] = None, tipo_usuario: Optional[TipoUsuario] = None,
                   ativos_apenas: bool = True) -> List[Usuario]:
    with get_session() as session:
        query = select(Usuario)
        
        conditions = []
        if grupo_id:
            conditions.append(Usuario.grupo_id == grupo_id)
        if tipo_usuario:
            conditions.append(Usuario.tipo_usuario == tipo_usuario)
        if ativos_apenas:
            conditions.append(Usuario.ativo)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return list(session.execute(query).scalars().all())

def obter_usuario(usuario_id: int) -> Optional[Usuario]:
    with get_session() as session:
        return session.get(Usuario, usuario_id)

def atualizar_usuario(usuario_id: int, **kwargs) -> bool:
    with get_session() as session:
        usuario = session.get(Usuario, usuario_id)
        if not usuario:
            return False
        
        for key, value in kwargs.items():
            if key == "senha":
                usuario.set_senha(value)
            elif key == "inicio_na_empresa" and isinstance(value, str):
                setattr(usuario, key, datetime.strptime(value, "%Y-%m-%d").date())
            else:
                setattr(usuario, key, value)
        
        session.commit()
        return True

def deletar_usuario(usuario_id: int) -> bool:
    with get_session() as session:
        usuario = session.get(Usuario, usuario_id)
        if not usuario:
            return False
        usuario.ativo = False
        session.commit()
        return True

# ==================== EVENTOS ====================

def criar_evento(usuario_id: int, data_inicio: str, data_fim: str, 
                tipo_ausencia: TipoAusencia, turno: Optional[Turno] = None,
                descricao: Optional[str] = None) -> Evento:
    with get_session() as session:
        # Converte strings para date
        inicio_date = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        fim_date = datetime.strptime(data_fim, "%Y-%m-%d").date()
        
        total_dias = (fim_date - inicio_date).days + 1
        
        evento = Evento(
            usuario_id=usuario_id,
            data_inicio=inicio_date,
            data_fim=fim_date,
            total_dias=total_dias,
            tipo_ausencia=tipo_ausencia,
            turno=turno,
            descricao=descricao
        )
        session.add(evento)
        session.commit()
        session.refresh(evento)
        return evento

def listar_eventos(usuario_id: Optional[int] = None, grupo_id: Optional[int] = None,
                  status: Optional[StatusEvento] = None) -> List[Evento]:
    with get_session() as session:
        query = select(Evento).join(Usuario, Evento.usuario_id == Usuario.id)
        
        conditions = []
        if usuario_id:
            conditions.append(Evento.usuario_id == usuario_id)
        if grupo_id:
            conditions.append(Usuario.grupo_id == grupo_id)
        if status:
            conditions.append(Evento.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return list(session.execute(query).scalars().all())

def obter_evento(evento_id: int) -> Optional[Evento]:
    with get_session() as session:
        return session.get(Evento, evento_id)

def atualizar_evento(evento_id: int, **kwargs) -> bool:
    with get_session() as session:
        evento = session.get(Evento, evento_id)
        if not evento:
            return False
        
        for key, value in kwargs.items():
            if key in ["data_inicio", "data_fim"] and isinstance(value, str):
                setattr(evento, key, datetime.strptime(value, "%Y-%m-%d").date())
            else:
                setattr(evento, key, value)
        
        # Recalcula total de dias se as datas mudaram
        if "data_inicio" in kwargs or "data_fim" in kwargs:
            evento.total_dias = (evento.data_fim - evento.data_inicio).days + 1
        
        session.commit()
        return True

def deletar_evento(evento_id: int) -> bool:
    with get_session() as session:
        evento = session.get(Evento, evento_id)
        if not evento:
            return False
        session.delete(evento)
        session.commit()
        return True

def aprovar_evento(evento_id: int, aprovador_id: int, observacoes: Optional[str] = None) -> bool:
    with get_session() as session:
        evento = session.get(Evento, evento_id)
        if not evento:
            return False
        
        evento.status = StatusEvento.APROVADO
        evento.aprovado_por_id = aprovador_id
        evento.data_aprovacao = datetime.utcnow()
        evento.observacoes_aprovacao = observacoes
        
        session.commit()
        return True

def rejeitar_evento(evento_id: int, aprovador_id: int, observacoes: Optional[str] = None) -> bool:
    with get_session() as session:
        evento = session.get(Evento, evento_id)
        if not evento:
            return False
        
        evento.status = StatusEvento.REJEITADO
        evento.aprovado_por_id = aprovador_id
        evento.data_aprovacao = datetime.utcnow()
        evento.observacoes_aprovacao = observacoes
        
        session.commit()
        return True

# ==================== UTILITÁRIOS ====================

def eventos_para_calendario(grupo_id: Optional[int] = None, apenas_aprovados: bool = True) -> List[Dict]:
    """Retorna eventos formatados para calendário"""
    with get_session() as session:
        # Join explícito especificando a condição
        query = select(Evento, Usuario).join(Usuario, Evento.usuario_id == Usuario.id)
        
        conditions = []
        if grupo_id:
            conditions.append(Usuario.grupo_id == grupo_id)
        if apenas_aprovados:
            conditions.append(Evento.status == StatusEvento.APROVADO)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        results = session.execute(query).all()
        
        calendario = []
        for evento, usuario in results:
            calendario.append({
                "id": evento.id,
                "title": f"{evento.tipo_ausencia.value} - {usuario.nome}",
                "start": evento.data_inicio.isoformat(),
                "end": (evento.data_fim + timedelta(days=1)).isoformat(),
                "color": evento.TIPO_AUSENCIA_CORES.get(evento.tipo_ausencia, "grey"),
                "extendedProps": {
                    "description": evento.descricao,
                    "shift": evento.turno.value if evento.turno else None,
                    "status": evento.status.value,
                    "usuario_id": evento.usuario_id,
                    "usuario_nome": usuario.nome,
                    "total_dias": evento.total_dias
                }
            })
        
        return calendario

def estatisticas_grupo(grupo_id: int) -> Dict[str, Any]:
    """Retorna estatísticas de um grupo"""
    with get_session() as session:
        grupo = session.get(Grupo, grupo_id)
        if not grupo:
            return {}
        
        # Conta usuários do grupo
        total_usuarios = session.execute(
            select(func.count(Usuario.id)).where(Usuario.grupo_id == grupo_id)
        ).scalar()
        
        usuarios_ativos = session.execute(
            select(func.count(Usuario.id)).where(
                and_(Usuario.grupo_id == grupo_id, Usuario.ativo)
            )
        ).scalar()
        
        # Conta eventos pendentes - join explícito
        eventos_pendentes = session.execute(
            select(func.count(Evento.id))
            .join(Usuario, Evento.usuario_id == Usuario.id)
            .where(
                and_(
                    Usuario.grupo_id == grupo_id,
                    Evento.status == StatusEvento.PENDENTE
                )
            )
        ).scalar()
        
        # Conta eventos aprovados - join explícito
        eventos_aprovados = session.execute(
            select(func.count(Evento.id))
            .join(Usuario, Evento.usuario_id == Usuario.id)
            .where(
                and_(
                    Usuario.grupo_id == grupo_id,
                    Evento.status == StatusEvento.APROVADO
                )
            )
        ).scalar()
        
        return {
            "grupo": grupo.nome,
            "total_usuarios": total_usuarios,
            "eventos_pendentes": eventos_pendentes,
            "eventos_aprovados": eventos_aprovados,
            "usuarios_ativos": usuarios_ativos
        }

# ==================== CONVERSORES ====================

def empresa_para_dict(empresa: Empresa) -> Dict[str, Any]:
    with get_session() as session:
        # Conta grupos da empresa
        total_grupos = session.execute(
            select(func.count(Grupo.id)).where(Grupo.empresa_id == empresa.id)
        ).scalar()
        
        return {
            "id": empresa.id,
            "nome": empresa.nome,
            "cnpj": empresa.cnpj,
            "endereco": empresa.endereco,
            "telefone": empresa.telefone,
            "email": empresa.email,
            "ativa": empresa.ativa,
            "criado_em": empresa.criado_em.isoformat(),
            "total_grupos": total_grupos
        }

def grupo_para_dict(grupo: Grupo) -> Dict[str, Any]:
    with get_session() as session:
        # Busca nome da empresa
        empresa = session.get(Empresa, grupo.empresa_id)
        empresa_nome = empresa.nome if empresa else "N/A"
        
        # Conta usuários do grupo
        total_usuarios = session.execute(
            select(func.count(Usuario.id)).where(Usuario.grupo_id == grupo.id)
        ).scalar()
        
        return {
            "id": grupo.id,
            "nome": grupo.nome,
            "descricao": grupo.descricao,
            "empresa_id": grupo.empresa_id,
            "empresa_nome": empresa_nome,
            "ativo": grupo.ativo,
            "criado_em": grupo.criado_em.isoformat(),
            "total_usuarios": total_usuarios
        }

def usuario_para_dict(usuario: Usuario) -> Dict[str, Any]:
    with get_session() as session:
        # Busca nome do grupo se existir
        grupo_nome = None
        if usuario.grupo_id:
            grupo = session.get(Grupo, usuario.grupo_id)
            grupo_nome = grupo.nome if grupo else None
        
        # Calcula férias tiradas no ano atual
        ano_atual = datetime.now().year
        ferias_tiradas = session.execute(
            select(func.sum(Evento.total_dias))
            .where(
                and_(
                    Evento.usuario_id == usuario.id,
                    Evento.tipo_ausencia == TipoAusencia.FERIAS,
                    Evento.status == StatusEvento.APROVADO,
                    func.strftime('%Y', Evento.data_inicio) == str(ano_atual)
                )
            )
        ).scalar() or 0
        
        return {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo_usuario": usuario.tipo_usuario.value,
            "grupo_id": usuario.grupo_id,
            "grupo_nome": grupo_nome,
            "inicio_na_empresa": usuario.inicio_na_empresa.isoformat(),
            "ativo": usuario.ativo,
            "criado_em": usuario.criado_em.isoformat(),
            "ferias_tiradas": ferias_tiradas
        }

def evento_para_dict(evento: Evento) -> Dict[str, Any]:
    with get_session() as session:
        # Busca nome do usuário
        usuario = session.get(Usuario, evento.usuario_id)
        usuario_nome = usuario.nome if usuario else "N/A"
        
        # Busca nome do aprovador se existir
        aprovado_por_nome = None
        if evento.aprovado_por_id:
            aprovador = session.get(Usuario, evento.aprovado_por_id)
            aprovado_por_nome = aprovador.nome if aprovador else None
        
        return {
            "id": evento.id,
            "usuario_id": evento.usuario_id,
            "usuario_nome": usuario_nome,
            "data_inicio": evento.data_inicio.isoformat(),
            "data_fim": evento.data_fim.isoformat(),
            "total_dias": evento.total_dias,
            "tipo_ausencia": evento.tipo_ausencia.value,
            "turno": evento.turno.value if evento.turno else None,
            "descricao": evento.descricao,
            "status": evento.status.value,
            "aprovado_por_id": evento.aprovado_por_id,
            "aprovado_por_nome": aprovado_por_nome,
            "data_aprovacao": evento.data_aprovacao.isoformat() if evento.data_aprovacao else None,
            "observacoes_aprovacao": evento.observacoes_aprovacao,
            "criado_em": evento.criado_em.isoformat()
        }
