from flask import Blueprint, request, jsonify

from ..database.crud import eventos_para_calendario
from ..middleware.auth import jwt_required

calendario_bp = Blueprint('calendario', __name__)

@calendario_bp.route('', methods=['GET'])
@jwt_required
def obter_calendario():
    """Retorna eventos formatados para calendário"""
    try:
        grupo_id = request.args.get('grupo_id', type=int)
        apenas_aprovados = request.args.get('apenas_aprovados', 'true').lower() == 'true'
        
        eventos = eventos_para_calendario(
            grupo_id=grupo_id,
            apenas_aprovados=apenas_aprovados
        )
        return jsonify(eventos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@calendario_bp.route('/grupo/<int:grupo_id>', methods=['GET'])
@jwt_required
def calendario_grupo(grupo_id: int):
    """Retorna calendário específico de um grupo"""
    try:
        apenas_aprovados = request.args.get('apenas_aprovados', 'true').lower() == 'true'
        
        eventos = eventos_para_calendario(
            grupo_id=grupo_id,
            apenas_aprovados=apenas_aprovados
        )
        return jsonify({
            "grupo_id": grupo_id,
            "eventos": eventos,
            "total_eventos": len(eventos)
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
