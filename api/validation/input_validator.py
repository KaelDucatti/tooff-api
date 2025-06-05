from typing import Optional, Dict, Any, Union, List
import re

def validar_cpf(cpf: Union[str, int]) -> bool:
    """Valida um CPF"""
    # Converte para string se for número
    cpf_str = str(cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf_str) != 11:
        return False
        
    # Verifica se todos os caracteres são dígitos
    if not cpf_str.isdigit():
        return False
        
    # Verifica se não são todos dígitos iguais
    if len(set(cpf_str)) == 1:
        return False
        
    # Implementação do algoritmo de validação de CPF
    # (simplificado para este exemplo)
    return True

def validar_cnpj(cnpj: Union[str, int]) -> bool:
    """Valida um CNPJ"""
    # Converte para string se for número
    cnpj_str = str(cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_str) != 14:
        return False
        
    # Verifica se todos os caracteres são dígitos
    if not cnpj_str.isdigit():
        return False
        
    # Verifica se não são todos dígitos iguais
    if len(set(cnpj_str)) == 1:
        return False
        
    # Implementação do algoritmo de validação de CNPJ
    # (simplificado para este exemplo)
    return True

def validar_email(email: str) -> bool:
    """Valida um email"""
    if not email or not isinstance(email, str):
        return False
        
    # Padrão básico de validação de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validar_data(data: str) -> bool:
    """Valida uma data no formato YYYY-MM-DD"""
    if not data or not isinstance(data, str):
        return False
        
    # Verifica o formato
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, data):
        return False
        
    # Verifica se é uma data válida
    try:
        from datetime import datetime
        datetime.strptime(data, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validar_telefone(telefone: str) -> bool:
    """Valida um telefone"""
    if not telefone or not isinstance(telefone, str):
        return False
        
    # Remove caracteres não numéricos
    numeros = re.sub(r'\D', '', telefone)
    
    # Verifica se tem entre 10 e 11 dígitos (com ou sem DDD)
    return 10 <= len(numeros) <= 11

def validar_uf(uf: str) -> bool:
    """Valida uma UF brasileira"""
    if not uf or not isinstance(uf, str):
        return False
    
    # Lista de UFs válidas
    ufs_validas = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
        'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
        'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    
    return uf.upper() in ufs_validas

def validar_usuario_input(dados: Dict[str, Any]) -> List[str]:
    """Valida os dados de entrada para criação/atualização de usuário"""
    erros = []
    
    # Validar campos obrigatórios
    campos_obrigatorios = ["cpf", "nome", "email", "senha", "grupo_id", "inicio_na_empresa", "uf"]
    for campo in campos_obrigatorios:
        if campo not in dados or not dados[campo]:
            erros.append(f"Campo obrigatório ausente: {campo}")
    
    # Se faltam campos obrigatórios, não continua a validação
    if erros:
        return erros
    
    # Validar CPF
    if not validar_cpf(dados["cpf"]):
        erros.append("CPF inválido")
    
    # Validar email
    if not validar_email(dados["email"]):
        erros.append("Email inválido")
    
    # Validar data
    if not validar_data(dados["inicio_na_empresa"]):
        erros.append("Data de início na empresa inválida")
    
    # Validar UF
    if not validar_uf(dados["uf"]):
        erros.append("UF inválida")
    
    return erros

def validar_grupo_input(dados: Dict[str, Any]) -> List[str]:
    """Valida os dados de entrada para criação/atualização de grupo"""
    erros = []
    
    # Validar campos obrigatórios
    campos_obrigatorios = ["nome", "cnpj_empresa", "telefone"]
    for campo in campos_obrigatorios:
        if campo not in dados or not dados[campo]:
            erros.append(f"Campo obrigatório ausente: {campo}")
    
    # Se faltam campos obrigatórios, não continua a validação
    if erros:
        return erros
    
    # Validar CNPJ
    if not validar_cnpj(dados["cnpj_empresa"]):
        erros.append("CNPJ inválido")
    
    # Validar telefone
    if not validar_telefone(dados["telefone"]):
        erros.append("Telefone inválido")
    
    return erros

def validar_evento_input(dados: Dict[str, Any]) -> List[str]:
    """Valida os dados de entrada para criação/atualização de evento"""
    erros = []
    
    # Validar campos obrigatórios
    campos_obrigatorios = ["cpf_usuario", "data_inicio", "data_fim", "id_tipo_ausencia", "uf"]
    for campo in campos_obrigatorios:
        if campo not in dados or dados[campo] is None:
            erros.append(f"Campo obrigatório ausente: {campo}")
    
    # Se faltam campos obrigatórios, não continua a validação
    if erros:
        return erros
    
    # Validar CPF
    if not validar_cpf(dados["cpf_usuario"]):
        erros.append("CPF inválido")
    
    # Validar datas
    if not validar_data(dados["data_inicio"]):
        erros.append("Data de início inválida")
    
    if not validar_data(dados["data_fim"]):
        erros.append("Data de fim inválida")
    
    # Validar que data_inicio <= data_fim
    if validar_data(dados["data_inicio"]) and validar_data(dados["data_fim"]):
        from datetime import datetime
        inicio = datetime.strptime(dados["data_inicio"], "%Y-%m-%d")
        fim = datetime.strptime(dados["data_fim"], "%Y-%m-%d")
        if inicio > fim:
            erros.append("Data de início não pode ser posterior à data de fim")
    
    # Validar UF
    if not validar_uf(dados["uf"]):
        erros.append("UF inválida")
    
    return erros
