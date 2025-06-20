from typing import List, Optional, Dict, Any, Union # Added Union
from datetime import datetime, timedelta, date 
from sqlalchemy import select, and_, func, extract, or_ 
from sqlalchemy.orm import Session 

from .models import (
  get_session, Usuario, Empresa, Grupo, Evento, UF,
  TipoAusencia, Turno, FeriadoNacional, FeriadoEstadual,
  TipoUsuario, StatusEvento, FlagGestor
)

# Constants for vacation logic
VACATION_TYPE_DESCRIPTION = "Férias"
MAX_VACATION_DAYS_ALLOWANCE = 30
MIN_EMPLOYMENT_DURATION_DAYS = 365


# ==================== DATE UTILITIES (NEW) ====================

def is_weekend(date_obj: date) -> bool:
  """Checks if a date is a weekend (Saturday or Sunday)."""
  return date_obj.weekday() >= 5 # Monday is 0 and Sunday is 6

def get_holidays_for_uf(session: Session, target_date: date, uf_code: str) -> List[Union[FeriadoNacional, FeriadoEstadual]]:
  """Gets national and specific state holidays for a given date and UF."""
  national_holidays = session.execute(
      select(FeriadoNacional).where(FeriadoNacional.data_feriado == target_date)
  ).scalars().all()
  
  state_holidays = []
  if uf_code: # Only query state holidays if a UF code is provided
      state_holidays = session.execute(
          select(FeriadoEstadual).where(
              and_(
                  FeriadoEstadual.data_feriado == target_date,
                  FeriadoEstadual.uf == uf_code.upper() # Ensure UF code is uppercase for comparison
              )
          )
      ).scalars().all()
  return list(national_holidays) + list(state_holidays)

def is_public_holiday(session: Session, date_obj: date, uf_code: str) -> bool:
  """Checks if a date is a public holiday for a given UF."""
  if not uf_code: # Cannot check state holidays without UF
      # Check only national holidays if UF is not provided
      national_holidays = session.execute(
          select(FeriadoNacional).where(FeriadoNacional.data_feriado == date_obj)
      ).scalars().all()
      return bool(national_holidays)
  return bool(get_holidays_for_uf(session, date_obj, uf_code))

def get_approved_vacation_days_last_12_months(session: Session, cpf_usuario: int, reference_date: date) -> int:
  """
  Calculates the total number of approved vacation days taken by a user
  in the 12 months leading up to the reference_date.
  Vacations are identified by VACATION_TYPE_DESCRIPTION.
  """
  # CRITICAL FIX: Case-insensitive and space-trimmed comparison for vacation type in DB query
  vacation_tipo_ausencia = session.execute(
      select(TipoAusencia).where(func.lower(func.trim(TipoAusencia.descricao_ausencia)) == VACATION_TYPE_DESCRIPTION.strip().lower())
  ).scalar_one_or_none()

  # CRITICAL FIX: Prevent crash if "Férias" type is not found in the database.
  if not vacation_tipo_ausencia:
      return 0 

  twelve_months_ago = reference_date - timedelta(days=365) 

  approved_vacations = session.execute(
      select(func.sum(Evento.total_dias)).where(
          and_(
              Evento.cpf_usuario == cpf_usuario,
              Evento.id_tipo_ausencia == vacation_tipo_ausencia.id_tipo_ausencia,
              Evento.status == StatusEvento.APROVADO.value,
              Evento.data_inicio >= twelve_months_ago, # Vacations starting within the 12-month window
              Evento.data_inicio < reference_date # Vacations starting before the reference date (e.g., today)
          )
      )
  ).scalar_one_or_none()

  return approved_vacations or 0

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

