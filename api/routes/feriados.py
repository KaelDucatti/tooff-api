from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import (
    criar_feriado_nacional, criar_feriado_estadual,
    listar_feriados_nacionais, listar_feriados_estaduais
)
from ..middleware.auth import jwt_required, rh_required

feriados_bp = Blueprint('feriados', __name__)

@feriados_bp.route('/nacionais', methods=['GET'])
@jwt_required
def listar_nacionais():
    """Lista feriados nacionais"""
    try:
        uf = request.args.get('uf')
        feriados = listar_feriados_nacionais(uf)
        return jsonify([{
            "data_feriado": f.data_feriado.isoformat(),
            "uf": f.uf,
            "descricao_feriado": f.descricao_feriado
        } for f in feriados]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@feriados_bp.route('/estaduais', methods=['GET'])
@jwt_required
def listar_estaduais():
    """Lista feriados estaduais"""
    try:
        uf = request.args.get('uf')
        feriados = listar_feriados_estaduais(uf)
        return jsonify([{
            "data_feriado": f.data_feriado.isoformat(),
            "uf": f.uf,
            "descricao_feriado": f.descricao_feriado
        } for f in feriados]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@feriados_bp.route('', methods=['GET'])
def listar_todos():
    """Lista todos os feriados (endpoint público)"""
    try:
        uf = request.args.get('uf')
        
        # Combina feriados nacionais e estaduais
        feriados_nacionais = listar_feriados_nacionais(uf)
        feriados_estaduais = listar_feriados_estaduais(uf)
        
        todos_feriados = []
        
        # Adiciona feriados nacionais
        for f in feriados_nacionais:
            todos_feriados.append({
                "data_feriado": f.data_feriado.isoformat(),
                "uf": f.uf,
                "descricao_feriado": f.descricao_feriado,
                "tipo": "nacional"
            })
        
        # Adiciona feriados estaduais
        for f in feriados_estaduais:
            todos_feriados.append({
                "data_feriado": f.data_feriado.isoformat(),
                "uf": f.uf,
                "descricao_feriado": f.descricao_feriado,
                "tipo": "estadual"
            })
        
        return jsonify(todos_feriados), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@feriados_bp.route('/nacionais', methods=['POST'])
@jwt_required
@rh_required
def criar_nacional():
    """Cria um novo feriado nacional (apenas RH)"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        feriado = criar_feriado_nacional(
            data_feriado=dados["data_feriado"],
            uf=dados["uf"].upper(),
            descricao_feriado=dados["descricao_feriado"]
        )
        
        return jsonify({
            "data_feriado": feriado.data_feriado.isoformat(),
            "uf": feriado.uf,
            "descricao_feriado": feriado.descricao_feriado
        }), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@feriados_bp.route('/estaduais', methods=['POST'])
@jwt_required
@rh_required
def criar_estadual():
    """Cria um novo feriado estadual (apenas RH)"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        feriado = criar_feriado_estadual(
            data_feriado=dados["data_feriado"],
            uf=dados["uf"].upper(),
            descricao_feriado=dados["descricao_feriado"]
        )
        
        return jsonify({
            "data_feriado": feriado.data_feriado.isoformat(),
            "uf": feriado.uf,
            "descricao_feriado": feriado.descricao_feriado
        }), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
