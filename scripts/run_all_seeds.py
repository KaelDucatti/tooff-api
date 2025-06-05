#!/usr/bin/env python3
"""
Script para executar todos os scripts de seed em sequência
"""

import os
import sys
import subprocess
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_script(script_path):
    """Executa um script Python"""
    try:
        logging.info(f"🚀 Executando script: {script_path}")
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info(f"✅ Script {script_path} executado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Erro ao executar {script_path}: {e}")
        logging.error(f"Saída de erro: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"❌ Erro inesperado ao executar {script_path}: {e}")
        return False

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("🌱 EXECUÇÃO COMPLETA DE SEEDS")
    print("="*60)
    
    # Obtém o diretório de scripts
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Lista de scripts para executar em ordem
    scripts = [
        "seed_data_complete.py",  # Primeiro script - cria UFs, empresas, grupos e usuários
        "seed_additional_data.py", # Segundo script - cria tipos de ausência, turnos, feriados
        "verify_data.py"           # Terceiro script - verifica todos os dados criados
    ]
    
    # Executa cada script em sequência
    success = True
    for script in scripts:
        script_path = os.path.join(scripts_dir, script)
        if os.path.exists(script_path):
            if not run_script(script_path):
                success = False
                logging.warning(f"⚠️ Continuando com o próximo script após falha em {script}")
        else:
            logging.error(f"❌ Script não encontrado: {script_path}")
            success = False
    
    # Resultado final
    if success:
        print("\n" + "="*60)
        print("✅ TODOS OS SCRIPTS FORAM EXECUTADOS COM SUCESSO!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("⚠️ ALGUNS SCRIPTS FALHARAM. VERIFIQUE OS LOGS ACIMA.")
        print("="*60)

if __name__ == "__main__":
    main()
