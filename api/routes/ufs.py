from flask import Blueprint, jsonify
from ..database.crud import listar_ufs, obter_uf

ufs_bp = Blueprint('ufs', __name__)

@ufs_bp.route('/', methods=['GET'])
def listar():
    """Lista todas as UFs cadastradas"""
    try:
        ufs = listar_ufs()
        return jsonify([{"uf": uf.uf, "cod_uf": uf.cod_uf} for uf in ufs]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@ufs_bp.route('/<string:uf>', methods=['GET'])
def obter(uf):
    """Obtém uma UF específica pelo código"""
    try:
        estado = obter_uf(uf)
        if not estado:
            return jsonify({"erro": "UF não encontrada"}), 404
        
        return jsonify({"uf": estado.uf, "cod_uf": estado.cod_uf}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
