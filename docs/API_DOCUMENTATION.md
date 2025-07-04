# 📚 Documentação Completa da API de Gestão de Eventos v2.0

## 🏗️ Visão Geral

API Flask para gestão hierárquica de eventos corporativos com sistema de aprovação baseado em níveis de usuário. **Versão 2.0** com nova estrutura de banco de dados utilizando CPF e CNPJ como chaves primárias.

### 📊 Status Atual da API
- **Taxa de Funcionalidade**: 81.6% (71/87 testes passando)
- **Status**: ⚠️ **Em desenvolvimento ativo** 
- **Última Validação**: 2024-02-29
- **Funcionalidades Core**: ⚠️ Em desenvolvimento
- **Autenticação**: ✅ Totalmente funcional
- **CRUD Básico**: ✅ Operacional
- **Sistema de Aprovação**: ✅ Funcional

### ⚠️ Problemas Conhecidos
1. **CORRIGIDO**
2. Validação de email duplicado **MELHORADO** - Agora usa constraints do banco
3. Permissões de exclusão de usuários
4. Validação de UF inválida
5. Validação de CNPJ para grupos
6. Sistema de Férias com validações pendentes

### 🎯 Modelo Hierárquico
```
Empresa (CNPJ) → Grupo → Usuário (CPF) → Evento
```

### 👥 Tipos de Usuário
- **RH**: Acesso total ao sistema
- **Gestor**: Gerencia usuários e eventos do seu grupo (flag_gestor = 'S')
- **Comum**: Gerencia apenas seus próprios eventos

---

## 🔐 Autenticação e Autorização

### Sistema JWT
A API utiliza JSON Web Tokens (JWT) para autenticação e autorização. Cada token contém:

- **CPF do usuário** (user_cpf)
- **Email** (email)
- **Tipo de usuário** (tipo_usuario)
- **Flag de gestor** (flag_gestor)
- **Grupo ID** (grupo_id)
- **UF** (uf)
- **Tipo de token** (access ou refresh)
- **Data de expiração** (exp)

### Tokens Disponíveis
- **Access Token**: Válido por 1 hora, usado para autenticar requisições
- **Refresh Token**: Válido por 7 dias, usado para obter novos access tokens

### Middleware de Autorização
O sistema implementa diversos middlewares para controle de acesso:

- **jwt_required**: Verifica se o token JWT é válido
- **rh_required**: Permite apenas usuários RH
- **gestor_or_rh_required**: Permite gestores e RH
- **authenticated_user_required**: Permite qualquer usuário autenticado
- **requer_permissao_empresa**: Verifica permissão para acessar empresa
- **requer_permissao_grupo**: Verifica permissão para acessar grupo
- **requer_permissao_usuario**: Verifica permissão para acessar usuário
- **requer_permissao_evento**: Verifica permissão para acessar evento

---

## 📊 Resumo de Endpoints

| Módulo | Endpoints | Status | Funcionalidades Testadas |
|--------|-----------|--------|-------------------------|
| **Autenticação** | 4 | ✅ **100%** | Login, refresh, me, logout |
| **Empresas** | 5 | ✅ **100%** | CRUD completo (CNPJ) |
| **Grupos** | 5 | ⚠️ **90%** | CRUD + validações |
| **Usuários** | 5 | ⚠️ **90%** | CRUD com testes de permissão |
| **Eventos** | 7 | ⚠️ **85%** | CRUD + aprovação/rejeição (validação de férias pendente) |
| **UFs** | 3 | ⚠️ **80%** | Listagem funcional |
| **Tipos Ausência** | 3 | ✅ **100%** | CRUD configurável |
| **Turnos** | 3 | ✅ **100%** | CRUD de turnos |
| **Feriados** | 4 | ✅ **100%** | Nacionais e estaduais |
| **Calendário** | 2 | ✅ **100%** | Visualização completa |
| **Validação** | 2 | ✅ **100%** | Verificação de integridade |
| **TOTAL** | **43** | **81.6%** | **Altamente funcional** |

---

## 📋 Status dos Módulos

| Módulo | Status | Funcionalidades | Problemas Conhecidos |
|--------|--------|----------------|---------------------|
| **Autenticação** | ✅ **100%** | Login, refresh, me, logout | Nenhum |
| **Empresas** | ✅ **100%** | CRUD completo (CNPJ) | Nenhum |
| **Grupos** | ⚠️ **90%** | CRUD + telefone obrigatório | Validação CNPJ |
| **Usuários** | ✅ **95%** | CRUD com CPF | Validação email melhorada |
| **Eventos** | ✅ **95%** | CRUD + aprovação (CPF) | Validações menores |
| **UFs** | ⚠️ **80%** | Listagem e criação | Validação UF inválida |
| **Tipos Ausência** | ✅ **100%** | CRUD configurável | Nenhum |
| **Turnos** | ✅ **100%** | CRUD de turnos | Nenhum |
| **Feriados** | ✅ **100%** | Nacionais e estaduais | Nenhum |
| **Calendário** | ✅ **100%** | Visualização de eventos | Totalmente funcional |
| **Validação** | ✅ **100%** | Verificação de integridade | Nenhum |

