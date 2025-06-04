"""
Endpoints para validação de integridade
"""
from flask import Blueprint, jsonify
from ..middleware.auth import jwt_required, rh_required
from ..validation.integrity_checker import CPFCNPJIntegrityChecker
from ..validation.report_generator import ReportGenerator

validation_bp = Blueprint('validation', __name__)

@validation_bp.route('/integrity-check', methods=['GET'])
@jwt_required
@rh_required
def check_integrity():
    """Endpoint para verificar integridade (apenas RH)"""
    try:
        checker = CPFCNPJIntegrityChecker()
        report = checker.run_all_checks()
        
        return jsonify({
            "summary": report.get_summary(),
            "errors": report.errors,
            "warnings": report.warnings,
            "info": report.info,
            "statistics": report.statistics
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@validation_bp.route('/integrity-report', methods=['GET'])
@jwt_required
@rh_required
def get_integrity_report():
    """Endpoint para obter relatório de integridade formatado"""
    try:
        checker = CPFCNPJIntegrityChecker()
        report = checker.run_all_checks()
        
        console_report = ReportGenerator.generate_console_report(report)
        
        return jsonify({
            "report": console_report,
            "summary": report.get_summary()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
