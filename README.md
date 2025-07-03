# API de Gestão de Eventos e Usuários

API Flask para gestão de eventos, usuários e grupos em empresas, com sistema de aprovação hierárquico e validação de CPF/CNPJ.

## 🆕 Novidades na Versão 2.0

- **Identificação por CPF/CNPJ**: Migração para CPF como chave primária para usuários e CNPJ para empresas
- **Sistema de UFs**: Suporte completo aos estados brasileiros
- **Tipos de Ausência Configuráveis**: Administração flexível de tipos de ausência
- **Sistema de Turnos**: Suporte a diferentes turnos de trabalho
- **Feriados Nacionais e Estaduais**: Gerenciamento de feriados por UF
- **Validação de Integridade**: Sistema robusto de verificação de CPF/CNPJ e integridade referencial
- **Migração para MySQL**: Suporte completo ao MySQL na GCP Cloud SQL

## 📋 Estrutura do Projeto

```
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de variáveis de ambiente
├── api/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py     # Modelos SQLAlchemy
│   │   └── crud.py       # Operações CRUD
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py       # Autenticação
│   │   ├── empresas.py   # CRUD Empresas (CNPJ)
│   │   ├── grupos.py     # CRUD Grupos
│   │   ├── usuarios.py   # CRUD Usuários (CPF)
│   │   ├── eventos.py    # CRUD Eventos
│   │   ├── tipos_ausencia.py # Tipos de Ausência
│   │   ├── turnos.py     # Turnos
│   │   ├── ufs.py        # UFs
│   │   ├── feriados.py   # Feriados
│   │   └── validation.py # Endpoints de validação
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py       # Middleware de autenticação
│   │   └── jwt_auth.py   # Autenticação JWT
│   └── validation/
│       ├── __init__.py
│       ├── cpf_cnpj_validator.py # Validador de CPF/CNPJ
│       ├── integrity_checker.py  # Verificador de integridade
│       └── report_generator.py   # Gerador de relatórios
├── scripts/
│   ├── seed_data.py      # Dados de exemplo (schema antigo)
│   ├── seed_data_v2.py   # Dados de exemplo (schema novo)
│   ├── seed_data_local.py # Dados para SQLite local
│   ├── validate_integrity.py # Validação de integridade
│   └── fix_integrity_issues.py # Correção de problemas
└── docs/
    ├── API_DOCUMENTATION.md    # Documentação da API
    ├── SCHEMA_DOCUMENTATION.md # Documentação do schema
    └── VALIDATION_DOCUMENTATION.md # Documentação de validação
```

## 🏗️ Modelo de Dados

### Hierarquia
- **Empresa (CNPJ)** → **Grupo** → **Usuário (CPF)** → **Evento**

### Tipos de Usuário
- **RH**: Acesso limitado à própria empresa (não pode criar/deletar empresas)
- **Gestor** (flag_gestor='S'): CRUD em usuários e eventos do seu grupo, aprovação de eventos
- **Comum**: CRUD nos próprios eventos, visualização do calendário do grupo

### Sistema de Aprovação
- Eventos criados ficam com status "pendente"
- Gestores e RH podem aprovar/rejeitar eventos
- Apenas eventos aprovados aparecem no calendário compartilhado

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- MySQL (para produção) ou SQLite (para desenvolvimento)
- Pip

### Passos de Instalação

1. Clone o repositório
\`\`\`bash
git clone https://github.com/seu-usuario/api-gestao-eventos.git
cd api-gestao-eventos
\`\`\`

2. Instale as dependências:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Configure as variáveis de ambiente:
\`\`\`bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
\`\`\`

**Variáveis obrigatórias:**
- `SECRET_KEY`: Chave secreta do Flask
- `JWT_SECRET_KEY`: Chave secreta para JWT
- `DB_HOST`: Host do banco MySQL (ou deixe vazio para SQLite)
- `DB_PORT`: Porta do MySQL (padrão: 3306)
- `DB_NAME`: Nome do banco de dados
- `DB_USER`: Usuário do MySQL
- `DB_PASS`: Senha do MySQL

### Configuração do Banco de Dados

#### Opção 1: MySQL na GCP (Produção)
Certifique-se de que todas as variáveis DB_* estejam configuradas no .env

#### Opção 2: SQLite Local (Desenvolvimento)
Deixe as variáveis DB_* vazias no .env para usar SQLite automaticamente

### Populando o Banco de Dados

1. Para o schema antigo (compatibilidade):
\`\`\`bash
python scripts/seed_data.py
\`\`\`

2. Para o novo schema com CPF/CNPJ:
\`\`\`bash
python scripts/seed_data_v2.py
\`\`\`

3. Para SQLite local:
\`\`\`bash
python scripts/seed_data_local.py
\`\`\`

## 🚀 Executando a Aplicação

\`\`\`bash
python app.py
\`\`\`

A API estará disponível em `http://localhost:5000`

