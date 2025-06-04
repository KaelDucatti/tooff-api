"""
Gerador de relatórios de integridade
"""
import json
from typing import Optional
from datetime import datetime
from .integrity_checker import IntegrityReport

class ReportGenerator:
    """Gerador de relatórios em diferentes formatos"""
    
    @staticmethod
    def generate_console_report(report: IntegrityReport) -> str:
        """Gera relatório para console"""
        output = []
        output.append("=" * 80)
        output.append("🔍 RELATÓRIO DE INTEGRIDADE CPF/CNPJ")
        output.append("=" * 80)
        output.append(f"📅 Data/Hora: {report.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        output.append("")
        
        # Resumo
        summary = report.get_summary()
        output.append("📊 RESUMO:")
        output.append(f"   ❌ Erros: {summary['total_errors']}")
        output.append(f"   ⚠️  Avisos: {summary['total_warnings']}")
        output.append(f"   ℹ️  Informações: {summary['total_info']}")
        output.append("")
        
        # Estatísticas
        if report.statistics:
            output.append("📈 ESTATÍSTICAS DO BANCO:")
            stats = report.statistics
            output.append(f"   🏢 Empresas: {stats.get('total_empresas', 0)} (Ativas: {stats.get('empresas_ativas', 0)}, Inativas: {stats.get('empresas_inativas', 0)})")
            output.append(f"   👥 Grupos: {stats.get('total_grupos', 0)}")
            output.append(f"   👤 Usuários: {stats.get('total_usuarios', 0)} (Ativos: {stats.get('usuarios_ativos', 0)}, Inativos: {stats.get('usuarios_inativos', 0)})")
            output.append(f"   📅 Eventos: {stats.get('total_eventos', 0)}")
            output.append(f"   🌎 UFs: {stats.get('total_ufs', 0)}")
            
            if 'usuarios_por_tipo' in stats:
                output.append("   👤 Usuários por tipo:")
                for tipo, count in stats['usuarios_por_tipo'].items():
                    output.append(f"      - {tipo}: {count}")
            
            if 'eventos_por_status' in stats:
                output.append("   📅 Eventos por status:")
                for status, count in stats['eventos_por_status'].items():
                    output.append(f"      - {status}: {count}")
            output.append("")
        
        # Erros
        if report.errors:
            output.append("❌ ERROS ENCONTRADOS:")
            for i, error in enumerate(report.errors, 1):
                output.append(f"   {i}. [{error['category']}] {error['message']}")
                if error['details']:
                    # Mostra apenas um resumo dos detalhes para não poluir o console
                    details = error['details']
                    if 'invalid_cpfs' in details:
                        output.append(f"      CPFs inválidos: {len(details['invalid_cpfs'])}")
                    elif 'invalid_cnpjs' in details:
                        output.append(f"      CNPJs inválidos: {len(details['invalid_cnpjs'])}")
                    elif 'duplicates' in details:
                        output.append(f"      Duplicatas: {len(details['duplicates'])}")
                    elif 'orphaned_usuarios' in details:
                        output.append(f"      Usuários órfãos: {len(details['orphaned_usuarios'])}")
                    elif 'orphaned_grupos' in details:
                        output.append(f"      Grupos órfãos: {len(details['orphaned_grupos'])}")
                    elif 'orphaned_eventos' in details:
                        output.append(f"      Eventos órfãos: {len(details['orphaned_eventos'])}")
            output.append("")
        
        # Avisos
        if report.warnings:
            output.append("⚠️  AVISOS:")
            for i, warning in enumerate(report.warnings, 1):
                output.append(f"   {i}. [{warning['category']}] {warning['message']}")
            output.append("")
        
        # Informações positivas
        if report.info:
            output.append("✅ VERIFICAÇÕES APROVADAS:")
            for info in report.info:
                output.append(f"   ✓ [{info['category']}] {info['message']}")
            output.append("")
        
        # Conclusão
        if report.errors:
            output.append("🚨 AÇÃO NECESSÁRIA: Foram encontrados erros que precisam ser corrigidos!")
        elif report.warnings:
            output.append("⚠️  ATENÇÃO: Foram encontrados avisos que devem ser revisados.")
        else:
            output.append("🎉 PARABÉNS: Nenhum problema de integridade encontrado!")
        
        output.append("=" * 80)
        return "\n".join(output)
    
    @staticmethod
    def generate_json_report(report: IntegrityReport) -> str:
        """Gera relatório em formato JSON"""
        report_data = {
            "summary": report.get_summary(),
            "errors": report.errors,
            "warnings": report.warnings,
            "info": report.info,
            "statistics": report.statistics
        }
        return json.dumps(report_data, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def save_report_to_file(report: IntegrityReport, filename: Optional[str] = None) -> str:
        """Salva relatório em arquivo"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integrity_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(ReportGenerator.generate_json_report(report))
        
        return filename
