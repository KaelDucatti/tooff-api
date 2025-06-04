from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import (
    criar_uf, listar_ufs, obter_uf
)
from ..middleware.auth import jwt_required, rh_required

ufs_bp = Blueprint('ufs', __name__)

@ufs_bp.route('', methods=['GET'])
@jwt_required
def listar():
    """Lista todas as UFs"""
    try:
        ufs = listar_ufs()
        return jsonify([{
            "cod_uf": uf.cod_uf,
            "uf": uf.uf
        } for uf in ufs]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@ufs_bp.route('/<string:uf>', methods=['GET'])
@jwt_required
def obter(uf: str):
    """Obtém uma UF específica"""
    try:
        estado = obter_uf(uf.upper())
        if not estado:
            return jsonify({"erro": "UF não encontrada"}), 404
        
        return jsonify({
            "cod_uf": estado.cod_uf,
            "uf": estado.uf
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@ufs_bp.route('', methods=['POST'])
@jwt_required
@rh_required
def criar():
    """Cria uma nova UF (apenas RH)"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        uf = criar_uf(
            cod_uf=dados["cod_uf"],
            uf=dados["uf"].upper()
        )
        
        return jsonify({
            "cod_uf": uf.cod_uf,
            "uf": uf.uf
        }), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