def criar_turno(descricao_turno: str) -> Turno:
  with get_session() as session:
      turno = Turno(descricao_ausencia=descricao_turno)  # Fixed: use correct attribute name
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
      email_normalizado = email.strip().lower()
      # Explicit check for email duplication before attempting to insert
      email_existente = session.execute(
          select(Usuario).where(Usuario.email == email_normalizado)
      ).scalar_one_or_none()
      if email_existente:
          raise ValueError("Email já cadastrado") # This will be caught by the route
          
      data_inicio_empresa = datetime.strptime(inicio_na_empresa, "%Y-%m-%d").date()
      
      if isinstance(tipo_usuario, TipoUsuario):
          tipo_usuario = tipo_usuario.value
      if isinstance(flag_gestor, FlagGestor):
          flag_gestor = flag_gestor.value
          
      valid_tipos = [e.value for e in TipoUsuario]
      valid_flags = [e.value for e in FlagGestor]
      
      if tipo_usuario not in valid_tipos:
          raise ValueError(f"tipo_usuario deve ser um de: {valid_tipos}")
      if flag_gestor not in valid_flags:
          raise ValueError(f"flag_gestor deve ser um de: {valid_flags}")
      
      usuario = Usuario(
          cpf=cpf,
          nome=nome,
          email=email_normalizado,
          tipo_usuario=tipo_usuario,
          grupo_id=grupo_id,
          inicio_na_empresa=data_inicio_empresa,
          UF=uf.upper(), # Store UF as uppercase
          flag_gestor=flag_gestor,
          criado_em=datetime.now(), # Ensure criado_em is set
          ativo=True, # Ensure new users are active by default
          **kwargs
      )
      usuario.set_senha(senha) # Hashes the password
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
              if isinstance(value, TipoUsuario): value = value.value
              setattr(usuario, key, value)
          elif key == "flag_gestor":
              if isinstance(value, FlagGestor): value = value.value
              setattr(usuario, key, value)
          elif key == "UF" and isinstance(value, str):
              setattr(usuario, key, value.upper())
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
              id_tipo_ausencia: int, uf: str, aprovado_por: int,
              session: Session 
              ) -> Evento:
  
  inicio_date = datetime.strptime(data_inicio, "%Y-%m-%d").date()
  fim_date = datetime.strptime(data_fim, "%Y-%m-%d").date()
  
  total_dias = (fim_date - inicio_date).days + 1
  
  evento = Evento(
      cpf_usuario=cpf_usuario,
      data_inicio=inicio_date,
      data_fim=fim_date,
      total_dias=total_dias,
      id_tipo_ausencia=id_tipo_ausencia,
      UF=uf.upper(), # Store UF as uppercase
      aprovado_por=aprovado_por,
      status=StatusEvento.PENDENTE.value,
      criado_em=datetime.now() # Ensure criado_em is set
  )
  session.add(evento)
  session.commit() # Commit here to ensure event ID is generated if needed by caller
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
          if isinstance(status, StatusEvento): status = status.value
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
              if isinstance(value, StatusEvento): value = value.value
              setattr(evento, key, value)
          elif key == "UF" and isinstance(value, str):
              setattr(evento, key, value.upper())
          else:
              setattr(evento, key, value)
      
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
      
      evento.status = StatusEvento.APROVADO.value
      evento.aprovado_por = aprovador_cpf
      
      session.commit()
      return True

def rejeitar_evento(evento_id: int, aprovador_cpf: int) -> bool:
  with get_session() as session:
      evento = session.get(Evento, evento_id)
      if not evento:
          return False
      
      evento.status = StatusEvento.REJEITADO.value
      evento.aprovado_por = aprovador_cpf
      
      session.commit()
      return True

# ==================== FERIADOS ====================

def criar_feriado_nacional(data_feriado: str, descricao_feriado: str, uf: str = "BR") -> FeriadoNacional: # uf default BR for national
  with get_session() as session:
      data = datetime.strptime(data_feriado, "%Y-%m-%d").date()
      feriado = FeriadoNacional(
          data_feriado=data,
          uf=uf.upper(), # Store UF as uppercase
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
          uf=uf.upper(), # Store UF as uppercase
          descricao_feriado=descricao_feriado
      )
      session.add(feriado)
      session.commit()
      session.refresh(feriado)
      return feriado

def listar_feriados_nacionais() -> List[FeriadoNacional]: # Removed uf parameter as national holidays are not UF specific
  with get_session() as session:
      query = select(FeriadoNacional)
      return list(session.execute(query).scalars().all())

def listar_feriados_estaduais(uf: Optional[str] = None) -> List[FeriadoEstadual]:
  with get_session() as session:
      query = select(FeriadoEstadual)
      if uf:
          query = query.where(FeriadoEstadual.uf == uf.upper())
      return list(session.execute(query).scalars().all())

# ==================== CALENDÁRIO ====================

