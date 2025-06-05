from flask import Blueprint, jsonify, request
from ..database.crud import listar_turnos, obter_turno, criar_turno
from ..middleware.auth import jwt_required, rh_required

turnos_bp = Blueprint('turnos', __name__)

@turnos_bp.route('/', methods=['GET'])
def listar():
    """Lista todos os turnos"""
    try:
        turnos = listar_turnos()
        return jsonify([{
            "id": turno.id,
            "descricao": turno.descricao_ausencia
        } for turno in turnos]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@turnos_bp.route('/<int:turno_id>', methods=['GET'])
def obter(turno_id):
    """Obtém um turno específico pelo ID"""
    try:
        turno = obter_turno(turno_id)
        if not turno:
            return jsonify({"erro": "Turno não encontrado"}), 404
        
        return jsonify({
            "id": turno.id,
            "descricao": turno.descricao_ausencia
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@turnos_bp.route('/', methods=['POST'])
@jwt_required
@rh_required
def criar():
    """Cria um novo turno (apenas RH)"""
    try:
        dados = request.get_json(force=True)
        
        if not dados.get('descricao_ausencia'):
            return jsonify({"erro": "Descrição do turno é obrigatória"}), 400
        
        turno = criar_turno(
            descricao_ausencia=dados['descricao_ausencia']
        )
        
        return jsonify({
            "id": turno.id,
            "descricao": turno.descricao_ausencia
        }), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