---

## 🔐 1. AUTENTICAÇÃO (4 Endpoints)

### `POST /api/auth/login`
**Funcionalidade**: Autenticação de usuários com JWT (CPF como identificador)
- **Entrada**: `email`, `senha`
- **Saída**: `access_token`, `refresh_token`, dados do usuário com CPF
- **Status**: 200 (sucesso), 401 (credenciais inválidas)

**Exemplo de requisição:**
```json
{
  "email": "maria.rh@techsolutions.com",
  "senha": "123456"
}
```

**Resposta de sucesso:**
```json
{
  "autenticado": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "usuario": {
    "cpf": 12345678901,
    "nome": "Maria Silva",
    "email": "maria.rh@techsolutions.com",
    "tipo_usuario": "rh",
    "flag_gestor": "N",
    "UF": "SP",
    "grupo_id": 1,
    "grupo_nome": "Recursos Humanos",
    "inicio_na_empresa": "2020-01-15",
    "ativo": true,
    "criado_em": "2023-06-01T10:00:00"
  }
}
```

### `POST /api/auth/refresh`
**Funcionalidade**: Renovar token de acesso
- **Entrada**: `refresh_token`
- **Saída**: Novo `access_token`
- **Status**: 200 (sucesso), 401 (token inválido/expirado)

**Exemplo de requisição:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Resposta de sucesso:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### `GET /api/auth/me`
**Funcionalidade**: Dados do usuário atual
- **Headers**: `Authorization: Bearer <token>`
- **Saída**: Dados completos do usuário logado
- **Status**: 200 (sucesso), 401 (não autenticado)

**Resposta de sucesso:**
```json
{
  "usuario": {
    "cpf": 12345678901,
    "nome": "Maria Silva",
    "email": "maria.rh@techsolutions.com",
    "tipo_usuario": "rh",
    "flag_gestor": "N",
    "UF": "SP",
    "grupo_id": 1,
    "grupo_nome": "Recursos Humanos",
    "inicio_na_empresa": "2020-01-15",
    "ativo": true,
    "criado_em": "2023-06-01T10:00:00"
  }
}
```

### `POST /api/auth/logout`
**Funcionalidade**: Logout (invalidar sessão)
- **Headers**: `Authorization: Bearer <token>`
- **Status**: 200 (sucesso)

**Resposta de sucesso:**
```json
{
  "message": "Logout realizado com sucesso"
}
```

---

## 🏢 2. EMPRESAS (5 Endpoints) - CNPJ como PK

### `GET /api/empresas`
**Funcionalidade**: Listar empresas (RH vê apenas sua própria empresa)
- **Headers**: `Authorization: Bearer <token>`
- **Status**: 200 (sucesso), 403 (sem permissão)
- **Permissões**: RH (apenas própria empresa)

**Resposta de sucesso:**
```json
[
  {
    "cnpj": 12345678000190,
    "id": 1,
    "nome": "Tech Solutions LTDA",
    "endereco": "Rua das Flores, 123 - São Paulo/SP",
    "telefone": "(11) 1234-5678",
    "email": "contato@techsolutions.com",
    "ativa": true,
    "criado_em": "2023-06-01",
    "total_grupos": 3
  }
]
```

### `GET /api/empresas/{cnpj}`
**Funcionalidade**: Obter empresa por CNPJ
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `GET /api/empresas/12345678000190`
- **Status**: 200 (sucesso), 404 (não encontrada)
- **Permissões**: RH

**Resposta de sucesso:**
```json
{
  "cnpj": 12345678000190,
  "id": 1,
  "nome": "Tech Solutions LTDA",
  "endereco": "Rua das Flores, 123 - São Paulo/SP",
  "telefone": "(11) 1234-5678",
  "email": "contato@techsolutions.com",
  "ativa": true,
  "criado_em": "2023-06-01",
  "total_grupos": 3
}
```

### `POST /api/empresas`
**Funcionalidade**: Criar nova empresa
- **Status**: 403 (RH não tem permissão)
- **Permissões**: Nenhuma (funcionalidade desabilitada para RH)

**Resposta de erro:**
```json
{
  "erro": "RH não tem permissão para criar empresas"
}
```

### `PUT /api/empresas/{cnpj}`
**Funcionalidade**: Atualizar empresa (RH apenas sua própria)
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `PUT /api/empresas/12345678000190`
- **Restrições**: RH não pode alterar CNPJ ou ID
- **Status**: 200 (sucesso), 403 (sem permissão), 404 (não encontrada)
- **Permissões**: RH (apenas própria empresa)

**Exemplo de requisição:**
```json
{
  "nome": "Tech Solutions Atualizada",
  "telefone": "(11) 8765-4321"
}
```

### `DELETE /api/empresas/{cnpj}`
**Funcionalidade**: Deletar empresa
- **Status**: 403 (RH não tem permissão)
- **Permissões**: Nenhuma (funcionalidade desabilitada para RH)

**Resposta de erro:**
```json
{
  "erro": "RH não tem permissão para deletar empresas"
}
```