def eventos_para_calendario(grupo_id: Optional[int] = None, apenas_aprovados: bool = True) -> List[Dict[str, Any]]:
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
      
      eventos_calendario = []
      for evento in eventos:
          usuario = session.get(Usuario, evento.cpf_usuario)
          tipo_ausencia_obj = session.get(TipoAusencia, evento.id_tipo_ausencia)
          
          cores_tipo = {
              "Férias": "#28a745", "Licença Médica": "#dc3545", 
              "Licença Maternidade": "#6f42c1", "Licença Paternidade": "#20c997",
              "Falta Justificada": "#fd7e14", "Falta Injustificada": "#dc3545",
              "Abono": "#17a2b8", "Compensação": "#6c757d",
              "Home Office": "#007bff", "Treinamento": "#ffc107"
          }
          
          tipo_desc = tipo_ausencia_obj.descricao_ausencia.strip() if tipo_ausencia_obj else "Ausência"
          cor = cores_tipo.get(tipo_desc, "#6c757d") # Default color
          if evento.status == StatusEvento.PENDENTE.value:
              cor = "#ffc107" # Yellow for pending
          elif evento.status == StatusEvento.REJEITADO.value:
              cor = "#dc3545" # Red for rejected
          
          evento_calendario = {
              "id": evento.id,
              "title": f"{usuario.nome if usuario else 'N/A'} - {tipo_desc}",
              "start": evento.data_inicio.isoformat(),
              "end": (evento.data_fim + timedelta(days=1)).isoformat(),
              "backgroundColor": cor, "borderColor": cor, "textColor": "#ffffff",
              "extendedProps": {
                  "cpf_usuario": evento.cpf_usuario,
                  "usuario_nome": usuario.nome if usuario else "N/A",
                  "tipo_ausencia": tipo_desc, "total_dias": evento.total_dias,
                  "status": evento.status, "uf": evento.UF,
                  "criado_em": evento.criado_em.isoformat() if evento.criado_em else None
              }
          }
          eventos_calendario.append(evento_calendario)
      
      return eventos_calendario

# ==================== CONVERSORES (para_dict) ====================

def empresa_para_dict(empresa: Empresa) -> Dict[str, Any]:
  with get_session() as session:
      total_grupos = session.execute(
          select(func.count(Grupo.id)).where(Grupo.cnpj_empresa == empresa.cnpj)
      ).scalar_one_or_none() or 0
      
      return {
          "cnpj": empresa.cnpj, "id": empresa.id, "nome": empresa.nome,
          "endereco": empresa.endereco, "telefone": empresa.telefone,
          "email": empresa.email, "ativa": empresa.ativa,
          "criado_em": empresa.criado_em.isoformat() if empresa.criado_em else None,
          "total_grupos": total_grupos
      }

def grupo_para_dict(grupo: Grupo) -> Dict[str, Any]:
  with get_session() as session:
      empresa = session.get(Empresa, grupo.cnpj_empresa)
      empresa_nome = empresa.nome if empresa else "N/A"
      
      total_usuarios = session.execute(
          select(func.count(Usuario.cpf)).where(Usuario.grupo_id == grupo.id)
      ).scalar_one_or_none() or 0
      
      return {
          "id": grupo.id, "nome": grupo.nome, "descricao": grupo.descricao,
          "cnpj_empresa": grupo.cnpj_empresa, "empresa_nome": empresa_nome,
          "telefone": grupo.telefone, "ativo": grupo.ativo,
          "criado_em": grupo.criado_em.isoformat() if grupo.criado_em else None,
          "total_usuarios": total_usuarios
      }

def usuario_para_dict(usuario: Usuario) -> Dict[str, Any]:
  with get_session() as session:
      grupo_nome = None
      if usuario.grupo_id:
          grupo = session.get(Grupo, usuario.grupo_id)
          grupo_nome = grupo.nome if grupo else None
      
      return {
          "cpf": usuario.cpf, "nome": usuario.nome, "email": usuario.email,
          "tipo_usuario": usuario.tipo_usuario, "grupo_id": usuario.grupo_id,
          "grupo_nome": grupo_nome,
          "inicio_na_empresa": usuario.inicio_na_empresa.isoformat() if usuario.inicio_na_empresa else None,
          "ativo": usuario.ativo, 
          "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None,
          "UF": usuario.UF, "flag_gestor": usuario.flag_gestor
      }

def evento_para_dict(evento: Evento) -> Dict[str, Any]:
  with get_session() as session:
      usuario = session.get(Usuario, evento.cpf_usuario)
      usuario_nome = usuario.nome if usuario else "N/A"
      
      aprovador_nome = "N/A"
      if evento.aprovado_por:
          aprovador = session.get(Usuario, evento.aprovado_por)
          aprovador_nome = aprovador.nome if aprovador else "N/A"
      
      tipo_ausencia_obj = session.get(TipoAusencia, evento.id_tipo_ausencia)
      tipo_ausencia_desc = tipo_ausencia_obj.descricao_ausencia.strip() if tipo_ausencia_obj else "N/A"
      
      return {
          "id": evento.id, "cpf_usuario": evento.cpf_usuario,
          "usuario_nome": usuario_nome,
          "data_inicio": evento.data_inicio.isoformat() if evento.data_inicio else None,
          "data_fim": evento.data_fim.isoformat() if evento.data_fim else None,
          "total_dias": evento.total_dias,
          "id_tipo_ausencia": evento.id_tipo_ausencia,
          "tipo_ausencia_desc": tipo_ausencia_desc,
          "status": evento.status, "aprovado_por": evento.aprovado_por,
          "aprovado_por_nome": aprovador_nome,
          "criado_em": evento.criado_em.isoformat() if evento.criado_em else None, 
          "UF": evento.UF
      }
