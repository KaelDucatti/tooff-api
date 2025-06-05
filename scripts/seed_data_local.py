"""
Script para popular o banco SQLite local com dados de exemplo
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from api.database.models import init_db, TipoUsuario, FlagGestor
from api.database.crud import (
    criar_uf, criar_empresa, criar_grupo, criar_usuario, criar_evento,
    criar_tipo_ausencia, criar_turno, criar_feriado_nacional
)

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório pai ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def seed_database():
    """Popula o banco SQLite local com dados de exemplo"""
    
    print("🚀 Conectando ao SQLite local...")
    
    try:
        # Inicializa o banco SQLite
        init_db("sqlite:///database/tooff_app.db")
        
        print("Criando dados de exemplo no SQLite...")
        
        # 1. Criar UFs
        print("📍 Criando UFs...")
        ufs = [
            (11, "SP"), (21, "RJ"), (31, "MG"), (41, "PR"), (42, "SC"),
            (43, "RS"), (51, "MT"), (52, "GO"), (53, "DF")
        ]
        
        for cod_uf, uf in ufs:
            try:
                criar_uf(cod_uf, uf)
            except IntegrityError:
                pass  # UF já existe
        
        # 2. Criar tipos de ausência
        print("📝 Criando tipos de ausência...")
        tipos_ausencia = [
            ("Férias", False),
            ("Assiduidade", False),
            ("Plantão", True),
            ("Licença Maternidade/Paternidade", False),
            ("Evento Especial", False),
            ("Licença Geral", False)
        ]
        
        tipos_criados = []
        for desc, usa_turno in tipos_ausencia:
            try:
                tipo = criar_tipo_ausencia(desc, usa_turno)
                tipos_criados.append(tipo)
            except IntegrityError:
                pass  # Tipo já existe
        
        # 3. Criar turnos
        print("⏰ Criando turnos...")
        turnos = ["Dia", "Noite", "Madrugada"]
        for turno_desc in turnos:
            try:
                criar_turno(turno_desc)
            except IntegrityError:
                pass  # Turno já existe
        
        # 4. Criar empresa
        print("🏢 Criando empresa...")
        empresa = criar_empresa(
            cnpj=12345678000190,
            id_empresa=1,
            nome="Tech Solutions LTDA",
            endereco="Rua das Flores, 123 - São Paulo/SP",
            telefone="(11) 1234-5678",
            email="contato@techsolutions.com"
        )
        print(f"✅ Empresa criada: {empresa.nome}")
        
        # 5. Criar grupos
        print("👥 Criando grupos...")
        grupo_rh = criar_grupo(
            nome="Recursos Humanos",
            cnpj_empresa=empresa.cnpj,
            telefone="(11) 1234-5679",
            descricao="Equipe de recursos humanos"
        )

        grupo_dev = criar_grupo(
            nome="Desenvolvimento",
            cnpj_empresa=empresa.cnpj,
            telefone="(11) 1234-5680",
            descricao="Equipe de desenvolvimento de software"
        )
        
        print(f"✅ Grupos criados: {grupo_rh.nome}, {grupo_dev.nome}")
        
        # 6. Criar usuários
        print("👤 Criando usuários...")
        usuario_rh = criar_usuario(
            cpf=12345678901,
            nome="Maria Silva",
            email="maria.rh@techsolutions.com",
            senha="123456",
            grupo_id=grupo_rh.id,
            inicio_na_empresa="2020-01-15",
            uf="SP",
            tipo_usuario=TipoUsuario.RH.value,
            flag_gestor=FlagGestor.NAO.value
        )
        
        gestor_dev = criar_usuario(
            cpf=23456789012,
            nome="João Santos",
            email="joao.gestor@techsolutions.com",
            senha="123456",
            grupo_id=grupo_dev.id,
            inicio_na_empresa="2021-03-10",
            uf="SP",
            tipo_usuario=TipoUsuario.GESTOR.value,
            flag_gestor=FlagGestor.SIM.value
        )
        
        dev1 = criar_usuario(
            cpf=34567890123,
            nome="Ana Costa",
            email="ana.dev@techsolutions.com",
            senha="123456",
            grupo_id=grupo_dev.id,
            inicio_na_empresa="2022-06-01",
            uf="SP",
            tipo_usuario=TipoUsuario.COMUM.value,
            flag_gestor=FlagGestor.NAO.value
        )
        
        print("✅ Usuários criados:")
        print(f"- RH: {usuario_rh.nome} (CPF {usuario_rh.cpf})")
        print(f"- Gestor: {gestor_dev.nome} (CPF {gestor_dev.cpf})")
        print(f"- Dev: {dev1.nome} (CPF {dev1.cpf})")
        
        # 7. Criar eventos de exemplo
        print("📅 Criando eventos...")
        if tipos_criados:
            evento = criar_evento(
                cpf_usuario=dev1.cpf,
                data_inicio="2024-12-15",
                data_fim="2024-12-19",
                id_tipo_ausencia=tipos_criados[0].id_tipo_ausencia,  # Férias
                uf="SP",
                aprovado_por=gestor_dev.cpf
            )
            print(f"✅ Evento criado: ID {evento.id}")
        
        # 8. Criar alguns feriados
        print("🎉 Criando feriados...")
        try:
            criar_feriado_nacional("2024-01-01", "SP", "Confraternização Universal")
            criar_feriado_nacional("2024-04-21", "SP", "Tiradentes")
        except IntegrityError:
            pass  # Feriados já existem
        
        print("\n🎉 Dados de exemplo criados com sucesso no SQLite!")
        print("📊 Banco local pronto para desenvolvimento!")
        print("✅ Enums corretamente implementados")

        print("\n=== CREDENCIAIS DE TESTE ===")
        print(f"RH: {usuario_rh.email} / 123456")
        print(f"Gestor: {gestor_dev.email} / 123456")
        print(f"Dev: {dev1.email} / 123456")
        
    except IntegrityError as ie:
        print(f"❌ Erro de integridade dos dados: {ie}")
        print("💡 Alguns dados podem já existir no banco.")
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
        raise

if __name__ == "__main__":
    seed_database()