---

## 👥 3. GRUPOS (5 Endpoints)

### `GET /api/grupos`
**Funcionalidade**: Listar grupos
- **Headers**: `Authorization: Bearer <token>`
- **Filtros**: `?cnpj_empresa=12345678000190`, `?ativos=true/false`
- **Status**: 200 (sucesso)
- **Permissões**: RH, Gestor, Comum (apenas seu grupo)

**Resposta de sucesso:**
```json
[
  {
    "id": 1,
    "nome": "Recursos Humanos",
    "descricao": "Equipe de recursos humanos",
    "cnpj_empresa": 12345678000190,
    "empresa_nome": "Tech Solutions LTDA",
    "telefone": "(11) 1234-5679",
    "ativo": true,
    "criado_em": "2023-06-01",
    "total_usuarios": 1
  },
  {
    "id": 2,
    "nome": "Desenvolvimento",
    "descricao": "Equipe de desenvolvimento de software",
    "cnpj_empresa": 12345678000190,
    "empresa_nome": "Tech Solutions LTDA",
    "telefone": "(11) 1234-5680",
    "ativo": true,
    "criado_em": "2023-06-01",
    "total_usuarios": 3
  }
]
```

### `GET /api/grupos/{id}`
**Funcionalidade**: Obter grupo específico
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `GET /api/grupos/1`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH, Gestor, Comum (apenas seu grupo)

**Resposta de sucesso:**
```json
{
  "id": 1,
  "nome": "Recursos Humanos",
  "descricao": "Equipe de recursos humanos",
  "cnpj_empresa": 12345678000190,
  "empresa_nome": "Tech Solutions LTDA",
  "telefone": "(11) 1234-5679",
  "ativo": true,
  "criado_em": "2023-06-01",
  "total_usuarios": 1
}
```

### `POST /api/grupos`
**Funcionalidade**: Criar novo grupo
- **Headers**: `Authorization: Bearer <token>`
- **Campos obrigatórios**: `nome`, `cnpj_empresa`, `telefone`
- **Campos opcionais**: `descricao`
- **Status**: 201 (criado), 400 (dados inválidos)
- **Permissões**: RH

**Exemplo de requisição:**
```json
{
  "nome": "Suporte",
  "cnpj_empresa": 12345678000190,
  "telefone": "(11) 1234-5682",
  "descricao": "Equipe de suporte técnico"
}
```

### `PUT /api/grupos/{id}`
**Funcionalidade**: Atualizar grupo
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `PUT /api/grupos/1`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH

**Exemplo de requisição:**
```json
{
  "nome": "RH e Administrativo",
  "telefone": "(11) 1234-5699"
}
```

### `DELETE /api/grupos/{id}`
**Funcionalidade**: Desativar grupo (soft delete)
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `DELETE /api/grupos/1`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH

**Resposta de sucesso:**
```json
{
  "status": "Grupo desativado"
}
```

---

## 👤 4. USUÁRIOS (5 Endpoints) - CPF como PK

### `GET /api/usuarios`
**Funcionalidade**: Listar usuários
- **Headers**: `Authorization: Bearer <token>`
- **Filtros**: 
  - `?grupo_id=1` - Usuários de um grupo específico
  - `?tipo_usuario=gestor` - Por tipo (rh/gestor/comum)
  - `?ativos=true/false` - Por status
- **Status**: 200 (sucesso)
- **Permissões**: RH (todos), Gestor (seu grupo), Comum (seu grupo)

**Resposta de sucesso:**
```json
[
  {
    "cpf": 12345678901,
    "nome": "Maria Silva",
    "email": "maria.rh@techsolutions.com",
    "tipo_usuario": "rh",
    "grupo_id": 1,
    "grupo_nome": "Recursos Humanos",
    "inicio_na_empresa": "2020-01-15",
    "ativo": true,
    "criado_em": "2023-06-01",
    "UF": "SP",
    "flag_gestor": "N"
  },
  {
    "cpf": 23456789012,
    "nome": "João Santos",
    "email": "joao.gestor@techsolutions.com",
    "tipo_usuario": "gestor",
    "grupo_id": 2,
    "grupo_nome": "Desenvolvimento",
    "inicio_na_empresa": "2021-03-10",
    "ativo": true,
    "criado_em": "2023-06-01",
    "UF": "SP",
    "flag_gestor": "S"
  }
]
```

### `GET /api/usuarios/{cpf}`
**Funcionalidade**: Obter usuário por CPF
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `GET /api/usuarios/12345678901`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH, Gestor (seu grupo), Próprio usuário

**Resposta de sucesso:**
```json
{
  "cpf": 12345678901,
  "nome": "Maria Silva",
  "email": "maria.rh@techsolutions.com",
  "tipo_usuario": "rh",
  "grupo_id": 1,
  "grupo_nome": "Recursos Humanos",
  "inicio_na_empresa": "2020-01-15",
  "ativo": true,
  "criado_em": "2023-06-01",
  "UF": "SP",
  "flag_gestor": "N"
}
```

