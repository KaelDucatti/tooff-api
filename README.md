# API de Gestão de Eventos e Usuários

API Flask para gestão de eventos, usuários e grupos em empresas, com sistema de aprovação hierárquico.

## Estrutura do Projeto

```
├── app.py                 
├── requirements.txt       
├── .env.example          
├── api/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py     
│   │   └── crud.py       
│   └── routes/
│       ├── __init__.py
│       ├── auth.py       
│       ├── empresas.py   
│       ├── grupos.py     
│       ├── usuarios.py   
│       ├── eventos.py    
│       └── calendario.py 
├── database/             
├── scripts/
│   └── seed_data.py     
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

## Próximos Passos

1. Implementar autenticação JWT
2. Adicionar middleware de autorização
3. Implementar validações mais robustas
4. Adicionar testes unitários
5. Documentação da API com Swagger
6. Sistema de notificações
7. Relatórios e dashboards
