"""
Script para popular o banco de dados com dados de exemplo
"""
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))

from api.database.models import init_db, TipoUsuario, TipoAusencia
from api.database.crud import (
    criar_empresa, criar_grupo, criar_usuario, criar_evento
)

def seed_database():
    """Popula o banco com dados de exemplo"""
    
    # Inicializa o banco
    init_db("sqlite:///./database/app.db")
    
    print("Criando dados de exemplo...")
    
    # Cria empresa
    empresa = criar_empresa(
        nome="Tech Solutions LTDA",
        cnpj="12.345.678/0001-90",
        endereco="Rua das Flores, 123 - São Paulo/SP",
        telefone="(11) 1234-5678",
        email="contato@techsolutions.com"
    )
    print(f"Empresa criada: {empresa.nome}")
    
    # Cria grupos
    grupo_dev = criar_grupo(
        nome="Desenvolvimento",
        empresa_id=empresa.id,
        descricao="Equipe de desenvolvimento de software"
    )
    
    grupo_marketing = criar_grupo(
        nome="Marketing",
        empresa_id=empresa.id,
        descricao="Equipe de marketing e vendas"
    )
    
    print(f"Grupos criados: {grupo_dev.nome}, {grupo_marketing.nome}")
    
    # Cria usuários
    # Usuário RH
    usuario_rh = criar_usuario(
        nome="Maria Silva",
        email="maria.rh@techsolutions.com",
        senha="123456",
        inicio_na_empresa="2020-01-15",
        tipo_usuario=TipoUsuario.RH
    )
    
    # Gestor do grupo de desenvolvimento
    gestor_dev = criar_usuario(
        nome="João Santos",
        email="joao.gestor@techsolutions.com",
        senha="123456",
        inicio_na_empresa="2021-03-10",
        tipo_usuario=TipoUsuario.GESTOR,
        grupo_id=grupo_dev.id
    )
    
    # Usuários comuns
    dev1 = criar_usuario(
        nome="Ana Costa",
        email="ana.dev@techsolutions.com",
        senha="123456",
        inicio_na_empresa="2022-06-01",
        tipo_usuario=TipoUsuario.COMUM,
        grupo_id=grupo_dev.id
    )
    
    dev2 = criar_usuario(
        nome="Carlos Oliveira",
        email="carlos.dev@techsolutions.com",
        senha="123456",
        inicio_na_empresa="2023-01-20",
        tipo_usuario=TipoUsuario.COMUM,
        grupo_id=grupo_dev.id
    )
    
    marketing1 = criar_usuario(
        nome="Lucia Ferreira",
        email="lucia.marketing@techsolutions.com",
        senha="123456",
        inicio_na_empresa="2022-09-15",
        tipo_usuario=TipoUsuario.COMUM,
        grupo_id=grupo_marketing.id
    )
    
    print("Usuários criados:")
    print(f"- RH: {usuario_rh.nome}")
    print(f"- Gestor: {gestor_dev.nome}")
    print(f"- Devs: {dev1.nome}, {dev2.nome}")
    print(f"- Marketing: {marketing1.nome}")
    
    # Cria alguns eventos de exemplo
    evento1 = criar_evento(
        usuario_id=dev1.id,
        data_inicio="2024-02-15",
        data_fim="2024-02-19",
        tipo_ausencia=TipoAusencia.FERIAS,
        descricao="Férias de carnaval"
    )
    
    evento2 = criar_evento(
        usuario_id=dev2.id,
        data_inicio="2024-03-01",
        data_fim="2024-03-01",
        tipo_ausencia=TipoAusencia.ASSIDUIDADE,
        descricao="Consulta médica"
    )
    
    print(f"Eventos criados: {evento1.id}, {evento2.id}")
    print("Dados de exemplo criados com sucesso!")
    
    print("\n=== CREDENCIAIS DE TESTE ===")
    print("RH: maria.rh@techsolutions.com / 123456")
    print("Gestor: joao.gestor@techsolutions.com / 123456")
    print("Dev: ana.dev@techsolutions.com / 123456")
    print("Dev: carlos.dev@techsolutions.com / 123456")
    print("Marketing: lucia.marketing@techsolutions.com / 123456")

if __name__ == "__main__":
    seed_database()
