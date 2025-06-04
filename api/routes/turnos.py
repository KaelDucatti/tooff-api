from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import (
    criar_turno, listar_turnos, obter_turno
)
from ..middleware.auth import jwt_required, rh_required

turnos_bp = Blueprint('turnos', __name__)

@turnos_bp.route('', methods=['GET'])
@jwt_required
def listar():
    """Lista todos os turnos"""
    try:
        turnos = listar_turnos()
        return jsonify([{
            "id": t.id,
            "descricao_ausencia": t.descricao_ausencia
        } for t in turnos]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@turnos_bp.route('/<int:turno_id>', methods=['GET'])
@jwt_required
def obter(turno_id: int):
    """Obtém um turno específico"""
    try:
        turno = obter_turno(turno_id)
        if not turno:
            return jsonify({"erro": "Turno não encontrado"}), 404
        
        return jsonify({
            "id": turno.id,
            "descricao_ausencia": turno.descricao_ausencia
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@turnos_bp.route('', methods=['POST'])
@jwt_required
@rh_required
def criar():
    """Cria um novo turno (apenas RH)"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        turno = criar_turno(
            descricao_ausencia=dados["descricao_ausencia"]
        )
        
        return jsonify({
            "id": turno.id,
            "descricao_ausencia": turno.descricao_ausencia
        }), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
