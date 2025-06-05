"""
Script para corrigir problemas de integridade encontrados
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from api.database.models import init_db, get_session, Usuario, Empresa, Grupo, Evento
from api.validation.integrity_checker import CPFCNPJIntegrityChecker
from api.validation.cpf_cnpj_validator import formatar_cpf, formatar_cnpj

# Adiciona o diretório pai ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Carrega variáveis de ambiente
load_dotenv()


class IntegrityFixer:
    """Classe para corrigir problemas de integridade"""
    
    def __init__(self):
        self.fixes_applied = []
        self.fixes_failed = []
    
    def fix_orphaned_usuarios(self, orphaned_usuarios: list) -> None:
        """Corrige usuários órfãos desativando-os"""
        with get_session() as session:
            for usuario_data in orphaned_usuarios:
                try:
                    usuario = session.get(Usuario, usuario_data['cpf'])
                    if usuario:
                        usuario.ativo = False
                        session.commit()
                        self.fixes_applied.append(
                            f"Usuário órfão desativado: {formatar_cpf(usuario.cpf)} - {usuario.nome}"
                        )
                except Exception as e:
                    self.fixes_failed.append(
                        f"Falha ao desativar usuário {formatar_cpf(usuario_data['cpf'])}: {e}"
                    )
    
    def fix_orphaned_eventos(self, orphaned_eventos: list) -> None:
        """Remove eventos órfãos"""
        with get_session() as session:
            for evento_data in orphaned_eventos:
                try:
                    evento = session.get(Evento, evento_data['id'])
                    if evento:
                        session.delete(evento)
                        session.commit()
                        self.fixes_applied.append(
                            f"Evento órfão removido: ID {evento.id} - CPF {formatar_cpf(evento_data['cpf_usuario'])}"
                        )
                except Exception as e:
                    self.fixes_failed.append(
                        f"Falha ao remover evento {evento_data['id']}: {e}"
                    )
    
    def fix_orphaned_grupos(self, orphaned_grupos: list) -> None:
        """Desativa grupos órfãos"""
        with get_session() as session:
            for grupo_data in orphaned_grupos:
                try:
                    grupo = session.get(Grupo, grupo_data['id'])
                    if grupo:
                        grupo.ativo = False
                        session.commit()
                        self.fixes_applied.append(
                            f"Grupo órfão desativado: {grupo.nome} - CNPJ {formatar_cnpj(grupo_data['cnpj_empresa'])}"
                        )
                except Exception as e:
                    self.fixes_failed.append(
                        f"Falha ao desativar grupo {grupo_data['id']}: {e}"
                    )
    
    def fix_invalid_cpf_cnpj(self) -> None:
        """Corrige CPF/CNPJ inválidos"""
        with get_session() as session:
            try:
                # Busca usuários com CPF inválido
                usuarios = session.query(Usuario).all()
                for usuario in usuarios:
                    # Aqui você pode implementar lógica para corrigir CPFs
                    # Por exemplo, remover caracteres especiais, validar formato, etc.
                    pass
                
                # Busca empresas com CNPJ inválido
                empresas = session.query(Empresa).all()
                for empresa in empresas:
                    # Aqui você pode implementar lógica para corrigir CNPJs
                    pass
                    
            except Exception as e:
                self.fixes_failed.append(f"Erro ao corrigir CPF/CNPJ: {e}")
    
    def apply_fixes(self, report) -> None:
        """Aplica correções baseadas no relatório"""
        print("🔧 Iniciando correções automáticas...")
        
        for error in report.errors:
            if error['category'] == 'ORPHANED_USUARIOS':
                print("👤 Corrigindo usuários órfãos...")
                self.fix_orphaned_usuarios(error['details']['orphaned_usuarios'])
            
            elif error['category'] == 'ORPHANED_EVENTOS':
                print("📅 Corrigindo eventos órfãos...")
                self.fix_orphaned_eventos(error['details']['orphaned_eventos'])
            
            elif error['category'] == 'ORPHANED_GRUPOS':
                print("👥 Corrigindo grupos órfãos...")
                self.fix_orphaned_grupos(error['details']['orphaned_grupos'])
        
        # Relatório de correções
        print(f"\n✅ Correções aplicadas: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"   ✓ {fix}")
        
        if self.fixes_failed:
            print(f"\n❌ Correções falharam: {len(self.fixes_failed)}")
            for fail in self.fixes_failed:
                print(f"   ✗ {fail}")

def main():
    """Função principal do script de correção"""
    print("🔧 Iniciando correção de problemas de integridade...")
    
    # Inicializa o banco de dados
    try:
        init_db("sqlite:///database/tooff_app.db")
        print("✅ Conexão com banco estabelecida")
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
        return 1
    
    # Executa verificação primeiro
    try:
        checker = CPFCNPJIntegrityChecker()
        report = checker.run_all_checks()
        
        if not report.errors:
            print("✅ Nenhum problema de integridade encontrado!")
            return 0
        
        print(f"🔍 Encontrados {len(report.errors)} problema(s) de integridade")
        
        # Pergunta se deve aplicar correções
        response = input("Deseja aplicar correções automáticas? (s/N): ")
        if response.lower() not in ['s', 'sim', 'y', 'yes']:
            print("❌ Correções canceladas pelo usuário")
            return 0
        
        # Aplica correções
        fixer = IntegrityFixer()
        fixer.apply_fixes(report)
        
        # Executa verificação novamente
        print("\n🔍 Executando nova verificação...")
        new_checker = CPFCNPJIntegrityChecker()
        new_report = new_checker.run_all_checks()
        
        if new_report.errors:
            print(f"⚠️  Ainda existem {len(new_report.errors)} problema(s) que precisam de correção manual")
            return 1
        else:
            print("🎉 Todos os problemas de integridade foram corrigidos!")
            return 0
            
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