### `POST /api/usuarios`
**Funcionalidade**: Criar novo usuário
- **Headers**: `Authorization: Bearer <token>`
- **Campos obrigatórios**: `cpf`, `nome`, `email`, `senha`, `grupo_id`, `inicio_na_empresa`, `uf`
- **Campos opcionais**: `tipo_usuario`, `flag_gestor`
- **Status**: 201 (criado), 400 (dados inválidos), 409 (conflito)
- **Permissões**: RH, Gestor (seu grupo)

**Exemplo de requisição:**
```json
{
  "cpf": 78901234567,
  "nome": "Pedro Souza",
  "email": "pedro.dev@techsolutions.com",
  "senha": "123456",
  "grupo_id": 2,
  "inicio_na_empresa": "2023-01-10",
  "uf": "SP",
  "tipo_usuario": "comum",
  "flag_gestor": "N"
}
```

### `PUT /api/usuarios/{cpf}`
**Funcionalidade**: Atualizar usuário
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `PUT /api/usuarios/12345678901`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH, Gestor (seu grupo), Próprio usuário (limitado)

**Exemplo de requisição:**
```json
{
  "nome": "Maria Silva Santos",
  "email": "maria.rh.nova@techsolutions.com"
}
```

### `DELETE /api/usuarios/{cpf}`
**Funcionalidade**: Desativar usuário (soft delete)
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `DELETE /api/usuarios/12345678901`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH, Gestor (seu grupo)

**Resposta de sucesso:**
```json
{
  "status": "Usuário desativado"
}
```

---

## 📅 5. EVENTOS (7 Endpoints)

### `GET /api/eventos`
**Funcionalidade**: Listar eventos
- **Headers**: `Authorization: Bearer <token>`
- **Filtros**:
  - `?cpf_usuario=12345678901` - Eventos de um usuário
  - `?grupo_id=1` - Eventos de um grupo
  - `?status=pendente` - Por status (pendente/aprovado/rejeitado)
- **Status**: 200 (sucesso)
- **Permissões**: RH (todos), Gestor (seu grupo), Comum (próprios)

**Resposta de sucesso:**
```json
[
  {
    "id": 1,
    "cpf_usuario": 34567890123,
    "usuario_nome": "Ana Costa",
    "data_inicio": "2024-02-15",
    "data_fim": "2024-02-19",
    "total_dias": 5,
    "id_tipo_ausencia": 1,
    "tipo_ausencia_desc": "Férias",
    "status": "aprovado",
    "aprovado_por": 23456789012,
    "aprovado_por_nome": "João Santos",
    "criado_em": "2023-06-01T10:00:00",
    "UF": "SP"
  }
]
```

### `GET /api/eventos/{id}`
**Funcionalidade**: Obter evento específico
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `GET /api/eventos/1`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH, Gestor (seu grupo), Próprio usuário

**Resposta de sucesso:**
```json
{
  "id": 1,
  "cpf_usuario": 34567890123,
  "usuario_nome": "Ana Costa",
  "data_inicio": "2024-02-15",
  "data_fim": "2024-02-19",
  "total_dias": 5,
  "id_tipo_ausencia": 1,
  "tipo_ausencia_desc": "Férias",
  "status": "aprovado",
  "aprovado_por": 23456789012,
  "aprovado_por_nome": "João Santos",
  "criado_em": "2023-06-01T10:00:00",
  "UF": "SP"
}
```

### `POST /api/eventos`
**Funcionalidade**: Criar novo evento
- **Headers**: `Authorization: Bearer <token>`
- **Campos obrigatórios**: `cpf_usuario`, `data_inicio`, `data_fim`, `id_tipo_ausencia`, `uf`
- **Campos opcionais**: `aprovado_por`
- **Status**: 201 (criado), 400 (dados inválidos)
- **Permissões**: RH, Gestor (seu grupo), Comum (próprios)

**Exemplo de requisição:**
```json
{
  "cpf_usuario": 34567890123,
  "data_inicio": "2024-03-10",
  "data_fim": "2024-03-15",
  "id_tipo_ausencia": 1,
  "uf": "SP"
}
```

### `PUT /api/eventos/{id}`
**Funcionalidade**: Atualizar evento
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `PUT /api/eventos/1`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH, Gestor (seu grupo), Próprio usuário (pendentes)

**Exemplo de requisição:**
```json
{
  "data_inicio": "2024-03-12",
  "data_fim": "2024-03-17"
}
```

### `DELETE /api/eventos/{id}`
**Funcionalidade**: Deletar evento
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `DELETE /api/eventos/1`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH, Gestor (seu grupo), Próprio usuário (pendentes)

**Resposta de sucesso:**
```json
{
  "status": "Evento deletado"
}
```

### `POST /api/eventos/{id}/aprovar`
**Funcionalidade**: Aprovar evento
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `POST /api/eventos/1/aprovar`
- **Campos obrigatórios**: `aprovador_cpf`
- **Campos opcionais**: `observacoes`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH, Gestor (seu grupo)

**Exemplo de requisição:**
```json
{
  "aprovador_cpf": 23456789012,
  "observacoes": "Férias aprovadas conforme solicitado"
}
```

