# API de Gestão de Eventos e Usuários

API Flask para gestão de eventos, usuários e grupos em empresas, com sistema de aprovação hierárquico.

## Estrutura do Projeto

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
│   └── routes/
│       ├── __init__.py
│       ├── auth.py       # Autenticação
│       ├── empresas.py   # CRUD Empresas
│       ├── grupos.py     # CRUD Grupos
│       ├── usuarios.py   # CRUD Usuários
│       ├── eventos.py    # CRUD Eventos
│       └── calendario.py # Calendário
├── database/             # Diretório do banco SQLite
├── scripts/
│   └── seed_data.py     # Script para dados de exemplo
└── README.md
```

## Modelo de Dados

### Hierarquia
- **Empresa** → **Grupo** → **Usuário** → **Evento**

### Tipos de Usuário
- **RH**: CRUD completo em empresas, grupos, usuários e eventos
- **Gestor**: CRUD em usuários e eventos do seu grupo, aprovação de eventos
- **Comum**: CRUD nos próprios eventos, visualização do calendário do grupo

### Sistema de Aprovação
- Eventos criados ficam com status "pendente"
- Gestores e RH podem aprovar/rejeitar eventos
- Apenas eventos aprovados aparecem no calendário compartilhado

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

**Variáveis obrigatórias:**
- `SECRET_KEY`: Chave secreta do Flask
- `JWT_SECRET_KEY`: Chave secreta para JWT
- `DATABASE_URL`: URL do banco de dados

## Autenticação JWT

A API utiliza JWT (JSON Web Tokens) para autenticação:

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "maria.rh@techsolutions.com", "senha": "123456"}'
```

### Usando o Token
```bash
curl -X GET http://localhost:5000/api/usuarios \
  -H "Authorization: Bearer <access_token>"
```

### Renovar Token
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

4. Execute o script para criar dados de exemplo:
```bash
python scripts/seed_data.py
```

5. Execute a aplicação:
```bash
python app.py
```

## Endpoints Principais

### Autenticação
- `POST /api/auth/login` - Login de usuário

### Empresas (RH apenas)
- `GET /api/empresas` - Listar empresas
- `POST /api/empresas` - Criar empresa
- `PUT /api/empresas/{id}` - Atualizar empresa
- `DELETE /api/empresas/{id}` - Desativar empresa

### Grupos (RH e Gestores)
- `GET /api/grupos` - Listar grupos
- `POST /api/grupos` - Criar grupo
- `PUT /api/grupos/{id}` - Atualizar grupo
- `DELETE /api/grupos/{id}` - Desativar grupo

### Usuários
- `GET /api/usuarios` - Listar usuários (com filtros)
- `POST /api/usuarios` - Criar usuário
- `PUT /api/usuarios/{id}` - Atualizar usuário
- `DELETE /api/usuarios/{id}` - Desativar usuário

### Eventos
- `GET /api/eventos` - Listar eventos (com filtros)
- `POST /api/eventos` - Criar evento
- `PUT /api/eventos/{id}` - Atualizar evento
- `DELETE /api/eventos/{id}` - Deletar evento
- `POST /api/eventos/{id}/aprovar` - Aprovar evento
- `POST /api/eventos/{id}/rejeitar` - Rejeitar evento

### Calendário
- `GET /api/calendario` - Eventos para calendário
- `GET /api/calendario/grupo/{id}` - Calendário de um grupo específico

## Credenciais de Teste

Após executar o script de dados de exemplo:

- **RH**: maria.rh@techsolutions.com / 123456
- **Gestor**: joao.gestor@techsolutions.com / 123456
- **Dev**: ana.dev@techsolutions.com / 123456
- **Dev**: carlos.dev@techsolutions.com / 123456
- **Marketing**: lucia.marketing@techsolutions.com / 123456

## Status Atual

✅ **IMPLEMENTADO:**
- Autenticação JWT completa (access + refresh tokens)
- Middleware de autorização por escopo
- Sistema de permissões hierárquico
- Validações robustas de dados
- Testes completos da API
- Documentação detalhada

## Próximos Passos Opcionais

1. Paginação para listas grandes
2. Health check endpoint
3. Sistema de logging avançado
4. Documentação OpenAPI/Swagger
5. Rate limiting
6. Sistema de notificações
7. Relatórios e dashboards
