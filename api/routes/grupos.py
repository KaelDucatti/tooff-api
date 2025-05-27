from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import (
    criar_grupo, listar_grupos, obter_grupo, 
    atualizar_grupo, deletar_grupo, grupo_para_dict,
    estatisticas_grupo
)

grupos_bp = Blueprint('grupos', __name__)

@grupos_bp.route('', methods=['GET'])
def listar():
    """Lista todos os grupos"""
    try:
        empresa_id = request.args.get('empresa_id', type=int)
        ativos_apenas = request.args.get('ativos', 'true').lower() == 'true'
        
        grupos = listar_grupos(empresa_id=empresa_id, ativos_apenas=ativos_apenas)
        return jsonify([grupo_para_dict(g) for g in grupos]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@grupos_bp.route('/<int:grupo_id>', methods=['GET'])
def obter(grupo_id: int):
    """Obtém um grupo específico"""
    try:
        grupo = obter_grupo(grupo_id)
        if not grupo:
            return jsonify({"erro": "Grupo não encontrado"}), 404
        return jsonify(grupo_para_dict(grupo)), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@grupos_bp.route('', methods=['POST'])
def criar():
    """Cria um novo grupo"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        grupo = criar_grupo(
            nome=dados["nome"],
            empresa_id=dados["empresa_id"],
            descricao=dados.get("descricao")
        )
        return jsonify(grupo_para_dict(grupo)), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@grupos_bp.route('/<int:grupo_id>', methods=['PUT'])
def atualizar(grupo_id: int):
    """Atualiza um grupo"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        sucesso = atualizar_grupo(grupo_id, **dados)
        if not sucesso:
            return jsonify({"erro": "Grupo não encontrado"}), 404
        return jsonify({"status": "Grupo atualizado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@grupos_bp.route('/<int:grupo_id>', methods=['DELETE'])
def deletar(grupo_id: int):
    """Desativa um grupo"""
    try:
        sucesso = deletar_grupo(grupo_id)
        if not sucesso:
            return jsonify({"erro": "Grupo não encontrado"}), 404
        return jsonify({"status": "Grupo desativado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@grupos_bp.route('/<int:grupo_id>/estatisticas', methods=['GET'])
def obter_estatisticas(grupo_id: int):
    """Obtém estatísticas de um grupo"""
    try:
        stats = estatisticas_grupo(grupo_id)
        if not stats:
            return jsonify({"erro": "Grupo não encontrado"}), 404
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
