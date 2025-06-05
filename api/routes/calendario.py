from flask import Blueprint, request, jsonify

from ..database.crud import eventos_para_calendario
from ..middleware.auth import jwt_required, filtrar_por_escopo_usuario, extrair_usuario_cpf_do_token

calendario_bp = Blueprint('calendario', __name__)

@calendario_bp.route('', methods=['GET'])
@jwt_required
def obter_calendario():
    """Retorna eventos formatados para calendário"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        apenas_aprovados = request.args.get('apenas_aprovados', 'true').lower() == 'true'
        
        # Aplica filtros baseados no escopo do usuário
        filtros = filtrar_por_escopo_usuario(usuario_cpf)
        
        grupo_id = None
        if filtros and 'grupo_id' in filtros:
            grupo_id = filtros['grupo_id']
        elif request.args.get('grupo_id'):
            grupo_id = request.args.get('grupo_id', type=int)
        
        eventos = eventos_para_calendario(
            grupo_id=grupo_id,
            apenas_aprovados=apenas_aprovados
        )
        
        return jsonify(eventos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@calendario_bp.route('/grupo/<int:grupo_id>', methods=['GET'])
@jwt_required
def calendario_grupo(grupo_id: int):
    """Retorna calendário específico de um grupo"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Verificar se o usuário tem permissão para ver este grupo
        filtros = filtrar_por_escopo_usuario(usuario_cpf)
        if filtros and 'grupo_id' in filtros and filtros['grupo_id'] != grupo_id:
            return jsonify({"erro": "Sem permissão para acessar este grupo"}), 403
        
        apenas_aprovados = request.args.get('apenas_aprovados', 'true').lower() == 'true'
        
        eventos = eventos_para_calendario(
            grupo_id=grupo_id,
            apenas_aprovados=apenas_aprovados
        )
        
        return jsonify({
            "grupo_id": grupo_id,
            "eventos": eventos,
            "total_eventos": len(eventos)
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
