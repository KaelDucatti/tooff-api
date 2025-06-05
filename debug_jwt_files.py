#!/usr/bin/env python3
"""
Script para diagnosticar problemas de JWT no Flask
"""

import os
import jwt
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def verificar_configuracao():
    """Verificar configurações JWT"""
    print("🔍 VERIFICANDO CONFIGURAÇÃO JWT")
    print("=" * 50)
    
    # Verificar JWT_SECRET_KEY
    secret_key = os.getenv('JWT_SECRET_KEY')
    if secret_key:
        print(f"✅ JWT_SECRET_KEY encontrada: {secret_key[:10]}...")
    else:
        print("❌ JWT_SECRET_KEY não encontrada no .env")
        return False
    
    # Verificar outras configurações
    jwt_algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
    jwt_expiration = os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600')
    
    print(f"✅ JWT_ALGORITHM: {jwt_algorithm}")
    print(f"✅ JWT_ACCESS_TOKEN_EXPIRES: {jwt_expiration} segundos")
    
    return True

def criar_token_teste():
    """Criar um token de teste para comparação"""
    print("\n🔧 CRIANDO TOKEN DE TESTE")
    print("=" * 50)
    
    secret_key = os.getenv('JWT_SECRET_KEY')
    if not secret_key:
        print("❌ Não é possível criar token sem JWT_SECRET_KEY")
        return None
    
    # Payload de teste (baseado no que vimos no token real)
    payload = {
        'user_cpf': 12345678901,
        'email': 'maria.rh@techsolutions.com',
        'tipo_usuario': 'rh',
        'flag_gestor': 'N',
        'grupo_id': 2,
        'uf': 'SP',
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    try:
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        print(f"✅ Token de teste criado: {token[:50]}...")
        return token
    except Exception as e:
        print(f"❌ Erro ao criar token: {e}")
        return None

def decodificar_token(token_string):
    """Decodificar e validar token"""
    print("\n🔍 DECODIFICANDO TOKEN")
    print("=" * 50)
    
    secret_key = os.getenv('JWT_SECRET_KEY')
    if not secret_key:
        print("❌ JWT_SECRET_KEY não encontrada")
        return None
    
    try:
        # Decodificar sem verificar (para debug)
        decoded_unverified = jwt.decode(token_string, options={"verify_signature": False})
        print("📋 Token decodificado (sem verificar assinatura):")
        print(json.dumps(decoded_unverified, indent=2, default=str))
        
        # Verificar expiração
        if 'exp' in decoded_unverified:
            exp_timestamp = decoded_unverified['exp']
            exp_date = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            
            print(f"\n⏰ Expiração: {exp_date}")
            print(f"⏰ Agora: {now}")
            print(f"⏰ Status: {'❌ EXPIRADO' if exp_date < now else '✅ VÁLIDO'}")
        
        # Tentar decodificar com verificação
        print("\n🔐 Tentando decodificar com secret_key...")
        decoded_verified = jwt.decode(token_string, secret_key, algorithms=['HS256'])
        print("✅ Token válido e verificado com sucesso!")
        return decoded_verified
        
    except jwt.ExpiredSignatureError:
        print("❌ Token expirado")
        return None
    except jwt.InvalidSignatureError:
        print("❌ Assinatura inválida - JWT_SECRET_KEY pode estar incorreta")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Token inválido: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def verificar_middleware():
    """Verificar se o middleware existe e está configurado"""
    print("\n🔍 VERIFICANDO ARQUIVOS DE MIDDLEWARE")
    print("=" * 50)
    
    middleware_files = [
        'api/middleware/jwt_auth.py',
        'api/middleware/auth.py',
        'api/middleware/__init__.py'
    ]
    
    for file_path in middleware_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} existe")
            
            # Verificar conteúdo básico
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'jwt' in content.lower():
                        print(f"   📋 Contém código JWT")
                    if 'token_required' in content or 'jwt_required' in content:
                        print(f"   📋 Contém decorador de autenticação")
            except Exception as e:
                print(f"   ❌ Erro ao ler arquivo: {e}")
        else:
            print(f"❌ {file_path} não encontrado")

def main():
    """Função principal"""
    print("🚀 DIAGNÓSTICO JWT FLASK")
    print("=" * 60)
    
    # 1. Verificar configuração
    if not verificar_configuracao():
        print("\n❌ Configuração inválida. Não é possível continuar.")
        return
    
    # 2. Verificar middleware
    verificar_middleware()
    
    # 3. Criar token de teste
    token_teste = criar_token_teste()
    
    # 4. Token real do teste (exemplo do log)
    token_real = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NwZiI6MTIzNDU2Nzg5MDEsImVtYWlsIjoibWFyaWEucmhAdGVjaHNvbHV0aW9ucy5jb20iLCJ0aXBvX3VzdWFyaW8iOiJyaCIsImZsYWdfZ2VzdG9yIjoiTiIsImdydXBvX2lkIjoyLCJ1ZiI6IlNQIiwiZXhwIjoxNzQ5MDg0Nzc0LCJpYXQiOjE3NDkwODExNzQsInR5cGUiOiJhY2Nlc3MifQ.9GhErYtXbTwm_cdxgFPpzdYufO5i-4ApjnMue5UOj9g"
    
    print("\n🔍 ANALISANDO TOKEN REAL DO TESTE")
    decodificar_token(token_real)
    
    if token_teste:
        print("\n🔍 ANALISANDO TOKEN DE TESTE CRIADO")
        decodificar_token(token_teste)
    
    print("\n💡 CONCLUSÕES E PRÓXIMOS PASSOS:")
    print("=" * 50)
    print("1. Se o token real decodifica corretamente aqui mas falha na API:")
    print("   - Problema está no middleware Flask")
    print("   - Verificar se @jwt_required está sendo usado")
    print("   - Verificar se o middleware está registrado no app")
    print()
    print("2. Se o token real não decodifica aqui:")
    print("   - JWT_SECRET_KEY diferente entre geração e validação")
    print("   - Verificar .env e configuração do Flask")
    print()
    print("3. Se o token está expirado:")
    print("   - Ajustar JWT_ACCESS_TOKEN_EXPIRES")
    print("   - Implementar refresh token")

if __name__ == "__main__":
    main()
