"""
Script para validar integridade de CPF/CNPJ no banco de dados
"""
import sys
from pathlib import Path
import argparse
from dotenv import load_dotenv
from api.database.models import init_db
from api.validation.integrity_checker import CPFCNPJIntegrityChecker
from api.validation.report_generator import ReportGenerator

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))


def main():
    """Função principal do script de validação"""
    parser = argparse.ArgumentParser(description='Validador de integridade CPF/CNPJ')
    parser.add_argument('--database', '-d', 
                       help='URL do banco de dados (padrão: SQLite local)',
                       default="sqlite:///database/tooff_app.db")
    parser.add_argument('--output', '-o', 
                       help='Arquivo de saída para relatório JSON')
    parser.add_argument('--quiet', '-q', 
                       action='store_true',
                       help='Modo silencioso (apenas erros)')
    
    args = parser.parse_args()
    
    print("🚀 Iniciando validação de integridade CPF/CNPJ...")
    print(f"📊 Banco de dados: {args.database}")
    
    # Inicializa o banco de dados
    try:
        init_db(args.database)
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
        return 1
    
    # Executa as verificações
    checker = CPFCNPJIntegrityChecker()
    report = checker.run_all_checks()
    
    # Gera relatório no console
    if not args.quiet:
        console_report = ReportGenerator.generate_console_report(report)
        print("\n" + console_report)
    
    # Salva relatório em arquivo se solicitado
    if args.output:
        filename = ReportGenerator.save_report_to_file(report, args.output)
        print(f"\n💾 Relatório salvo em: {filename}")
    
    # Retorna código de saída baseado nos resultados
    if report.errors:
        print(f"\n❌ Validação concluída com {len(report.errors)} erro(s)")
        return 1
    elif report.warnings:
        print(f"\n⚠️  Validação concluída com {len(report.warnings)} aviso(s)")
        return 0
    else:
        print("\n✅ Validação concluída com sucesso - nenhum problema encontrado!")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
