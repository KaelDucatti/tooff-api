from flask import Blueprint, request, jsonify
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError

from ..database.crud import (
    criar_usuario, listar_usuarios, obter_usuario,
    atualizar_usuario, deletar_usuario, usuario_para_dict
)
from ..middleware.auth import (
    jwt_required, requer_permissao_usuario, filtrar_por_escopo_usuario,
    extrair_usuario_cpf_do_token, verificar_permissao_grupo
)

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('', methods=['GET'])
@jwt_required
def listar():
    """Lista usuários com base no escopo do usuário logado"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        grupo_id = request.args.get('grupo_id', type=int)
        tipo_usuario = request.args.get('tipo_usuario')
        ativos_apenas = request.args.get('ativos', 'true').lower() == 'true'
        
        # Aplica filtros baseados no escopo do usuário
        filtros = filtrar_por_escopo_usuario(usuario_cpf)
        
        # Determina o grupo_id baseado no escopo
        if filtros and 'grupo_id' in filtros:
            # Gestores e usuários comuns veem apenas seu grupo
            grupo_id_final = filtros['grupo_id']
        elif filtros and 'cnpj_empresa' in filtros:
            # RH pode especificar grupo ou ver todos da empresa
            grupo_id_final = grupo_id  # Pode ser None para ver todos da empresa
        else:
            return jsonify([]), 200
        
        usuarios = listar_usuarios(
            grupo_id=grupo_id_final, 
            tipo_usuario=tipo_usuario, 
            ativos_apenas=ativos_apenas
        )
        
        # Para RH, filtra por empresa se não especificou grupo
        if filtros and 'cnpj_empresa' in filtros and not grupo_id:
            from ..database.crud import obter_grupo
            usuarios_filtrados = []
            for usuario in usuarios:
                if usuario.grupo_id:
                    grupo = obter_grupo(usuario.grupo_id)
                    if grupo and grupo.cnpj_empresa == filtros['cnpj_empresa']:
                        usuarios_filtrados.append(usuario)
            usuarios = usuarios_filtrados
        
        return jsonify([usuario_para_dict(u) for u in usuarios]), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@usuarios_bp.route('/<int:cpf>', methods=['GET'])
@jwt_required
@requer_permissao_usuario
def obter(cpf: int):
    """Obtém um usuário específico"""
    try:
        usuario = obter_usuario(cpf)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify(usuario_para_dict(usuario)), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@usuarios_bp.route('', methods=['POST'])
@jwt_required
def criar():
    """Cria um novo usuário"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if not usuario_cpf:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        
        # Verifica permissões baseadas no tipo de usuário
        from ..database.crud import obter_usuario as get_user
        usuario_logado = get_user(usuario_cpf)
        if not usuario_logado:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        grupo_id = dados.get("grupo_id")
        if grupo_id is None:
            return jsonify({"erro": "grupo_id é obrigatório"}), 400

        # Verifica se pode criar usuário no grupo especificado
        if not verificar_permissao_grupo(usuario_cpf, grupo_id):
            return jsonify({"erro": "Sem permissão para criar usuários neste grupo"}), 403
        
        # RH e Gestores podem criar usuários
        if usuario_logado.tipo_usuario not in ['rh'] and usuario_logado.flag_gestor != 'S':
            return jsonify({"erro": "Sem permissão para criar usuários"}), 403
        
        usuario = criar_usuario(
            cpf=dados["cpf"],
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            grupo_id=grupo_id,
            inicio_na_empresa=dados["inicio_na_empresa"],
            uf=dados["uf"],
            tipo_usuario=dados.get("tipo_usuario", "comum"),
            flag_gestor=dados.get("flag_gestor", "N")
        )
        return jsonify(usuario_para_dict(usuario)), 201
    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except ValueError as ve:
        return jsonify({"erro": f"Valor inválido: {ve}"}), 400
    except IntegrityError as ie:
        if "Duplicate entry" in str(ie) and "email" in str(ie):
            return jsonify({"erro": "Email já cadastrado"}), 409
        elif "Duplicate entry" in str(ie) and "cpf" in str(ie):
            return jsonify({"erro": "CPF já cadastrado"}), 409
        else:
            return jsonify({"erro": "Erro de integridade dos dados"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@usuarios_bp.route('/<int:cpf>', methods=['PUT'])
@jwt_required
@requer_permissao_usuario
def atualizar(cpf: int):
    """Atualiza um usuário"""
    dados: Dict[str, Any] = request.get_json(force=True)
    
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if usuario_cpf is None:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        from ..database.crud import obter_usuario as get_user
        usuario_logado = get_user(usuario_cpf)
        
        if not usuario_logado:
            return jsonify({"erro": "Usuário logado não encontrado"}), 404
        
        # Usuários comuns só podem atualizar alguns campos próprios
        if usuario_logado.tipo_usuario == 'comum' and usuario_logado.flag_gestor == 'N' and usuario_cpf == cpf:
            # Permite apenas atualização de senha e dados pessoais
            campos_permitidos = ['senha', 'nome', 'email']
            dados_filtrados = {k: v for k, v in dados.items() if k in campos_permitidos}
            dados = dados_filtrados
        elif usuario_logado.tipo_usuario == 'comum' and usuario_logado.flag_gestor == 'N':
            return jsonify({"erro": "Usuários comuns só podem atualizar próprios dados"}), 403
        
        sucesso = atualizar_usuario(cpf, **dados)
        if not sucesso:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify({"status": "Usuário atualizado"}), 200
    except ValueError as ve:
        return jsonify({"erro": f"Valor inválido: {ve}"}), 400
    except IntegrityError as ie:
        if "Duplicate entry" in str(ie) and "email" in str(ie):
            return jsonify({"erro": "Email já cadastrado"}), 409
        else:
            return jsonify({"erro": "Erro de integridade dos dados"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@usuarios_bp.route('/<int:cpf>', methods=['DELETE'])
@jwt_required
@requer_permissao_usuario
def deletar(cpf: int):
    """Desativa um usuário"""
    try:
        usuario_cpf = extrair_usuario_cpf_do_token()
        if usuario_cpf is None:
            return jsonify({"erro": "Token de autenticação necessário"}), 401
        from ..database.crud import obter_usuario as get_user
        usuario_logado = get_user(usuario_cpf)
        
        if not usuario_logado:
            return jsonify({"erro": "Usuário logado não encontrado"}), 404
        
        # Apenas RH e Gestores podem desativar usuários
        if usuario_logado.tipo_usuario not in ['rh'] and usuario_logado.flag_gestor != 'S':
            return jsonify({"erro": "Sem permissão para desativar usuários"}), 403
        
        # Usuário não pode desativar a si mesmo
        if usuario_cpf == cpf:
            return jsonify({"erro": "Não é possível desativar sua própria conta"}), 400
        
        sucesso = deletar_usuario(cpf)
        if not sucesso:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify({"status": "Usuário desativado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