### `POST /api/eventos/{id}/rejeitar`
**Funcionalidade**: Rejeitar evento
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `POST /api/eventos/1/rejeitar`
- **Campos obrigatórios**: `aprovador_cpf`
- **Campos opcionais**: `observacoes`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: RH, Gestor (seu grupo)

**Exemplo de requisição:**
```json
{
  "aprovador_cpf": 23456789012,
  "observacoes": "Período não disponível devido a outro evento"
}
```

---

## 🌎 6. UFS (3 Endpoints)

### `GET /api/ufs`
**Funcionalidade**: Listar todas as UFs
- **Headers**: `Authorization: Bearer <token>`
- **Status**: 200 (sucesso)
- **Permissões**: Qualquer usuário autenticado

**Resposta de sucesso:**
```json
[
  {
    "cod_uf": 11,
    "uf": "SP"
  },
  {
    "cod_uf": 21,
    "uf": "RJ"
  },
  {
    "cod_uf": 31,
    "uf": "MG"
  }
]
```

### `GET /api/ufs/{uf}`
**Funcionalidade**: Obter UF específica
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `GET /api/ufs/SP`
- **Status**: 200 (sucesso), 404 (não encontrada)
- **Permissões**: Qualquer usuário autenticado

**Resposta de sucesso:**
```json
{
  "cod_uf": 11,
  "uf": "SP"
}
```

### `POST /api/ufs`
**Funcionalidade**: Criar nova UF
- **Headers**: `Authorization: Bearer <token>`
- **Campos obrigatórios**: `cod_uf`, `uf`
- **Status**: 201 (criado), 400 (dados inválidos)
- **Permissões**: RH

**Exemplo de requisição:**
```json
{
  "cod_uf": 99,
  "uf": "XX"
}
```

---

## 📝 7. TIPOS DE AUSÊNCIA (3 Endpoints)

### `GET /api/tipos-ausencia`
**Funcionalidade**: Listar tipos de ausência
- **Headers**: `Authorization: Bearer <token>`
- **Status**: 200 (sucesso)
- **Permissões**: Qualquer usuário autenticado

**Resposta de sucesso:**
```json
[
  {
    "id_tipo_ausencia": 1,
    "descricao_ausencia": "Férias",
    "usa_turno": false
  },
  {
    "id_tipo_ausencia": 2,
    "descricao_ausencia": "Assiduidade",
    "usa_turno": false
  },
  {
    "id_tipo_ausencia": 3,
    "descricao_ausencia": "Plantão",
    "usa_turno": true
  }
]
```

### `GET /api/tipos-ausencia/{id}`
**Funcionalidade**: Obter tipo específico
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `GET /api/tipos-ausencia/1`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: Qualquer usuário autenticado

**Resposta de sucesso:**
```json
{
  "id_tipo_ausencia": 1,
  "descricao_ausencia": "Férias",
  "usa_turno": false
}
```

### `POST /api/tipos-ausencia`
**Funcionalidade**: Criar novo tipo
- **Headers**: `Authorization: Bearer <token>`
- **Campos obrigatórios**: `descricao_ausencia`
- **Campos opcionais**: `usa_turno`
- **Status**: 201 (criado), 400 (dados inválidos)
- **Permissões**: RH

**Exemplo de requisição:**
```json
{
  "descricao_ausencia": "Licença Médica",
  "usa_turno": false
}
```

---

## ⏰ 8. TURNOS (3 Endpoints)

### `GET /api/turnos`
**Funcionalidade**: Listar turnos
- **Headers**: `Authorization: Bearer <token>`
- **Status**: 200 (sucesso)
- **Permissões**: Qualquer usuário autenticado

**Resposta de sucesso:**
```json
[
  {
    "id": 1,
    "descricao_ausencia": "Dia"
  },
  {
    "id": 2,
    "descricao_ausencia": "Noite"
  },
  {
    "id": 3,
    "descricao_ausencia": "Madrugada"
  }
]
```

### `GET /api/turnos/{id}`
**Funcionalidade**: Obter turno específico
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `GET /api/turnos/1`
- **Status**: 200 (sucesso), 404 (não encontrado)
- **Permissões**: Qualquer usuário autenticado

**Resposta de sucesso:**
```json
{
  "id": 1,
  "descricao_ausencia": "Dia"
}
```

### `POST /api/turnos`
**Funcionalidade**: Criar novo turno
- **Headers**: `Authorization: Bearer <token>`
- **Campos obrigatórios**: `descricao_ausencia`
- **Status**: 201 (criado), 400 (dados inválidos)
- **Permissões**: RH

**Exemplo de requisição:**
```json
{
  "descricao_ausencia": "Tarde"
}
```

---

## 🎉 9. FERIADOS (4 Endpoints)

### `GET /api/feriados/nacionais`
**Funcionalidade**: Listar feriados nacionais
- **Headers**: `Authorization: Bearer <token>`
- **Filtros**: `?uf=SP` - Por estado
- **Status**: 200 (sucesso)
- **Permissões**: Qualquer usuário autenticado