## 🔍 Validação de Integridade

O sistema inclui ferramentas para validar a integridade dos dados:

1. Verificar integridade:
\`\`\`bash
python scripts/validate_integrity.py
\`\`\`

2. Corrigir problemas de integridade:
\`\`\`bash
python scripts/fix_integrity_issues.py
\`\`\`

3. Via API (apenas RH):
\`\`\`
GET /api/validation/integrity-check
GET /api/validation/integrity-report
\`\`\`

## 🔐 Autenticação JWT

A API utiliza JWT (JSON Web Tokens) para autenticação:

### Login
\`\`\`bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "maria.rh@techsolutions.com", "senha": "123456"}'
\`\`\`

### Usando o Token
\`\`\`bash
curl -X GET http://localhost:5000/api/usuarios \
  -H "Authorization: Bearer <access_token>"
\`\`\`

### Renovar Token
\`\`\`bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
\`\`\`

## 👥 Credenciais de Teste

Após executar o script de dados de exemplo:

- **RH**: maria.rh@techsolutions.com / 123456 (CPF: 12345678901)
- **Gestor**: joao.gestor@techsolutions.com / 123456 (CPF: 23456789012)
- **Dev**: ana.dev@techsolutions.com / 123456 (CPF: 34567890123)
- **Dev**: carlos.dev@techsolutions.com / 123456 (CPF: 45678901234)
- **Marketing**: lucia.marketing@techsolutions.com / 123456 (CPF: 56789012345)

## 📚 Documentação Adicional

- [Documentação Completa da API](docs/API_DOCUMENTATION.md)
- [Documentação do Schema](docs/SCHEMA_DOCUMENTATION.md)
- [Documentação do Sistema de Validação](docs/VALIDATION_DOCUMENTATION.md)

## 🐛 Solução de Problemas

### Problemas de Conexão com MySQL
- Verifique se as credenciais no .env estão corretas
- Confirme se o IP do seu servidor está autorizado no Cloud SQL
- Teste a conexão com: `mysql -h <DB_HOST> -u <DB_USER> -p`

### Erros de Integridade
- Execute `python scripts/validate_integrity.py` para identificar problemas
- Use `python scripts/fix_integrity_issues.py` para correções automáticas

### Problemas com JWT
- Verifique se JWT_SECRET_KEY está definido no .env
- Confirme se o token não expirou (padrão: 1 hora)
- Use o endpoint /api/auth/refresh para renovar tokens expirados

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

  
### Próximos passos:

- **Rastreamento de saldo de férias** (dias de férias anuais por usuário)
- **Aviso prévio mínimo** para solicitações de férias (ex: 15 dias)
- **Máximo de dias consecutivos de férias** (ex: 30 dias)
- **Períodos de bloqueio** (sem férias durante períodos críticos)
- **Prevenção de sobreposição** (máx % da equipe de férias simultaneamente)
- **Eventos recorrentes** (ausências semanais/mensais)
- **Suporte a meio período**
- **Categorias de eventos** (férias, licença médica, treinamento, etc.)
- **Notificações por email** para mudanças de status de eventos
- **Notificações de lembrete** para aprovações pendentes (24h, 48h)
- **Notificações de escalação** para aprovações atrasadas (para alta gestão)
- **Notificações da equipe** para ausências aprovadas
- **Notificações de aniversário e datas comemorativas**
- **Alertas de saldo de férias** (quando estiver baixo)
- **Aprovação automática** para certos tipos de eventos (ex: consultas médicas sob 2 horas)
- **Delegação de autoridade de aprovação** (atribuição temporária de gestor)
- **Operações em lote** para solicitações similares
- **Solicitações baseadas em templates** (padrões comuns de ausência)
- **Regras de aprovação condicional** (baseadas no tamanho da equipe, temporada, etc.)
- **Integração com sistemas de folha de pagamento** (cálculo automático de deduções)