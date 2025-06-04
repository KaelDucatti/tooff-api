from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import (
    criar_tipo_ausencia, listar_tipos_ausencia, obter_tipo_ausencia
)
from ..middleware.auth import jwt_required, rh_required

tipos_ausencia_bp = Blueprint('tipos_ausencia', __name__)

@tipos_ausencia_bp.route('', methods=['GET'])
@jwt_required
def listar():
    """Lista todos os tipos de ausência"""
    try:
        tipos = listar_tipos_ausencia()
        return jsonify([{
            "id_tipo_ausencia": t.id_tipo_ausencia,
            "descricao_ausencia": t.descricao_ausencia,
            "usa_turno": t.usa_turno
        } for t in tipos]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@tipos_ausencia_bp.route('/<int:id_tipo>', methods=['GET'])
@jwt_required
def obter(id_tipo: int):
    """Obtém um tipo de ausência específico"""
    try:
        tipo = obter_tipo_ausencia(id_tipo)
        if not tipo:
            return jsonify({"erro": "Tipo de ausência não encontrado"}), 404
        
        return jsonify({
            "id_tipo_ausencia": tipo.id_tipo_ausencia,
            "descricao_ausencia": tipo.descricao_ausencia,
            "usa_turno": tipo.usa_turno
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@tipos_ausencia_bp.route('', methods=['POST'])
@jwt_required
@rh_required
def criar():
    """Cria um novo tipo de ausência (apenas RH)"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        tipo = criar_tipo_ausencia(
            descricao_ausencia=dados["descricao_ausencia"],
            usa_turno=dados.get("usa_turno", False)
        )
        
        return jsonify({
            "id_tipo_ausencia": tipo.id_tipo_ausencia,
            "descricao_ausencia": tipo.descricao_ausencia,
            "usa_turno": tipo.usa_turno
        }), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