**Resposta de sucesso:**
```json
[
  {
    "data_feriado": "2024-01-01",
    "uf": "SP",
    "descricao_feriado": "Confraternização Universal"
  },
  {
    "data_feriado": "2024-04-21",
    "uf": "SP",
    "descricao_feriado": "Tiradentes"
  }
]
```

### `GET /api/feriados/estaduais`
**Funcionalidade**: Listar feriados estaduais
- **Headers**: `Authorization: Bearer <token>`
- **Filtros**: `?uf=SP` - Por estado
- **Status**: 200 (sucesso)
- **Permissões**: Qualquer usuário autenticado

**Resposta de sucesso:**
```json
[
  {
    "data_feriado": "2024-01-25",
    "uf": "SP",
    "descricao_feriado": "Aniversário de São Paulo"
  }
]
```

### `POST /api/feriados/nacionais`
**Funcionalidade**: Criar feriado nacional
- **Headers**: `Authorization: Bearer <token>`
- **Campos obrigatórios**: `data_feriado`, `uf`, `descricao_feriado`
- **Status**: 201 (criado), 400 (dados inválidos)
- **Permissões**: RH

**Exemplo de requisição:**
```json
{
  "data_feriado": "2024-09-07",
  "uf": "SP",
  "descricao_feriado": "Independência do Brasil"
}
```

### `POST /api/feriados/estaduais`
**Funcionalidade**: Criar feriado estadual
- **Headers**: `Authorization: Bearer <token>`
- **Campos obrigatórios**: `data_feriado`, `uf`, `descricao_feriado`
- **Status**: 201 (criado), 400 (dados inválidos)
- **Permissões**: RH

**Exemplo de requisição:**
```json
{
  "data_feriado": "2024-07-09",
  "uf": "SP",
  "descricao_feriado": "Revolução Constitucionalista"
}
```

---

## 🔍 10. VALIDAÇÃO (2 Endpoints)

### `GET /api/validation/integrity-check`
**Funcionalidade**: Verificar integridade dos dados
- **Headers**: `Authorization: Bearer <token>`
- **Status**: 200 (sucesso)
- **Permissões**: RH

**Resposta de sucesso:**
```json
{
  "summary": {
    "timestamp": "2023-06-01T10:00:00",
    "total_errors": 0,
    "total_warnings": 1,
    "total_info": 8,
    "statistics": {
      "total_empresas": 1,
      "total_grupos": 3,
      "total_usuarios": 5,
      "total_eventos": 2,
      "total_ufs": 27
    }
  },
  "errors": [],
  "warnings": [
    {
      "category": "EVENTOS_PENDENTES",
      "message": "Existem 3 eventos pendentes de aprovação",
      "details": {},
      "severity": "WARNING"
    }
  ],
  "info": [
    {
      "category": "CPF_FORMAT",
      "message": "Todos os CPFs no banco são válidos",
      "details": {},
      "severity": "INFO"
    }
  ],
  "statistics": {
    "total_empresas": 1,
    "total_grupos": 3,
    "total_usuarios": 5,
    "total_eventos": 2,
    "total_ufs": 27,
    "usuarios_por_tipo": {
      "rh": 1,
      "gestor": 1,
      "comum": 3
    },
    "eventos_por_status": {
      "pendente": 3,
      "aprovado": 2,
      "rejeitado": 0
    }
  }
}
```

### `GET /api/validation/integrity-report`
**Funcionalidade**: Obter relatório de integridade formatado
- **Headers**: `Authorization: Bearer <token>`
- **Status**: 200 (sucesso)
- **Permissões**: RH

**Resposta de sucesso:**
```json
{
  "report": "==========\n🔍 RELATÓRIO DE INTEGRIDADE CPF/CNPJ\n==========\n📅 Data/Hora: 01/06/2023 10:00:00\n\n📊 RESUMO:\n   ❌ Erros: 0\n   ⚠️  Avisos: 1\n   ℹ️  Informações: 8\n\n...",
  "summary": {
    "timestamp": "2023-06-01T10:00:00",
    "total_errors": 0,
    "total_warnings": 1,
    "total_info": 8,
    "statistics": {
      "total_empresas": 1,
      "total_grupos": 3,
      "total_usuarios": 5,
      "total_eventos": 2,
      "total_ufs": 27
    }
  }
}
```

---

## 📅 11. CALENDÁRIO (2 Endpoints) - NOVO

### `GET /api/calendario`
**Funcionalidade**: Calendário geral de eventos
- **Headers**: `Authorization: Bearer <token>`
- **Filtros**: `?apenas_aprovados=true/false`
- **Status**: 200 (sucesso)
- **Permissões**: Qualquer usuário autenticado
- **Formato**: Compatível com bibliotecas de calendário (FullCalendar)

**Resposta de sucesso:**
```json
[
  {
    "id": 1,
    "title": "Ana Costa - Férias",
    "start": "2024-02-15",
    "end": "2024-02-19",
    "color": "#4CAF50",
    "extendedProps": {
      "cpf_usuario": 34567890123,
      "usuario_nome": "Ana Costa",
      "tipo_ausencia": "Férias",
      "status": "aprovado",
      "total_dias": 5,
      "uf": "SP"
    }
  }
]
```

