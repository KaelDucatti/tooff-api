from flask import Blueprint, request, jsonify
from typing import Dict, Any
from datetime import datetime, timedelta

from ..database.crud import (
    listar_eventos, obter_evento, obter_grupo,
    obter_usuario, obter_tipo_ausencia
)
from ..middleware.auth import (
    jwt_required, filtrar_por_escopo_usuario,
    extrair_usuario_cpf_do_token, verificar_permissao_grupo, 
    verificar_permissao_usuario_target
)

calendario_bp = Blueprint('calendario', __name__)

def evento_para_calendario(evento: Any) -> Dict[str, Any]:
    """Converte um evento para o formato do calendário"""
    tipo_ausencia = obter_tipo_ausencia(evento.id_tipo_ausencia)
    
    # Tenta obter a descrição do tipo de ausência de forma segura
    tipo_desc = "Desconhecido"
    if tipo_ausencia:
        # Verifica qual atributo existe no modelo TipoAusencia
        for attr in ['descricao', 'nome', 'tipo', 'id']:
            if hasattr(tipo_ausencia, attr):
                tipo_desc = str(getattr(tipo_ausencia, attr))
                break
    
    # Cores baseadas no status
    cores = {
        'pendente': '#ffc107',  # Amarelo
        'aprovado': '#28a745',  # Verde
        'rejeitado': '#dc3545'  # Vermelho
    }
    
    # Converte data_fim para string se necessário e adiciona um dia
    if isinstance(evento.data_fim, str):
        data_fim_obj = datetime.fromisoformat(evento.data_fim)
    else:
        data_fim_obj = datetime.combine(evento.data_fim, datetime.min.time())
    
    data_fim_plus = (data_fim_obj + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Converte data_inicio para string se necessário
    if isinstance(evento.data_inicio, str):
        data_inicio_str = evento.data_inicio
    else:
        data_inicio_str = evento.data_inicio.strftime('%Y-%m-%d')
    
    return {
        'id': evento.id,
        'title': f"{tipo_desc} - {evento.usuario_nome if hasattr(evento, 'usuario_nome') else ''}",
        'start': data_inicio_str,
        'end': data_fim_plus,
        'backgroundColor': cores.get(evento.status, '#6c757d'),
        'borderColor': cores.get(evento.status, '#6c757d'),
        'extendedProps': {
            'cpf_usuario': evento.cpf_usuario,
            'tipo_ausencia': tipo_desc,
            'status': evento.status,
            'criado_em': evento.criado_em.isoformat() if hasattr(evento.criado_em, 'isoformat') else str(evento.criado_em)
        }
    }

def filtrar_eventos_por_data(eventos, inicio=None, fim=None):
    """Filtra eventos por data"""
    if not inicio and not fim:
        return eventos
    
    eventos_filtrados = []
    for evento in eventos:
        # Converte datas do evento para datetime se necessário
        if isinstance(evento.data_inicio, str):
            evento_inicio = datetime.fromisoformat(evento.data_inicio)
        else:
            evento_inicio = datetime.combine(evento.data_inicio, datetime.min.time())
        
        if isinstance(evento.data_fim, str):
            evento_fim = datetime.fromisoformat(evento.data_fim)
        else:
            evento_fim = datetime.combine(evento.data_fim, datetime.min.time())
        
        # Verifica se o evento está no período solicitado
        if inicio:
            inicio_obj = datetime.fromisoformat(inicio)
            if evento_fim < inicio_obj:
                continue
        
        if fim:
            fim_obj = datetime.fromisoformat(fim)
            if evento_inicio > fim_obj:
                continue
        
        eventos_filtrados.append(evento)
    
    return eventos_filtrados

@calendario_bp.route('', methods=['GET'])
@jwt_required
def listar_calendario():
    """Lista eventos para visualização em calendário"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Parâmetros de filtro
        inicio = request.args.get('inicio')
        fim = request.args.get('fim')
        tipo_ausencia = request.args.get('tipo_ausencia', type=int)
        status = request.args.get('status')
        
        # Aplica filtros baseados no escopo do usuário
        filtros = filtrar_por_escopo_usuario(usuario_cpf)
        
        # Determina os filtros baseados no escopo
        if filtros and 'cpf_usuario' in filtros:
            # Usuário comum vê apenas seus próprios eventos
            cpf_usuario = filtros['cpf_usuario']
            eventos = listar_eventos(
                cpf_usuario=cpf_usuario,
                status=status
            )
        elif filtros and 'grupo_id' in filtros:
            # Gestor vê eventos do seu grupo
            grupo_id = filtros['grupo_id']
            eventos = listar_eventos(
                grupo_id=grupo_id,
                status=status
            )
        elif filtros and 'cnpj_empresa' in filtros:
            # RH vê eventos da empresa - lista todos os eventos e filtra depois
            eventos = listar_eventos(status=status)
        else:
            return jsonify([]), 200
        
        # Filtra por data se especificado
        eventos = filtrar_eventos_por_data(eventos, inicio, fim)
        
        # Filtra por tipo de ausência se especificado
        if tipo_ausencia:
            eventos = [e for e in eventos if e.id_tipo_ausencia == tipo_ausencia]
        
        return jsonify([evento_para_calendario(e) for e in eventos]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@calendario_bp.route('/grupo/<int:grupo_id>', methods=['GET'])
@jwt_required
def listar_calendario_grupo(grupo_id: int):
    """Lista eventos de um grupo específico para visualização em calendário"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Verifica permissão para acessar o grupo
        if not verificar_permissao_grupo(usuario_cpf, grupo_id):
            return jsonify({"erro": "Sem permissão para acessar dados deste grupo"}), 403
        
        # Parâmetros de filtro
        inicio = request.args.get('inicio')
        fim = request.args.get('fim')
        tipo_ausencia = request.args.get('tipo_ausencia', type=int)
        status = request.args.get('status')
        
        eventos = listar_eventos(
            grupo_id=grupo_id,
            status=status
        )
        
        # Filtra por data se especificado
        eventos = filtrar_eventos_por_data(eventos, inicio, fim)
        
        # Filtra por tipo de ausência se especificado
        if tipo_ausencia:
            eventos = [e for e in eventos if e.id_tipo_ausencia == tipo_ausencia]
        
        return jsonify({
            "grupo_id": grupo_id,
            "total_eventos": len(eventos),
            "eventos": [evento_para_calendario(e) for e in eventos]
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@calendario_bp.route('/usuario/<int:cpf_usuario>', methods=['GET'])
@jwt_required
def listar_calendario_usuario(cpf_usuario: int):
    """Lista eventos de um usuário específico para visualização em calendário"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Verifica permissão para acessar dados do usuário
        if not verificar_permissao_usuario_target(usuario_cpf, cpf_usuario):
            return jsonify({"erro": "Sem permissão para acessar dados deste usuário"}), 403
        
        # Parâmetros de filtro
        inicio = request.args.get('inicio')
        fim = request.args.get('fim')
        tipo_ausencia = request.args.get('tipo_ausencia', type=int)
        status = request.args.get('status')
        
        eventos = listar_eventos(
            cpf_usuario=cpf_usuario,
            status=status
        )
        
        # Filtra por data se especificado
        eventos = filtrar_eventos_por_data(eventos, inicio, fim)
        
        # Filtra por tipo de ausência se especificado
        if tipo_ausencia:
            eventos = [e for e in eventos if e.id_tipo_ausencia == tipo_ausencia]
        
        usuario = obter_usuario(cpf_usuario)
        nome_usuario = usuario.nome if usuario else "Usuário Desconhecido"
        
        return jsonify({
            "cpf_usuario": cpf_usuario,
            "nome_usuario": nome_usuario,
            "total_eventos": len(eventos),
            "eventos": [evento_para_calendario(e) for e in eventos]
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
