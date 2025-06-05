from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func, extract

from .models import (
    get_session, Usuario, Empresa, Grupo, Evento, UF,
    TipoAusencia, Turno, FeriadoNacional, FeriadoEstadual,
    TipoUsuario, StatusEvento, FlagGestor
)

# ==================== UF ====================

def criar_uf(cod_uf: int, uf: str) -> UF:
    with get_session() as session:
        estado = UF(cod_uf=cod_uf, uf=uf)
        session.add(estado)
        session.commit()
        session.refresh(estado)
        return estado

def listar_ufs() -> List[UF]:
    with get_session() as session:
        return list(session.execute(select(UF)).scalars().all())

def obter_uf(uf: str) -> Optional[UF]:
    with get_session() as session:
        return session.get(UF, uf)

# ==================== EMPRESAS ====================

def criar_empresa(cnpj: int, id_empresa: int, nome: str, endereco: str, 
                 telefone: str, email: str, **kwargs) -> Empresa:
    with get_session() as session:
        empresa = Empresa(
            cnpj=cnpj,
            id=id_empresa,
            nome=nome,
            endereco=endereco,
            telefone=telefone,
            email=email,
            criado_em=datetime.now().date(),
            **kwargs
        )
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

def obter_empresa(cnpj: int) -> Optional[Empresa]:
    with get_session() as session:
        return session.get(Empresa, cnpj)

def atualizar_empresa(cnpj: int, **kwargs) -> bool:
    with get_session() as session:
        empresa = session.get(Empresa, cnpj)
        if not empresa:
            return False
        for key, value in kwargs.items():
            setattr(empresa, key, value)
        session.commit()
        return True

def deletar_empresa(cnpj: int) -> bool:
    with get_session() as session:
        empresa = session.get(Empresa, cnpj)
        if not empresa:
            return False
        empresa.ativa = False
        session.commit()
        return True

# ==================== GRUPOS ====================

def criar_grupo(nome: str, cnpj_empresa: int, telefone: str, 
               descricao: Optional[str] = None, **kwargs) -> Grupo:
    with get_session() as session:
        grupo = Grupo(
            nome=nome,
            cnpj_empresa=cnpj_empresa,
            telefone=telefone,
            descricao=descricao,
            criado_em=datetime.now().date(),
            **kwargs
        )
        session.add(grupo)
        session.commit()
        session.refresh(grupo)
        return grupo

def listar_grupos(cnpj_empresa: Optional[int] = None, ativos_apenas: bool = True) -> List[Grupo]:
    with get_session() as session:
        query = select(Grupo)
        if cnpj_empresa:
            query = query.where(Grupo.cnpj_empresa == cnpj_empresa)
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

# ==================== TIPOS DE AUSÊNCIA ====================

def criar_tipo_ausencia(descricao_ausencia: str, usa_turno: bool = False) -> TipoAusencia:
    with get_session() as session:
        tipo = TipoAusencia(descricao_ausencia=descricao_ausencia, usa_turno=usa_turno)
        session.add(tipo)
        session.commit()
        session.refresh(tipo)
        return tipo

def listar_tipos_ausencia() -> List[TipoAusencia]:
    with get_session() as session:
        return list(session.execute(select(TipoAusencia)).scalars().all())

def obter_tipo_ausencia(id_tipo: int) -> Optional[TipoAusencia]:
    with get_session() as session:
        return session.get(TipoAusencia, id_tipo)

# ==================== TURNOS ====================

def criar_turno(descricao_ausencia: str) -> Turno:
    with get_session() as session:
        turno = Turno(descricao_ausencia=descricao_ausencia)
        session.add(turno)
        session.commit()
        session.refresh(turno)
        return turno

def listar_turnos() -> List[Turno]:
    with get_session() as session:
        return list(session.execute(select(Turno)).scalars().all())

def obter_turno(turno_id: int) -> Optional[Turno]:
    with get_session() as session:
        return session.get(Turno, turno_id)

# ==================== USUÁRIOS ====================

