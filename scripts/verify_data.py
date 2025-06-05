#!/usr/bin/env python3
"""
Script para verificar os dados no banco de dados
Exibe um resumo de todos os dados existentes
"""

import os
import sys
import logging
from dotenv import load_dotenv
from tabulate import tabulate

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database.models import init_db, get_session
from api.database.models import (
    Usuario, Empresa, Grupo, UF, TipoAusencia, 
    Turno, FeriadoNacional, FeriadoEstadual, Evento
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def count_records(model):
    """Conta registros de um modelo"""
    with get_session() as session:
        return session.query(model).count()

def get_sample_records(model, limit=5):
    """Obtém uma amostra de registros"""
    with get_session() as session:
        return session.query(model).limit(limit).all()

def print_table(title, headers, rows):
    """Imprime uma tabela formatada"""
    print(f"\n{title}")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

def verify_ufs():
    """Verifica UFs cadastradas"""
    count = count_records(UF)
    samples = get_sample_records(UF, 5)
    
    rows = [[uf.cod_uf, uf.uf] for uf in samples]
    print_table(f"UFs Cadastradas (Total: {count})", ["Código", "UF"], rows)
    
    return count

def verify_empresas():
    """Verifica empresas cadastradas"""
    count = count_records(Empresa)
    samples = get_sample_records(Empresa, 5)
    
    rows = [[empresa.cnpj, empresa.nome, empresa.telefone] for empresa in samples]
    print_table(f"Empresas Cadastradas (Total: {count})", ["CNPJ", "Nome", "Telefone"], rows)
    
    return count

def verify_grupos():
    """Verifica grupos cadastrados"""
    count = count_records(Grupo)
    samples = get_sample_records(Grupo, 5)
    
    rows = [[grupo.id, grupo.nome, grupo.cnpj_empresa] for grupo in samples]
    print_table(f"Grupos Cadastrados (Total: {count})", ["ID", "Nome", "CNPJ Empresa"], rows)
    
    return count

def verify_usuarios():
    """Verifica usuários cadastrados"""
    count = count_records(Usuario)
    samples = get_sample_records(Usuario, 5)
    
    rows = [[
        usuario.cpf, 
        usuario.nome, 
        usuario.email, 
        usuario.tipo_usuario,
        usuario.UF,
        usuario.flag_gestor
    ] for usuario in samples]
    
    print_table(
        f"Usuários Cadastrados (Total: {count})", 
        ["CPF", "Nome", "Email", "Tipo", "UF", "Gestor"], 
        rows
    )
    
    return count

def verify_tipos_ausencia():
    """Verifica tipos de ausência cadastrados"""
    count = count_records(TipoAusencia)
    samples = get_sample_records(TipoAusencia)
    
    rows = [[tipo.id_tipo_ausencia, tipo.descricao_ausencia, "Sim" if tipo.usa_turno else "Não"] 
            for tipo in samples]
    
    print_table(
        f"Tipos de Ausência Cadastrados (Total: {count})", 
        ["ID", "Descrição", "Usa Turno"], 
        rows
    )
    
    return count

def verify_turnos():
    """Verifica turnos cadastrados"""
    count = count_records(Turno)
    samples = get_sample_records(Turno)
    
    rows = [[turno.id, turno.descricao_ausencia] for turno in samples]
    print_table(f"Turnos Cadastrados (Total: {count})", ["ID", "Descrição"], rows)
    
    return count

def verify_feriados():
    """Verifica feriados cadastrados"""
    count_nacionais = count_records(FeriadoNacional)
    count_estaduais = count_records(FeriadoEstadual)
    
    samples_nacionais = get_sample_records(FeriadoNacional, 3)
    samples_estaduais = get_sample_records(FeriadoEstadual, 3)
    
    rows_nacionais = [[
        feriado.data_feriado.strftime('%Y-%m-%d'), 
        feriado.descricao_feriado,
        feriado.uf
    ] for feriado in samples_nacionais]
    
    rows_estaduais = [[
        feriado.data_feriado.strftime('%Y-%m-%d'), 
        feriado.descricao_feriado,
        feriado.uf
    ] for feriado in samples_estaduais]
    
    print_table(
        f"Feriados Nacionais Cadastrados (Total: {count_nacionais})", 
        ["Data", "Descrição", "UF"], 
        rows_nacionais
    )
    
    print_table(
        f"Feriados Estaduais Cadastrados (Total: {count_estaduais})", 
        ["Data", "Descrição", "UF"], 
        rows_estaduais
    )
    
    return count_nacionais + count_estaduais

def verify_eventos():
    """Verifica eventos cadastrados"""
    count = count_records(Evento)
    samples = get_sample_records(Evento, 5)
    
    rows = [[
        evento.id,
        evento.cpf_usuario,
        evento.data_inicio.strftime('%Y-%m-%d'),
        evento.data_fim.strftime('%Y-%m-%d'),
        evento.status
    ] for evento in samples]
    
    print_table(
        f"Eventos Cadastrados (Total: {count})", 
        ["ID", "CPF", "Data Início", "Data Fim", "Status"], 
        rows
    )
    
    return count

def connect_to_database():
    """Conecta ao banco de dados usando as mesmas configurações do seed"""
    # Configuração do banco MySQL
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    
    database_url = None
    if all([db_host, db_name, db_user, db_pass]):
        database_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        logging.info("🚀 Conectando ao MySQL...")
        logging.info(f"📊 Host: {db_host}")
        logging.info(f"🗄️ Database: {db_name}")
    else:
        logging.info("⚠️ Variáveis MySQL não configuradas, usando SQLite local")
    
    init_db(database_url)
    logging.info("✅ Conexão com o banco de dados estabelecida com sucesso!")

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("📊 VERIFICAÇÃO DE DADOS NO BANCO")
    print("="*60)
    
    # Carrega variáveis de ambiente
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logging.info(f"✅ Arquivo .env carregado: {env_path}")
    else:
        logging.warning("⚠️ Arquivo .env não encontrado")
    
    # Conecta ao banco usando a mesma lógica do seed
    try:
        connect_to_database()
    except Exception as e:
        logging.error(f"❌ Erro ao conectar com o banco: {e}")
        return
    
    # Verifica dados
    try:
        print("\n" + "="*60)
        print("📊 RESUMO DOS DADOS NO BANCO")
        print("="*60)
        
        ufs = verify_ufs()
        empresas = verify_empresas()
        grupos = verify_grupos()
        usuarios = verify_usuarios()
        tipos_ausencia = verify_tipos_ausencia()
        turnos = verify_turnos()
        feriados = verify_feriados()
        eventos = verify_eventos()
        
        print("\n" + "="*60)
        print("📊 TOTAIS:")
        print(f"🗺️  UFs: {ufs}")
        print(f"🏢 Empresas: {empresas}")
        print(f"👥 Grupos: {grupos}")
        print(f"👤 Usuários: {usuarios}")
        print(f"📋 Tipos de Ausência: {tipos_ausencia}")
        print(f"⏰ Turnos: {turnos}")
        print(f"🎉 Feriados: {feriados}")
        print(f"📅 Eventos: {eventos}")
        print("="*60)
        
    except Exception as e:
        logging.error(f"❌ Erro durante a verificação: {e}")
        return
    
    print("\n" + "="*60)
    print("✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)

if __name__ == "__main__":
    main()
