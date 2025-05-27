from flask import Blueprint, request, jsonify
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError

from ..database.crud import (
    criar_empresa, listar_empresas, obter_empresa, 
    atualizar_empresa, deletar_empresa, empresa_para_dict
)

empresas_bp = Blueprint('empresas', __name__)

@empresas_bp.route('', methods=['GET'])
def listar():
    """Lista todas as empresas"""
    try:
        ativas_apenas = request.args.get('ativas', 'true').lower() == 'true'
        empresas = listar_empresas(ativas_apenas=ativas_apenas)
        return jsonify([empresa_para_dict(e) for e in empresas]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@empresas_bp.route('/<int:empresa_id>', methods=['GET'])
def obter(empresa_id: int):
    """Obtém uma empresa específica"""
    try:
        empresa = obter_empresa(empresa_id)
        if not empresa:
            return jsonify({"erro": "Empresa não encontrada"}), 404
        return jsonify(empresa_para_dict(empresa)), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@empresas_bp.route('', methods=['POST'])
def criar():
    """Cria uma nova empresa"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        empresa = criar_empresa(
            nome=dados["nome"],
            cnpj=dados.get("cnpj"),
            endereco=dados.get("endereco"),
            telefone=dados.get("telefone"),
            email=dados.get("email")
        )
        return jsonify(empresa_para_dict(empresa)), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except IntegrityError as ie:
        if "UNIQUE constraint failed: empresas.cnpj" in str(ie):
            return jsonify({"erro": "CNPJ já cadastrado"}), 409
        elif "UNIQUE constraint failed: empresas.email" in str(ie):
            return jsonify({"erro": "Email já cadastrado"}), 409
        else:
            return jsonify({"erro": "Erro de integridade dos dados"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@empresas_bp.route('/<int:empresa_id>', methods=['PUT'])
def atualizar(empresa_id: int):
    """Atualiza uma empresa"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        sucesso = atualizar_empresa(empresa_id, **dados)
        if not sucesso:
            return jsonify({"erro": "Empresa não encontrada"}), 404
        return jsonify({"status": "Empresa atualizada"}), 200
    except IntegrityError as ie:
        if "UNIQUE constraint failed: empresas.cnpj" in str(ie):
            return jsonify({"erro": "CNPJ já cadastrado"}), 409
        elif "UNIQUE constraint failed: empresas.email" in str(ie):
            return jsonify({"erro": "Email já cadastrado"}), 409
        else:
            return jsonify({"erro": "Erro de integridade dos dados"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@empresas_bp.route('/<int:empresa_id>', methods=['DELETE'])
def deletar(empresa_id: int):
    """Desativa uma empresa"""
    try:
        sucesso = deletar_empresa(empresa_id)
        if not sucesso:
            return jsonify({"erro": "Empresa não encontrada"}), 404
        return jsonify({"status": "Empresa desativada"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
