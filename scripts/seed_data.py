"""
Script para popular o banco de dados MySQL com dados de exemplo
"""
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório pai ao path para importar os módulos
print(f"📁 Script directory: {Path(__file__).parent}")
print(f"📁 Project root: {Path(__file__).parent.parent}")

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
print(f"🐍 Python path: {sys.path[:3]}...")

# Verifica se o arquivo .env existe
env_path = project_root / ".env"
if env_path.exists():
    print(f"✅ Arquivo .env carregado: {env_path}")
else:
    print(f"⚠️ Arquivo .env não encontrado em: {env_path}")

try:
    from api.database.models import init_db, TipoUsuario, FlagGestor
    from api.database.crud import criar_empresa, criar_grupo, criar_usuario
    print("✅ Módulos importados com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("💡 Verifique se o diretório 'api' está no PYTHONPATH")
    sys.exit(1)

def seed_database():
    """Popula o banco MySQL com dados de exemplo"""
    print("🌱 Iniciando seed do banco de dados...")
    print("🔍 Validando ambiente...")
    
    # Configuração do banco MySQL
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    
    database_url = None
    if all([db_host, db_name, db_user, db_pass]):
        database_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        print("🚀 Conectando ao MySQL...")
        print(f"📊 Host: {db_host}")
        print(f"🗄️  Database: {db_name}")
    else:
        print("⚠️ Variáveis MySQL não configuradas, usando SQLite local")
    
    try:
        # Inicializa o banco
        init_db(database_url)
        
        # Importa o engine após a inicialização
        from api.database.models import engine
        
        # Verifica se o engine foi criado
        if engine is None:
            raise Exception("Engine não foi inicializado corretamente")
        
        # Testa a conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                if database_url and database_url.startswith("mysql"):
                    print("✅ Conexão com MySQL estabelecida com sucesso!")
                else:
                    print("✅ Conexão com SQLite estabelecida com sucesso!")
            
            # Verifica se as tabelas existem (para MySQL)
            if database_url and database_url.startswith("mysql"):
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() AND table_name IN "
                    "('empresa', 'grupo', 'usuario')"
                ))
                table_count = result.scalar()
                if table_count is not None and table_count >= 3:
                    print("✅ Tabelas criadas/verificadas!")
                else:
                    print("⚠️ Algumas tabelas podem estar faltando!")
            else:
                # Para SQLite, verifica de forma diferente
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM sqlite_master "
                    "WHERE type='table' AND name IN ('empresa', 'grupo', 'usuario')"
                ))
                table_count = result.scalar()
                if table_count is not None and table_count >= 3:
                    print("✅ Tabelas criadas/verificadas!")
                else:
                    print("⚠️ Algumas tabelas podem estar faltando!")
        
        print("✅ Conexão estabelecida! Criando dados de exemplo...")
        
        # Cria empresa
        empresa = criar_empresa(
            cnpj=12345678000190,
            id_empresa=1,
            nome="Tech Solutions LTDA",
            endereco="Rua das Flores, 123 - São Paulo/SP",
            telefone="(11) 1234-5678",
            email="contato@techsolutions.com"
        )
        print(f"✅ Empresa criada: {empresa.nome}")
        
        # Cria grupos
        grupo_rh = criar_grupo(
            nome="Recursos Humanos",
            cnpj_empresa=empresa.cnpj,
            telefone="(11) 1234-5679",
            descricao="Equipe de recursos humanos"
        )

        grupo_dev = criar_grupo(
            nome="Desenvolvimento",
            cnpj_empresa=empresa.cnpj,
            telefone="(11) 1234-5680",
            descricao="Equipe de desenvolvimento de software"
        )
        
        print(f"✅ Grupos criados: {grupo_rh.nome}, {grupo_dev.nome}")
        
        # Cria usuários
        usuario_rh_obj = criar_usuario(
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
        
        usuario_gestor_obj = criar_usuario(
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
        
        usuario_comum_obj = criar_usuario(
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
        
        print("✅ Usuários criados:")
        print(f"- RH: {usuario_rh_obj.nome} (CPF {usuario_rh_obj.cpf})")
        print(f"- Gestor: {usuario_gestor_obj.nome} (CPF {usuario_gestor_obj.cpf})")
        print(f"- Comum: {usuario_comum_obj.nome} (CPF {usuario_comum_obj.cpf})")
        
        print("\n🎉 Dados de exemplo criados com sucesso!")

        print("\n=== CREDENCIAIS DE TESTE ===")
        print(f"RH: {usuario_rh_obj.email} / 123456 (CPF {usuario_rh_obj.cpf})")
        print(f"Gestor: {usuario_gestor_obj.email} / 123456 (CPF {usuario_gestor_obj.cpf})")
        print(f"Comum: {usuario_comum_obj.email} / 123456 (CPF {usuario_comum_obj.cpf})")
        
    except IntegrityError as ie:
        print(f"❌ Erro de integridade dos dados: {ie}")
        print("💡 Dados podem já existir no banco. Execute DROP das tabelas se necessário.")
        raise
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        raise

if __name__ == "__main__":
    seed_database()
