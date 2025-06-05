from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import (
    criar_grupo, listar_grupos, obter_grupo, 
    atualizar_grupo, deletar_grupo, grupo_para_dict
)
from ..middleware.auth import (
    jwt_required, requer_permissao_grupo, filtrar_por_escopo_usuario,
    extrair_usuario_cpf_do_token, verificar_permissao_empresa
)

grupos_bp = Blueprint('grupos', __name__)

@grupos_bp.route('', methods=['GET'])
@jwt_required
def listar():
    """Lista grupos com base no escopo do usuário"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        ativos_apenas = request.args.get('ativos', 'true').lower() == 'true'
        
        # Aplica filtros baseados no escopo do usuário
        filtros = filtrar_por_escopo_usuario(usuario_cpf)
        
        if filtros and 'cnpj_empresa' in filtros:
            # RH vê grupos da sua empresa
            grupos = listar_grupos(cnpj_empresa=filtros['cnpj_empresa'], ativos_apenas=ativos_apenas)
        elif filtros and 'grupo_id' in filtros:
            # Gestores e usuários comuns veem apenas seu grupo
            grupo_id = filtros['grupo_id']
            if grupo_id is not None:
                grupo = obter_grupo(grupo_id)
                grupos = [grupo] if grupo and grupo.ativo else []
            else:
                grupos = []
        else:
            grupos = []
        
        return jsonify([grupo_para_dict(g) for g in grupos]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@grupos_bp.route('/<int:grupo_id>', methods=['GET'])
@jwt_required
@requer_permissao_grupo
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
@jwt_required
def criar():
    """Cria um novo grupo"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Apenas RH pode criar grupos
        from ..database.crud import obter_usuario
        usuario = obter_usuario(usuario_cpf)
        if not usuario or usuario.tipo_usuario != 'rh':
            return jsonify({"erro": "Apenas RH pode criar grupos"}), 403
        
        # Verifica se o usuário pode criar grupos na empresa especificada
        cnpj_empresa = dados["cnpj_empresa"]

        # RH pode criar grupos apenas na sua própria empresa
        if usuario.grupo_id:
            from ..database.crud import obter_grupo
            grupo_rh = obter_grupo(usuario.grupo_id)
            if not grupo_rh or grupo_rh.cnpj_empresa != cnpj_empresa:
                return jsonify({"erro": "RH só pode criar grupos na sua própria empresa"}), 403
        
        grupo = criar_grupo(
            nome=dados["nome"],
            cnpj_empresa=cnpj_empresa,
            telefone=dados["telefone"],
            descricao=dados.get("descricao")
        )
        return jsonify(grupo_para_dict(grupo)), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@grupos_bp.route('/<int:grupo_id>', methods=['PUT'])
@jwt_required
@requer_permissao_grupo
def atualizar(grupo_id: int):
    """Atualiza um grupo"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
            
        from ..database.crud import obter_usuario
        usuario = obter_usuario(usuario_cpf)
        if not usuario or usuario.tipo_usuario != 'rh':
            return jsonify({"erro": "Apenas RH pode atualizar grupos"}), 403
        
        sucesso = atualizar_grupo(grupo_id, **dados)
        if not sucesso:
            return jsonify({"erro": "Grupo não encontrado"}), 404
        return jsonify({"status": "Grupo atualizado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@grupos_bp.route('/<int:grupo_id>', methods=['DELETE'])
@jwt_required
@requer_permissao_grupo
def deletar(grupo_id: int):
    """Desativa um grupo"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
            
        from ..database.crud import obter_usuario
        usuario = obter_usuario(usuario_cpf)
        if not usuario or usuario.tipo_usuario != 'rh':
            return jsonify({"erro": "Apenas RH pode desativar grupos"}), 403
        
        sucesso = deletar_grupo(grupo_id)
        if not sucesso:
            return jsonify({"erro": "Grupo não encontrado"}), 404
        return jsonify({"status": "Grupo desativado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
