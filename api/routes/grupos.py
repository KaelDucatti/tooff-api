from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..database.crud import (
    criar_grupo, listar_grupos, obter_grupo, 
    atualizar_grupo, deletar_grupo, grupo_para_dict,
    estatisticas_grupo
)
from ..middleware.auth import (
    jwt_required, requer_permissao_grupo, filtrar_por_escopo_usuario,
    extrair_usuario_id_do_token, verificar_permissao_empresa
)
from ..database.models import TipoUsuario

grupos_bp = Blueprint('grupos', __name__)

@grupos_bp.route('', methods=['GET'])
@jwt_required
def listar():
    """Lista grupos com base no escopo do usuário"""
    try:
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        ativos_apenas = request.args.get('ativos', 'true').lower() == 'true'
        
        # Aplica filtros baseados no escopo do usuário
        filtros = filtrar_por_escopo_usuario(usuario_id)
        
        if filtros and 'empresa_id' in filtros:
            # RH vê grupos da sua empresa
            grupos = listar_grupos(empresa_id=filtros['empresa_id'], ativos_apenas=ativos_apenas)
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
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Verifica se o usuário pode criar grupos na empresa especificada
        empresa_id = dados["empresa_id"]
        if not verificar_permissao_empresa(usuario_id, empresa_id):
            return jsonify({"erro": "Sem permissão para criar grupos nesta empresa"}), 403
        
        # Apenas RH pode criar grupos
        from ..database.crud import obter_usuario
        usuario = obter_usuario(usuario_id)
        if not usuario or usuario.tipo_usuario != TipoUsuario.RH:
            return jsonify({"erro": "Apenas RH pode criar grupos"}), 403
        
        grupo = criar_grupo(
            nome=dados["nome"],
            empresa_id=empresa_id,
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
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
            
        from ..database.crud import obter_usuario
        usuario = obter_usuario(usuario_id)
        if not usuario or usuario.tipo_usuario != TipoUsuario.RH:
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
        usuario_id = extrair_usuario_id_do_token()
        if not usuario_id:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
            
        from ..database.crud import obter_usuario
        usuario = obter_usuario(usuario_id)
        if not usuario or usuario.tipo_usuario != TipoUsuario.RH:
            return jsonify({"erro": "Apenas RH pode desativar grupos"}), 403
        
        sucesso = deletar_grupo(grupo_id)
        if not sucesso:
            return jsonify({"erro": "Grupo não encontrado"}), 404
        return jsonify({"status": "Grupo desativado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@grupos_bp.route('/<int:grupo_id>/estatisticas', methods=['GET'])
@jwt_required
@requer_permissao_grupo
def obter_estatisticas(grupo_id: int):
    """Obtém estatísticas de um grupo"""
    try:
        stats = estatisticas_grupo(grupo_id)
        if not stats:
            return jsonify({"erro": "Grupo não encontrado"}), 404
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
