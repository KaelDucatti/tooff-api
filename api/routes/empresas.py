from flask import Blueprint, request, jsonify
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError

from ..database.crud import (
    criar_empresa, obter_empresa, 
    atualizar_empresa, deletar_empresa, empresa_para_dict
)
from ..middleware.auth import (
    jwt_required, get_current_user_id, get_current_user_tipo,
    requer_permissao_empresa, filtrar_por_escopo_usuario, 
    extrair_usuario_id_do_token
)
from ..database.models import TipoUsuario

empresas_bp = Blueprint('empresas', __name__)

@empresas_bp.route('', methods=['GET'])
@jwt_required
def listar():
    """Lista empresas com base no escopo do usuário"""
    try:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Aplica filtros baseados no escopo do usuário
        filtros = filtrar_por_escopo_usuario(usuario_id)
        if filtros and 'empresa_id' in filtros:
            empresa_id = filtros['empresa_id']
            if empresa_id is not None:
                # RH só vê sua própria empresa
                empresa = obter_empresa(empresa_id)
                if empresa:
                    return jsonify([empresa_para_dict(empresa)]), 200
            return jsonify([]), 200
        elif filtros and 'grupo_id' in filtros:
            # Gestores e usuários comuns não têm acesso direto a empresas
            return jsonify({"erro": "Sem permissão para listar empresas"}), 403
        
        # Fallback (não deveria chegar aqui)
        return jsonify([]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@empresas_bp.route('/<int:empresa_id>', methods=['GET'])
@jwt_required
@requer_permissao_empresa
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
@jwt_required
def criar():
    """Cria uma nova empresa (apenas RH da mesma empresa)"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Apenas RH pode criar empresas, e apenas na sua própria empresa
        from ..database.crud import obter_usuario
        usuario = obter_usuario(usuario_id)
        if not usuario or usuario.tipo_usuario != TipoUsuario.RH:
            return jsonify({"erro": "Apenas RH pode criar empresas"}), 403
        
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
@jwt_required
@requer_permissao_empresa
def atualizar(empresa_id: int):
    """Atualiza uma empresa"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
            
        from ..database.crud import obter_usuario
        usuario = obter_usuario(usuario_id)
        if not usuario or usuario.tipo_usuario != TipoUsuario.RH:
            return jsonify({"erro": "Apenas RH pode atualizar empresas"}), 403
        
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
@jwt_required
@requer_permissao_empresa
def deletar(empresa_id: int):
    """Desativa uma empresa"""
    try:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
            
        from ..database.crud import obter_usuario
        usuario = obter_usuario(usuario_id)
        if not usuario or usuario.tipo_usuario != TipoUsuario.RH:
            return jsonify({"erro": "Apenas RH pode desativar empresas"}), 403
        
        sucesso = deletar_empresa(empresa_id)
        if not sucesso:
            return jsonify({"erro": "Empresa não encontrada"}), 404
        return jsonify({"status": "Empresa desativada"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