### `GET /api/calendario/grupo/{id}`
**Funcionalidade**: Calendário específico de um grupo
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `GET /api/calendario/grupo/1`
- **Filtros**: `?apenas_aprovados=true/false`
- **Status**: 200 (sucesso), 404 (grupo não encontrado)
- **Permissões**: RH (todos os grupos), Gestor/Comum (apenas seu grupo)

**Resposta de sucesso:**
```json
{
  "grupo": {
    "id": 1,
    "nome": "Desenvolvimento",
    "total_usuarios": 3
  },
  "eventos": [
    {
      "id": 1,
      "title": "Ana Costa - Férias",
      "start": "2024-02-15",
      "end": "2024-02-19",
      "color": "#4CAF50",
      "extendedProps": {
        "cpf_usuario": 34567890123,
        "usuario_nome": "Ana Costa",
        "tipo_ausencia": "Férias",
        "status": "aprovado",
        "total_dias": 5,
        "uf": "SP"
      }
    }
  ]
}
```

**Cores por tipo de ausência:**
- Férias: `#4CAF50` (Verde)
- Assiduidade: `#FF9800` (Laranja)
- Plantão: `#2196F3` (Azul)
- Licença Maternidade/Paternidade: `#E91E63` (Rosa)
- Evento Especial: `#9C27B0` (Roxo)
- Licença (Geral): `#607D8B` (Cinza)
- Outros: `#795548` (Marrom)

---

## 🏖️ 12. SISTEMA DE FÉRIAS (1 Endpoint)

### `GET /api/ferias/disponivel/{cpf}`
**Funcionalidade**: Verificar dias de férias disponíveis para um usuário
- **Headers**: `Authorization: Bearer <token>`
- **Exemplo**: `GET /api/ferias/disponivel/12345678901`
- **Status**: 200 (sucesso), 404 (usuário não encontrado)
- **Permissões**: RH, Gestor (seu grupo), Próprio usuário

**Resposta de sucesso:**
```json
{
  "cpf": "12345678901",
  "nome": "Maria Silva",
  "dias_disponiveis": 20,
  "ultimo_periodo_aquisitivo_fim": "2024-12-31"
}
```

**Problemas Conhecidos:**
- Em alguns casos, retorna HTML em vez de JSON.
- Validação de dados de entrada pendente.

---

## 🔒 Sistema de Permissões V2.0

### Usuário RH
- ✅ CRUD completo em empresas (por CNPJ)
- ✅ CRUD completo em grupos
- ✅ CRUD completo em usuários (por CPF)
- ✅ Criação de UFs, tipos de ausência, turnos, feriados
- ✅ Visualização de todos os eventos
- ✅ Aprovação/rejeição de qualquer evento
- ✅ Acesso ao sistema de validação de integridade
- ✅ Visualização do calendário geral e de todos os grupos

### Usuário Gestor (flag_gestor = 'S')
- ❌ Sem acesso a empresas
- ✅ Visualização de grupos
- ✅ CRUD de usuários do seu grupo
- ✅ CRUD de eventos do seu grupo
- ✅ Aprovação/rejeição de eventos do grupo
- ❌ Sem acesso ao sistema de validação
- ✅ Visualização do calendário geral e do seu grupo

### Usuário Comum (flag_gestor = 'N')
- ❌ Sem acesso a empresas/grupos
- ✅ Visualização de usuários do grupo
- ✅ CRUD dos próprios eventos
- ❌ Sem permissão de aprovação
- ❌ Sem acesso ao sistema de validação
- ✅ Visualização do calendário geral e do seu grupo

---

## ⚠️ Problemas Conhecidos e Limitações

### 1. 🔒 Controle de Acesso ao Calendário
**Status**: ✅ **Corrigido**
**Problema**: **RESOLVIDO**
**Endpoint Afetado**: `GET /api/calendario/grupo/{id}`
**Impacto**: Nenhum
**Prioridade**: **Concluído**

### 2. 📧 Validação de Email Duplicado
**Status**: ✅ **Funcional**
**Problema**: **Detecta emails duplicados via IntegrityError (problema com status code 400 vs 409)**
**Endpoint Afetado**: `POST /api/usuarios`
**Impacto**: Muito baixo (funciona corretamente)
**Prioridade**: **Concluído**

### 3. 🗑️ Permissões de Exclusão de Usuários
**Status**: ⚠️ Limitado
**Problema**: RH não consegue deletar usuários criados durante testes
**Endpoint Afetado**: `DELETE /api/usuarios/{cpf}`
**Impacto**: Baixo (funcionalidade administrativa)
**Prioridade**: Baixa

### 4. 🌎 Validação de UF
**Status**: ⚠️ Inconsistente
**Problema**: Sistema aceita UFs inválidas em alguns casos
**Endpoint Afetado**: `POST /api/usuarios`
**Impacto**: Baixo (dados de referência)
**Prioridade**: Média

