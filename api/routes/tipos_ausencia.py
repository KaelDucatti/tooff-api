from flask import Blueprint, jsonify, request
from ..database.crud import listar_tipos_ausencia, obter_tipo_ausencia, criar_tipo_ausencia
from ..middleware.auth import jwt_required, rh_required

tipos_ausencia_bp = Blueprint('tipos_ausencia', __name__)

@tipos_ausencia_bp.route('/', methods=['GET'])
def listar():
    """Lista todos os tipos de ausência"""
    try:
        tipos = listar_tipos_ausencia()
        return jsonify([{
            "id": tipo.id_tipo_ausencia,
            "descricao": tipo.descricao_ausencia,
            "usa_turno": tipo.usa_turno
        } for tipo in tipos]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@tipos_ausencia_bp.route('/<int:id_tipo>', methods=['GET'])
def obter(id_tipo):
    """Obtém um tipo de ausência específico pelo ID"""
    try:
        tipo = obter_tipo_ausencia(id_tipo)
        if not tipo:
            return jsonify({"erro": "Tipo de ausência não encontrado"}), 404
        
        return jsonify({
            "id": tipo.id_tipo_ausencia,
            "descricao": tipo.descricao_ausencia,
            "usa_turno": tipo.usa_turno
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@tipos_ausencia_bp.route('/', methods=['POST'])
@jwt_required
@rh_required
def criar():
    """Cria um novo tipo de ausência (apenas RH)"""
    try:
        dados = request.get_json(force=True)
        
        if not dados.get('descricao_ausencia'):
            return jsonify({"erro": "Descrição da ausência é obrigatória"}), 400
        
        usa_turno = dados.get('usa_turno', False)
        
        tipo = criar_tipo_ausencia(
            descricao_ausencia=dados['descricao_ausencia'],
            usa_turno=usa_turno
        )
        
        return jsonify({
            "id": tipo.id_tipo_ausencia,
            "descricao": tipo.descricao_ausencia,
            "usa_turno": tipo.usa_turno
        }), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
