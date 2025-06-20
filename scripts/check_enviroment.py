"""
Script para diagnosticar problemas de ambiente e importação
"""
import sys
import os
from pathlib import Path

def check_project_structure():
    """Verifica a estrutura do projeto"""
    print("🔍 DIAGNÓSTICO DA ESTRUTURA DO PROJETO")
    print("=" * 50)
    
    # Diretório atual
    current_dir = Path.cwd()
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"📁 Diretório atual: {current_dir}")
    print(f"📁 Diretório do script: {script_dir}")
    print(f"📁 Raiz do projeto: {project_root}")
    
    # Verifica estrutura esperada
    expected_structure = {
        "api/": "Diretório principal da API",
        "api/__init__.py": "Arquivo de inicialização do pacote",
        "api/database/": "Módulo de banco de dados",
        "api/database/__init__.py": "Init do módulo database",
        "api/database/models.py": "Modelos do banco",
        "api/database/crud.py": "Operações CRUD",
        "scripts/": "Scripts utilitários",
        ".env": "Variáveis de ambiente",
        "requirements.txt": "Dependências Python"
    }
    
    print("\n📋 VERIFICAÇÃO DA ESTRUTURA:")
    for path, description in expected_structure.items():
        full_path = project_root / path
        status = "✅" if full_path.exists() else "❌"
        print(f"{status} {path:<25} - {description}")
    
    return project_root

def check_python_environment():
    """Verifica o ambiente Python"""
    print("\n🐍 DIAGNÓSTICO DO AMBIENTE PYTHON")
    print("=" * 50)
    
    print(f"Versão Python: {sys.version}")
    print(f"Executável: {sys.executable}")
    print(f"Python Path (primeiros 5):")
    for i, path in enumerate(sys.path[:5]):
        print(f"  {i+1}. {path}")
    
    # Verifica se está em ambiente virtual
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    print(f"Ambiente virtual: {'✅ Ativo' if in_venv else '❌ Não detectado'}")

def check_imports():
    """Testa importações"""
    print("\n📦 TESTE DE IMPORTAÇÕES")
    print("=" * 50)
    
    # Adiciona o diretório raiz ao path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"✅ Adicionado ao path: {project_root}")
    
    # Testa importações uma por uma
    imports_to_test = [
        ("api", "Pacote principal"),
        ("api.database", "Módulo database"),
        ("api.database.models", "Modelos"),
        ("api.database.crud", "CRUD operations"),
    ]
    
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name:<20} - {description}")
        except ImportError as e:
            print(f"❌ {module_name:<20} - {description} (Erro: {e})")

def check_environment_variables():
    """Verifica variáveis de ambiente"""
    print("\n🔧 VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    
    # Tenta carregar .env
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        print(f"✅ Arquivo .env encontrado: {env_file}")
        
        # Carrega e verifica variáveis
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASS']
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Mostra apenas os primeiros caracteres por segurança
                masked_value = value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"❌ {var}: Não configurado")
    else:
        print(f"❌ Arquivo .env não encontrado: {env_file}")

def generate_fix_commands():
    """Gera comandos para corrigir problemas"""
    print("\n🔧 COMANDOS PARA CORRIGIR PROBLEMAS")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    print("1. Criar arquivo api/__init__.py:")
    print(f"   touch {project_root}/api/__init__.py")
    
    print("\n2. Executar script do diretório correto:")
    print(f"   cd {project_root}")
    print("   python -m scripts.seed_data_complete")
    
    print("\n3. Verificar ambiente virtual:")
    print("   python -m venv .venv")
    print("   source .venv/bin/activate  # Linux/Mac")
    print("   .venv\\Scripts\\activate     # Windows")
    
    print("\n4. Instalar dependências:")
    print("   pip install -r requirements.txt")

def main():
    """Executa todos os diagnósticos"""
    print("🚀 DIAGNÓSTICO COMPLETO DO AMBIENTE")
    print("=" * 60)
    
    check_project_structure()
    check_python_environment()
    check_imports()
    check_environment_variables()
    generate_fix_commands()
    
    print("\n✅ Diagnóstico concluído!")

if __name__ == "__main__":
    main()