def criar_usuario(cpf: int, nome: str, email: str, senha: str, 
                 grupo_id: int, inicio_na_empresa: str, uf: str,
                 tipo_usuario: str = TipoUsuario.COMUM.value, 
                 flag_gestor: str = FlagGestor.NAO.value, **kwargs) -> Usuario:
    with get_session() as session:
        # Converte string para date se necessário
        data_inicio = datetime.strptime(inicio_na_empresa, "%Y-%m-%d").date()
        
        # Garante que os valores são strings válidas dos enums
        if isinstance(tipo_usuario, TipoUsuario):
            tipo_usuario = tipo_usuario.value
        if isinstance(flag_gestor, FlagGestor):
            flag_gestor = flag_gestor.value
            
        # Valida valores dos enums
        valid_tipos = [e.value for e in TipoUsuario]
        valid_flags = [e.value for e in FlagGestor]
        
        if tipo_usuario not in valid_tipos:
            raise ValueError(f"tipo_usuario deve ser um de: {valid_tipos}")
        if flag_gestor not in valid_flags:
            raise ValueError(f"flag_gestor deve ser um de: {valid_flags}")
        
        usuario = Usuario(
            cpf=cpf,
            nome=nome,
            email=email.strip().lower(),
            tipo_usuario=tipo_usuario,
            grupo_id=grupo_id,
            inicio_na_empresa=data_inicio,
            UF=uf,
            flag_gestor=flag_gestor,
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

def listar_usuarios(grupo_id: Optional[int] = None, tipo_usuario: Optional[str] = None,
                   ativos_apenas: bool = True) -> List[Usuario]:
    with get_session() as session:
        query = select(Usuario)
        
        conditions = []
        if grupo_id:
            conditions.append(Usuario.grupo_id == grupo_id)
        if tipo_usuario:
            # Converte enum para string se necessário
            if isinstance(tipo_usuario, TipoUsuario):
                tipo_usuario = tipo_usuario.value
            conditions.append(Usuario.tipo_usuario == tipo_usuario)
        if ativos_apenas:
            conditions.append(Usuario.ativo)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return list(session.execute(query).scalars().all())

def obter_usuario(cpf: int) -> Optional[Usuario]:
    with get_session() as session:
        return session.get(Usuario, cpf)

def atualizar_usuario(cpf: int, **kwargs) -> bool:
    with get_session() as session:
        usuario = session.get(Usuario, cpf)
        if not usuario:
            return False
        
        for key, value in kwargs.items():
            if key == "senha":
                usuario.set_senha(value)
            elif key == "inicio_na_empresa" and isinstance(value, str):
                setattr(usuario, key, datetime.strptime(value, "%Y-%m-%d").date())
            elif key == "tipo_usuario":
                if isinstance(value, TipoUsuario):
                    value = value.value
                setattr(usuario, key, value)
            elif key == "flag_gestor":
                if isinstance(value, FlagGestor):
                    value = value.value
                setattr(usuario, key, value)
            else:
                setattr(usuario, key, value)
        
        session.commit()
        return True

def deletar_usuario(cpf: int) -> bool:
    with get_session() as session:
        usuario = session.get(Usuario, cpf)
        if not usuario:
            return False
        usuario.ativo = False
        session.commit()
        return True

# ==================== EVENTOS ====================

def criar_evento(cpf_usuario: int, data_inicio: str, data_fim: str, 
                id_tipo_ausencia: int, uf: str, aprovado_por: int) -> Evento:
    with get_session() as session:
        # Converte strings para date
        inicio_date = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        fim_date = datetime.strptime(data_fim, "%Y-%m-%d").date()
        
        total_dias = (fim_date - inicio_date).days + 1
        
        evento = Evento(
            cpf_usuario=cpf_usuario,
            data_inicio=inicio_date,
            data_fim=fim_date,
            total_dias=total_dias,
            id_tipo_ausencia=id_tipo_ausencia,
            UF=uf,
            aprovado_por=aprovado_por,
            status=StatusEvento.PENDENTE.value  # Usa string do enum
        )
        session.add(evento)
        session.commit()
        session.refresh(evento)
        return evento

def listar_eventos(cpf_usuario: Optional[int] = None, grupo_id: Optional[int] = None,
                  status: Optional[str] = None) -> List[Evento]:
    with get_session() as session:
        query = select(Evento).join(Usuario, Evento.cpf_usuario == Usuario.cpf)
        
        conditions = []
        if cpf_usuario:
            conditions.append(Evento.cpf_usuario == cpf_usuario)
        if grupo_id:
            conditions.append(Usuario.grupo_id == grupo_id)
        if status:
            # Converte enum para string se necessário
            if isinstance(status, StatusEvento):
                status = status.value
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
            elif key == "status":
                if isinstance(value, StatusEvento):
                    value = value.value
                setattr(evento, key, value)
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

def aprovar_evento(evento_id: int, aprovador_cpf: int) -> bool:
    with get_session() as session:
        evento = session.get(Evento, evento_id)
        if not evento:
            return False
        
        evento.status = StatusEvento.APROVADO.value  # Usa string do enum
        evento.aprovado_por = aprovador_cpf
        
        session.commit()
        return True

def rejeitar_evento(evento_id: int, aprovador_cpf: int) -> bool:
    with get_session() as session:
        evento = session.get(Evento, evento_id)
        if not evento:
            return False
        
        evento.status = StatusEvento.REJEITADO.value  # Usa string do enum
        evento.aprovado_por = aprovador_cpf
        
        session.commit()
        return True

# ==================== FERIADOS ====================

def criar_feriado_nacional(data_feriado: str, uf: str, descricao_feriado: str) -> FeriadoNacional:
    with get_session() as session:
        data = datetime.strptime(data_feriado, "%Y-%m-%d").date()
        feriado = FeriadoNacional(
            data_feriado=data,
            uf=uf,
            descricao_feriado=descricao_feriado
        )
        session.add(feriado)
        session.commit()
        session.refresh(feriado)
        return feriado

def criar_feriado_estadual(data_feriado: str, uf: str, descricao_feriado: str) -> FeriadoEstadual:
    with get_session() as session:
        data = datetime.strptime(data_feriado, "%Y-%m-%d").date()
        feriado = FeriadoEstadual(
            data_feriado=data,
            uf=uf,
            descricao_feriado=descricao_feriado
        )
        session.add(feriado)
        session.commit()
        session.refresh(feriado)
        return feriado

def listar_feriados_nacionais(uf: Optional[str] = None) -> List[FeriadoNacional]:
    with get_session() as session:
        query = select(FeriadoNacional)
        if uf:
            query = query.where(FeriadoNacional.uf == uf)
        return list(session.execute(query).scalars().all())

def listar_feriados_estaduais(uf: Optional[str] = None) -> List[FeriadoEstadual]:
    with get_session() as session:
        query = select(FeriadoEstadual)
        if uf:
            query = query.where(FeriadoEstadual.uf == uf)
        return list(session.execute(query).scalars().all())

# ==================== CALENDÁRIO ====================

def eventos_para_calendario(grupo_id: Optional[int] = None, apenas_aprovados: bool = True) -> List[Dict[str, Any]]:
    """Retorna eventos formatados para calendário (FullCalendar.js)"""
    with get_session() as session:
        query = select(Evento).join(Usuario, Evento.cpf_usuario == Usuario.cpf)
        
        conditions = []
        if grupo_id:
            conditions.append(Usuario.grupo_id == grupo_id)
        if apenas_aprovados:
            conditions.append(Evento.status == StatusEvento.APROVADO.value)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        eventos = session.execute(query).scalars().all()
        
        # Formatar para calendário
        eventos_calendario = []
        for evento in eventos:
            # Buscar dados do usuário e tipo de ausência
            usuario = session.get(Usuario, evento.cpf_usuario)
            tipo_ausencia = session.get(TipoAusencia, evento.id_tipo_ausencia)
            
            # Cores por tipo de ausência
            cores_tipo = {
                "Férias": "#28a745",
                "Licença Médica": "#dc3545", 
                "Licença Maternidade": "#6f42c1",
                "Licença Paternidade": "#20c997",
                "Falta Justificada": "#fd7e14",
                "Falta Injustificada": "#dc3545",
                "Abono": "#17a2b8",
                "Compensação": "#6c757d",
                "Home Office": "#007bff",
                "Treinamento": "#ffc107"
            }
            
            tipo_desc = tipo_ausencia.descricao_ausencia if tipo_ausencia else "Ausência"
            cor = cores_tipo.get(tipo_desc, "#6c757d")
            
            evento_calendario = {
                "id": evento.id,
                "title": f"{usuario.nome if usuario else 'N/A'} - {tipo_desc}",
                "start": evento.data_inicio.isoformat(),
                "end": (evento.data_fim + timedelta(days=1)).isoformat(),  # FullCalendar usa end exclusivo
                "backgroundColor": cor,
                "borderColor": cor,
                "textColor": "#ffffff",
                "extendedProps": {
                    "cpf_usuario": evento.cpf_usuario,
                    "usuario_nome": usuario.nome if usuario else "N/A",
                    "tipo_ausencia": tipo_desc,
                    "total_dias": evento.total_dias,
                    "status": evento.status,
                    "uf": evento.UF,
                    "criado_em": evento.criado_em.isoformat()
                }
            }
            eventos_calendario.append(evento_calendario)
        
        return eventos_calendario

# ==================== CONVERSORES ====================

def empresa_para_dict(empresa: Empresa) -> Dict[str, Any]:
    with get_session() as session:
        # Conta grupos da empresa
        total_grupos = session.execute(
            select(func.count(Grupo.id)).where(Grupo.cnpj_empresa == empresa.cnpj)
        ).scalar()
        
        return {
            "cnpj": empresa.cnpj,
            "id": empresa.id,
            "nome": empresa.nome,
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
        empresa = session.get(Empresa, grupo.cnpj_empresa)
        empresa_nome = empresa.nome if empresa else "N/A"
        
        # Conta usuários do grupo
        total_usuarios = session.execute(
            select(func.count(Usuario.cpf)).where(Usuario.grupo_id == grupo.id)
        ).scalar()
        
        return {
            "id": grupo.id,
            "nome": grupo.nome,
            "descricao": grupo.descricao,
            "cnpj_empresa": grupo.cnpj_empresa,
            "empresa_nome": empresa_nome,
            "telefone": grupo.telefone,
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
        
        return {
            "cpf": usuario.cpf,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo_usuario": usuario.tipo_usuario,  # Já é string
            "grupo_id": usuario.grupo_id,
            "grupo_nome": grupo_nome,
            "inicio_na_empresa": usuario.inicio_na_empresa.isoformat(),
            "ativo": usuario.ativo,
            "criado_em": usuario.criado_em.isoformat(),
            "UF": usuario.UF,
            "flag_gestor": usuario.flag_gestor  # Já é string
        }

def evento_para_dict(evento: Evento) -> Dict[str, Any]:
    with get_session() as session:
        # Busca nome do usuário
        usuario = session.get(Usuario, evento.cpf_usuario)
        usuario_nome = usuario.nome if usuario else "N/A"
        
        # Busca nome do aprovador
        aprovador = session.get(Usuario, evento.aprovado_por)
        aprovado_por_nome = aprovador.nome if aprovador else "N/A"
        
        # Busca tipo de ausência
        tipo_ausencia = session.get(TipoAusencia, evento.id_tipo_ausencia)
        tipo_ausencia_desc = tipo_ausencia.descricao_ausencia if tipo_ausencia else "N/A"
        
        return {
            "id": evento.id,
            "cpf_usuario": evento.cpf_usuario,
            "usuario_nome": usuario_nome,
            "data_inicio": evento.data_inicio.isoformat(),
            "data_fim": evento.data_fim.isoformat(),
            "total_dias": evento.total_dias,
            "id_tipo_ausencia": evento.id_tipo_ausencia,
            "tipo_ausencia_desc": tipo_ausencia_desc,
            "status": evento.status,  # Já é string
            "aprovado_por": evento.aprovado_por,
            "aprovado_por_nome": aprovado_por_nome,
            "criado_em": evento.criado_em.isoformat(),
            "UF": evento.UF
        }