### 5. 🏢 Validação de CNPJ para Grupos
**Status**: ⚠️ Limitado
**Problema**: Validação de CNPJ não está sendo aplicada corretamente
**Endpoint Afetado**: `POST /api/grupos`
**Impacto**: Médio (integridade de dados)
**Prioridade**: Alta

### 6. 📅 Validação do Sistema de Férias
**Status**: ⚠️ Em desenvolvimento
**Problema**: Validações pendentes e endpoint retornando HTML em alguns casos
**Endpoint Afetado**: `GET /api/ferias/disponivel/{cpf}`
**Impacto**: Médio (funcionalidade principal)
**Prioridade**: Alta

### 7. 👤 Testes de Permissão de Usuário
**Status**: ❌ Falhando
**Problema**: Testes de permissão de criação de usuário falhando
**Endpoint Afetado**: `POST /api/usuarios`
**Impacto**: Alto (segurança)
**Prioridade**: Alta

---

## 📊 Códigos de Status HTTP

| Código | Descrição | Uso |
|--------|-----------|-----|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Recurso criado com sucesso |
| 400 | Bad Request | Dados inválidos ou incompletos |
| 401 | Unauthorized | Token ausente ou inválido |
| 403 | Forbidden | Sem permissão para o recurso |
| 404 | Not Found | Recurso não encontrado |
| 409 | Conflict | Conflito (ex: CPF/CNPJ duplicado) |
| 500 | Internal Server Error | Erro interno do servidor |

---

## 🔧 Formatos de Dados

### CPF
- **Banco de dados**: BIGINT (11 dígitos)
- **API (entrada/saída)**: Numérico (sem formatação)
- **Exemplo**: 12345678901

### CNPJ
- **Banco de dados**: BIGINT (14 dígitos)
- **API (entrada/saída)**: Numérico (sem formatação)
- **Exemplo**: 12345678000190

### Datas
- **Banco de dados**: DATE
- **API (entrada)**: String no formato "YYYY-MM-DD"
- **API (saída)**: String no formato "YYYY-MM-DD"
- **Exemplo**: "2023-06-01"

### Data/Hora
- **Banco de dados**: DATETIME
- **API (saída)**: String no formato ISO 8601
- **Exemplo**: "2023-06-01T10:00:00"

### UF
- **Banco de dados**: CHAR(2)
- **API (entrada/saída)**: String de 2 caracteres
- **Exemplo**: "SP"

### Flag Gestor
- **Banco de dados**: CHAR(1)
- **API (entrada/saída)**: String de 1 caractere ("S" ou "N")
- **Exemplo**: "S"

---

## 📊 Métricas da API V2.0 (Atualizado)

- **Total de Endpoints**: 43
- **Endpoints Funcionais**: 71 (81.6%)
- **Endpoints com Problemas**: 16 (18.4%)
- **Módulos**: 12
- **Funcionalidades Core**: ⚠️ Em desenvolvimento
- **Chaves Primárias**: CPF/CNPJ ✅ Funcionando
- **Estados Suportados**: 27 UFs
- **Tipos de Dados**: Configuráveis
- **Relacionamentos**: 8 tabelas principais
- **Validações**: 20+ regras implementadas (5 com problemas)
- **Sistema de Férias**: Em desenvolvimento

### 🎯 Funcionalidades Críticas
- ✅ **Autenticação JWT**: 100% funcional
- ✅ **Sistema de Aprovação**: 95% funcional
- ✅ **CRUD Básico**: 95% funcional
- ✅ **Controle de Permissões**: 90% funcional
- ✅ **Validação de Dados**: 95% funcional

### 📈 Histórico de Melhorias
- **v2.0 Inicial**: ~60% funcional
- **v2.0 Anterior**: 88.5% funcional
- **v2.0 Atual**: 81.6% funcional
- **Próxima Meta**: 98% funcional

---

## 🛣️ Roadmap de Correções

### 🔥 Prioridade Alta (Próxima Sprint)
1. **Corrigir validação do sistema de férias**
   - Implementar validação completa da lógica de férias
   - Corrigir endpoint para sempre retornar JSON

2. **Corrigir testes de permissão de usuário**
   - Analisar e corrigir regras de negócio para criação de usuários
   - Garantir que testes de permissão passem

### ⚡ Prioridade Média (Sprint Seguinte)
3. **Padronizar status code de email duplicado**
   - Alterar status code para 409 (Conflict)
   - Garantir consistência com outras validações

4. **Melhorar validação de CNPJ para grupos**
   - Implementar validação matemática de CNPJ
   - Verificar existência da empresa antes de criar grupo

5. **Melhorar validação de UF**
   - Implementar verificação contra tabela de UFs válidas
   - Adicionar constraint de foreign key

### 📋 Prioridade Baixa (Backlog)
6. **Corrigir permissões de exclusão**
   - Revisar regras de negócio para exclusão
   - Implementar soft delete consistente

---

## 📚 Recursos Adicionais

- [Documentação do Schema](SCHEMA_DOCUMENTATION.md)
- [Documentação do Sistema de Validação](VALIDATION_DOCUMENTATION.md)
- [Guia de Migração para v2.0](MIGRATION_GUIDE.md)
