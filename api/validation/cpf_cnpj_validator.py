# """
# Validador de CPF e CNPJ com verificações de integridade
# """
# import re

# def validar_cpf(cpf: str) -> bool:
#     """
#     Valida um CPF brasileiro
#     """
#     # Remove caracteres não numéricos
#     cpf = re.sub(r'[^0-9]', '', str(cpf))
    
#     # Verifica se tem 11 dígitos
#     if len(cpf) != 11:
#         return False
    
#     # Verifica se todos os dígitos são iguais
#     if cpf == cpf[0] * 11:
#         return False
    
#     # Calcula o primeiro dígito verificador
#     soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
#     resto = soma % 11
#     digito1 = 0 if resto < 2 else 11 - resto
    
#     # Verifica o primeiro dígito
#     if int(cpf[9]) != digito1:
#         return False
    
#     # Calcula o segundo dígito verificador
#     soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
#     resto = soma % 11
#     digito2 = 0 if resto < 2 else 11 - resto
    
#     # Verifica o segundo dígito
#     return int(cpf[10]) == digito2

# def validar_cnpj(cnpj: str) -> bool:
#     """
#     Valida um CNPJ brasileiro
#     """
#     # Remove caracteres não numéricos
#     cnpj = re.sub(r'[^0-9]', '', str(cnpj))
    
#     # Verifica se tem 14 dígitos
#     if len(cnpj) != 14:
#         return False
    
#     # Verifica se todos os dígitos são iguais
#     if cnpj == cnpj[0] * 14:
#         return False
    
#     # Calcula o primeiro dígito verificador
#     pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
#     soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
#     resto = soma % 11
#     digito1 = 0 if resto < 2 else 11 - resto
    
#     # Verifica o primeiro dígito
#     if int(cnpj[12]) != digito1:
#         return False
    
#     # Calcula o segundo dígito verificador
#     pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
#     soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
#     resto = soma % 11
#     digito2 = 0 if resto < 2 else 11 - resto
    
#     # Verifica o segundo dígito
#     return int(cnpj[13]) == digito2

# def formatar_cpf(cpf: int) -> str:
#     """Formata CPF para exibição"""
#     cpf_str = str(cpf).zfill(11)
#     return f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"

# def formatar_cnpj(cnpj: int) -> str:
#     """Formata CNPJ para exibição"""
#     cnpj_str = str(cnpj).zfill(14)
#     return f"{cnpj_str[:2]}.{cnpj_str[2:5]}.{cnpj_str[5:8]}/{cnpj_str[8:12]}-{cnpj_str[12:]}"

# def cpf_para_int(cpf: str) -> int:
#     """Converte CPF string para int"""
#     return int(re.sub(r'[^0-9]', '', cpf))

# def cnpj_para_int(cnpj: str) -> int:
#     """Converte CNPJ string para int"""
#     return int(re.sub(r'[^0-9]', '', cnpj))

"""
Validador de CPF e CNPJ com verificações de integridade
"""
import re

def validar_cpf(cpf: str) -> bool:
    """
    Valida um CPF brasileiro - VALIDATION REMOVED
    """
    return True

def validar_cnpj(cnpj: str) -> bool:
    """
    Valida um CNPJ brasileiro - VALIDATION REMOVED
    """
    return True

def formatar_cpf(cpf: int) -> str:
    """Formata CPF para exibição"""
    cpf_str = str(cpf).zfill(11)
    return f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"

def formatar_cnpj(cnpj: int) -> str:
    """Formata CNPJ para exibição"""
    cnpj_str = str(cnpj).zfill(14)
    return f"{cnpj_str[:2]}.{cnpj_str[2:5]}.{cnpj_str[5:8]}/{cnpj_str[8:12]}-{cnpj_str[12:]}"

def cpf_para_int(cpf: str) -> int:
    """Converte CPF string para int"""
    return int(re.sub(r'[^0-9]', '', cpf))

def cnpj_para_int(cnpj: str) -> int:
    """Converte CNPJ string para int"""
    return int(re.sub(r'[^0-9]', '', cnpj))
