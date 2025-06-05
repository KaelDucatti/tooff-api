from flask import Blueprint, request, jsonify
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError

from ..database.crud import (
    obter_empresa, atualizar_empresa, empresa_para_dict,
    obter_usuario, obter_grupo
)
from ..middleware.auth import (
    jwt_required, extrair_usuario_cpf_do_token
)

empresas_bp = Blueprint('empresas', __name__)

def get_empresa_do_usuario_rh(usuario_cpf: int):
    """Retorna a empresa do usuário RH baseado no seu grupo"""
    usuario = obter_usuario(usuario_cpf)
    if not usuario or usuario.tipo_usuario != 'rh':
        return None
    
    if not usuario.grupo_id:
        return None
    
    grupo = obter_grupo(usuario.grupo_id)
    if not grupo:
        return None
    
    return obter_empresa(grupo.cnpj_empresa)

@empresas_bp.route('', methods=['GET'])
@jwt_required
def listar():
    """RH pode apenas visualizar sua própria empresa"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        usuario = obter_usuario(usuario_cpf)
        if not usuario or usuario.tipo_usuario != 'rh':
            return jsonify({"erro": "Apenas RH pode acessar dados de empresas"}), 403
        
        # RH só vê sua própria empresa
        empresa = get_empresa_do_usuario_rh(usuario_cpf)
        if empresa:
            return jsonify([empresa_para_dict(empresa)]), 200
        else:
            return jsonify([]), 200
            
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@empresas_bp.route('/<int:cnpj>', methods=['GET'])
@jwt_required
def obter(cnpj: int):
    """RH pode apenas visualizar sua própria empresa"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        usuario = obter_usuario(usuario_cpf)
        if not usuario or usuario.tipo_usuario != 'rh':
            return jsonify({"erro": "Apenas RH pode acessar dados de empresas"}), 403
        
        # Verifica se é a empresa do RH
        empresa_rh = get_empresa_do_usuario_rh(usuario_cpf)
        if not empresa_rh or empresa_rh.cnpj != cnpj:
            return jsonify({"erro": "RH só pode acessar dados da própria empresa"}), 403
        
        empresa = obter_empresa(cnpj)
        if not empresa:
            return jsonify({"erro": "Empresa não encontrada"}), 404
            
        return jsonify(empresa_para_dict(empresa)), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@empresas_bp.route('', methods=['POST'])
@jwt_required
def criar():
    """RH NÃO pode criar empresas"""
    return jsonify({"erro": "RH não tem permissão para criar empresas"}), 403

@empresas_bp.route('/<int:cnpj>', methods=['PUT'])
@jwt_required
def atualizar(cnpj: int):
    """RH pode apenas atualizar sua própria empresa"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
            
        usuario = obter_usuario(usuario_cpf)
        if not usuario or usuario.tipo_usuario != 'rh':
            return jsonify({"erro": "Apenas RH pode atualizar dados de empresas"}), 403
        
        # Verifica se é a empresa do RH
        empresa_rh = get_empresa_do_usuario_rh(usuario_cpf)
        if not empresa_rh or empresa_rh.cnpj != cnpj:
            return jsonify({"erro": "RH só pode atualizar dados da própria empresa"}), 403
        
        # RH não pode alterar CNPJ ou ID da empresa
        if 'cnpj' in dados:
            return jsonify({"erro": "RH não pode alterar o CNPJ da empresa"}), 403
        if 'id' in dados:
            return jsonify({"erro": "RH não pode alterar o ID da empresa"}), 403
        
        sucesso = atualizar_empresa(cnpj, **dados)
        if not sucesso:
            return jsonify({"erro": "Empresa não encontrada"}), 404
        return jsonify({"status": "Empresa atualizada com sucesso"}), 200
    except IntegrityError as ie:
        if "Duplicate entry" in str(ie) and "email" in str(ie):
            return jsonify({"erro": "Email já cadastrado"}), 409
        else:
            return jsonify({"erro": "Erro de integridade dos dados"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@empresas_bp.route('/<int:cnpj>', methods=['DELETE'])
@jwt_required
def deletar(cnpj: int):
    """RH NÃO pode deletar empresas"""
    return jsonify({"erro": "RH não tem permissão para deletar empresas"}), 403
