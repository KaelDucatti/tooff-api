#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para popular o banco de dados com dados iniciais de forma segura.
Verifica a existência dos dados antes de inserir para evitar duplicações.
"""

import os
import sys
import logging
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importar após ajustar o path
try:
    from api.database.models import (
        init_db, Grupo, 
        TipoUsuario, FlagGestor, get_session
    )
    from api.database.crud import (
        obter_empresa, obter_usuario,
        criar_empresa, criar_grupo, criar_usuario
    )
    from dotenv import load_dotenv
except ImportError as e:
    logger.error(f"❌ Erro ao importar módulos: {e}")
    logger.error("Verifique se o ambiente virtual está ativado e se os módulos estão instalados.")
    sys.exit(1)

def load_environment():
    """Carrega variáveis de ambiente do arquivo .env"""
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"✅ Arquivo .env carregado: {env_path}")
    else:
        logger.warning(f"⚠️ Arquivo .env não encontrado em: {env_path}")
        logger.warning("Usando variáveis de ambiente do sistema.")

def check_database_connection():
    """Verifica a conexão com o banco de dados"""
    try:
        # Configuração do banco MySQL
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')
        
        database_url = None
        if all([db_host, db_name, db_user, db_pass]):
            database_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
            logger.info("🚀 Conectando ao MySQL...")
            logger.info(f"📊 Host: {db_host}")
            logger.info(f"🗄️  Database: {db_name}")
        else:
            logger.info("⚠️ Variáveis MySQL não configuradas, usando SQLite local")
        
        # Inicializar o banco de dados
        init_db(database_url)
        
        # Importar engine após inicialização
        from api.database.models import engine
        
        # Verificar conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("✅ Conexão com o banco de dados estabelecida com sucesso!")
                return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        return False

def safe_create_empresa(cnpj, nome, **kwargs):
    """Cria uma empresa apenas se ela não existir"""
    try:
        # Verificar se a empresa já existe
        empresa_existente = obter_empresa(cnpj)
        if empresa_existente:
            logger.info(f"ℹ️ Empresa já existe: {nome} (CNPJ: {cnpj})")
            return empresa_existente
        
        # Criar empresa
        empresa = criar_empresa(cnpj=cnpj, nome=nome, **kwargs)
        logger.info(f"✅ Empresa criada: {nome} (CNPJ: {cnpj})")
        return empresa
    except Exception as e:
        logger.error(f"❌ Erro ao criar empresa {nome}: {e}")
        return None

def safe_create_grupo(nome, cnpj_empresa, **kwargs):
    """Cria um grupo apenas se ele não existir com o mesmo nome na mesma empresa"""
    try:
        # Verificar se o grupo já existe
        with get_session() as session:
            grupo_existente = session.query(Grupo).filter_by(
                nome=nome, cnpj_empresa=cnpj_empresa
            ).first()
        
        if grupo_existente:
            logger.info(f"ℹ️ Grupo já existe: {nome} (ID: {grupo_existente.id})")
            return grupo_existente
        
        # Criar grupo
        grupo = criar_grupo(nome=nome, cnpj_empresa=cnpj_empresa, **kwargs)
        logger.info(f"✅ Grupo criado: {nome} (ID: {grupo.id})")
        return grupo
    except Exception as e:
        logger.error(f"❌ Erro ao criar grupo {nome}: {e}")
        return None

def safe_create_usuario(cpf, nome, email, **kwargs):
    """Cria um usuário apenas se ele não existir"""
    try:
        # Verificar se o usuário já existe
        usuario_existente = obter_usuario(cpf)
        if usuario_existente:
            logger.info(f"ℹ️ Usuário já existe: {nome} (CPF: {cpf})")
            return usuario_existente
        
        # Criar usuário
        usuario = criar_usuario(cpf=cpf, nome=nome, email=email, **kwargs)
        logger.info(f"✅ Usuário criado: {nome} (CPF: {cpf})")
        return usuario
    except Exception as e:
        logger.error(f"❌ Erro ao criar usuário {nome}: {e}")
        return None

def seed_database():
    """Popula o banco de dados com dados iniciais de forma segura"""
    logger.info("🌱 Iniciando seed seguro do banco de dados...")
    
    try:
        # Criar empresa
        empresa = safe_create_empresa(
            cnpj=12345678000190,
            id_empresa=1,
            nome="Tech Solutions LTDA",
            endereco="Rua das Flores, 123 - São Paulo/SP",
            telefone="(11) 1234-5678",
            email="contato@techsolutions.com"
        )
        
        if not empresa:
            logger.error("❌ Não foi possível criar a empresa principal. Abortando.")
            return False
        
        # Criar grupos
        grupo_rh = safe_create_grupo(
            nome="Recursos Humanos",
            cnpj_empresa=empresa.cnpj,
            telefone="(11) 1234-5679",
            descricao="Equipe de recursos humanos"
        )
        
        grupo_dev = safe_create_grupo(
            nome="Desenvolvimento",
            cnpj_empresa=empresa.cnpj,
            telefone="(11) 1234-5680",
            descricao="Equipe de desenvolvimento de software"
        )
        
        if not grupo_rh or not grupo_dev:
            logger.error("❌ Não foi possível criar os grupos. Abortando.")
            return False
        
        # Criar usuários
        usuario_rh = safe_create_usuario(
            cpf=12345678901,
            nome="Maria Silva",
            email="maria.rh@techsolutions.com",
            senha="123456",
            grupo_id=grupo_rh.id,
            inicio_na_empresa="2020-01-15",
            uf="SP",
            tipo_usuario=TipoUsuario.RH.value,
            flag_gestor=FlagGestor.NAO.value
        )
        
        usuario_gestor = safe_create_usuario(
            cpf=23456789012,
            nome="João Santos",
            email="joao.gestor@techsolutions.com",
            senha="123456",
            grupo_id=grupo_dev.id,
            inicio_na_empresa="2021-03-10",
            uf="SP",
            tipo_usuario=TipoUsuario.GESTOR.value,
            flag_gestor=FlagGestor.SIM.value
        )
        
        usuario_comum = safe_create_usuario(
            cpf=34567890123,
            nome="Ana Costa",
            email="ana.dev@techsolutions.com",
            senha="123456",
            grupo_id=grupo_dev.id,
            inicio_na_empresa="2022-06-01",
            uf="SP",
            tipo_usuario=TipoUsuario.COMUM.value,
            flag_gestor=FlagGestor.NAO.value
        )
        
        # Resumo final
        logger.info("\n" + "="*50)
        logger.info("📊 RESUMO DO SEED:")
        logger.info(f"🏢 Empresa: {empresa.nome}")
        logger.info(f"👥 Grupos: {grupo_rh.nome}, {grupo_dev.nome}")
        logger.info(f"👤 Usuários criados/verificados: 3")
        logger.info("="*50)
        
        logger.info("✅ Seed concluído com sucesso!")
        return True
    
    except Exception as e:
        logger.error(f"❌ Erro inesperado durante o seed: {e}")
        return False

def main():
    """Função principal"""
    print("\n" + "="*50)
    print("🌱 SEED SEGURO DO BANCO DE DADOS")
    print("="*50 + "\n")
    
    # Carregar variáveis de ambiente
    load_environment()
    
    # Verificar conexão com o banco
    if not check_database_connection():
        logger.error("❌ Não foi possível conectar ao banco de dados. Abortando.")
        return 1
    
    # Executar seed
    success = seed_database()
    
    if success:
        print("\n" + "="*50)
        print("✅ SEED CONCLUÍDO COM SUCESSO!")
        print("="*50 + "\n")
        print("=== CREDENCIAIS DE TESTE ===")
        print("RH: maria.rh@techsolutions.com / 123456")
        print("Gestor: joao.gestor@techsolutions.com / 123456")
        print("Comum: ana.dev@techsolutions.com / 123456")
        print("="*50)
        return 0
    else:
        print("\n" + "="*50)
        print("❌ SEED FALHOU!")
        print("="*50 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
