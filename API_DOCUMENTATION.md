# 📚 Documentação Completa da API - Schema V2.0

## 🏗️ Visão Geral

API Flask para gestão hierárquica de eventos corporativos com sistema de aprovação baseado em níveis de usuário. **Versão 2.0** com nova estrutura de banco de dados utilizando CPF e CNPJ como chaves primárias.

### 🎯 Modelo Hierárquico
```
Empresa (CNPJ) → Grupo → Usuário (CPF) → Evento
```

### 👥 Tipos de Usuário
- **RH**: Acesso total ao sistema
- **Gestor**: Gerencia usuários e eventos do seu grupo (flag_gestor = 'S')
- **Comum**: Gerencia apenas seus próprios eventos

---

## 🆕 Principais Mudanças do Schema V2.0

### 🔑 Chaves Primárias Alteradas
- **Empresa**: `id` → `cnpj` (BIGINT)
- **Usuario**: `id` → `cpf` (BIGINT)
- **Grupo**: Mantém `id` mas referencia `cnpj_empresa`

### 📊 Novas Tabelas
- **`uf`**: Estados brasileiros (27 UFs)
- **`tipo_ausencia`**: Tipos configuráveis de ausência
- **`turno`**: Turnos de trabalho
- **`ausencia_turno`**: Relacionamento N:N entre ausências e turnos
- **`feriados_nacionais`**: Feriados nacionais por UF
- **`feriados_estaduais`**: Feriados estaduais por UF

### 🔧 Campos Adicionados
- **Usuario**: `UF` (CHAR(2)), `flag_gestor` (CHAR(1))
- **Grupo**: `telefone` (VARCHAR(20)) - obrigatório
- **Evento**: `UF` (CHAR(2)), referências atualizadas
- **Empresa**: Todos os campos agora obrigatórios

---

## 📊 Resumo de Funcionalidades

| Módulo | Endpoints | Funcionalidades |
|--------|-----------|----------------|
| **Autenticação** | 4 | Login, refresh, me, logout |
| **Empresas** | 5 | CRUD completo (CNPJ) |
| **Grupos** | 5 | CRUD + telefone obrigatório |
| **Usuários** | 5 | CRUD com CPF |
| **Eventos** | 7 | CRUD + aprovação (CPF) |
| **UFs** | 3 | Listagem e criação |
| **Tipos Ausência** | 3 | CRUD configurável |
| **Turnos** | 3 | CRUD de turnos |
| **Feriados** | 4 | Nacionais e estaduais |
| **TOTAL** | **39** | **Funcionalidades** |

---

## 🔐 1. AUTENTICAÇÃO (4 Funcionalidades)

### `POST /api/auth/login`
**Funcionalidade**: Autenticação de usuários com JWT (CPF como identificador)
- **Entrada**: `email`, `senha`
- **Saída**: `access_token`, `refresh_token`, dados do usuário com CPF
- **Status**: 200 (sucesso), 401 (credenciais inválidas)

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
    ...
  }
}
```

### Demais endpoints de autenticação
- `POST /api/auth/refresh` - Renovar token
- `GET /api/auth/me` - Dados do usuário atual
- `POST /api/auth/logout` - Logout

---

## 🏢 2. EMPRESAS (5 Funcionalidades) - CNPJ como PK

### `GET /api/empresas`
**Funcionalidade**: Listar empresas (RH apenas)
**Autenticação**: Requer `Authorization: Bearer <token>`
**Permissões**: RH

### `GET /api/empresas/{cnpj}`
**Funcionalidade**: Obter empresa por CNPJ
**Exemplo**: `GET /api/empresas/12345678000190`
**Autenticação**: Requer `Authorization: Bearer <token>`
**Permissões**: RH

### `POST /api/empresas`
**Funcionalidade**: Criar nova empresa
**Campos obrigatórios**: `cnpj`, `id`, `nome`, `endereco`, `telefone`, `email`
**Validações**: CNPJ único, email único
**Exemplo**:
```json
{
  "cnpj": 12345678000190,
  "id": 1,
  "nome": "Tech Solutions LTDA",
  "endereco": "Rua das Flores, 123 - São Paulo/SP",
  "telefone": "(11) 1234-5678",
  "email": "contato@techsolutions.com"
}
```

### `PUT /api/empresas/{cnpj}` e `DELETE /api/empresas/{cnpj}`
**Funcionalidade**: Atualizar e desativar empresa
**Permissões**: RH apenas

---

## 👥 3. GRUPOS (5 Funcionalidades) - Com telefone obrigatório

### `GET /api/grupos`
**Funcionalidade**: Listar grupos
**Filtros**: `?cnpj_empresa=12345678000190`, `?ativos=true/false`
**Retorna**: Grupos com nome da empresa e telefone

### `POST /api/grupos`
**Funcionalidade**: Criar novo grupo
**Campos obrigatórios**: `nome`, `cnpj_empresa`, `telefone`
**Campos opcionais**: `descricao`
**Exemplo**:
```json
{
  "nome": "Desenvolvimento",
  "cnpj_empresa": 12345678000190,
  "telefone": "(11) 1234-5680",
  "descricao": "Equipe de desenvolvimento"
}
```

---

## 👤 4. USUÁRIOS (5 Funcionalidades) - CPF como PK

### `GET /api/usuarios`
**Funcionalidade**: Listar usuários
**Filtros**: 
- `?grupo_id=1` - Usuários de um grupo específico
- `?tipo_usuario=gestor` - Por tipo (rh/gestor/comum)
- `?ativos=true/false` - Por status

### `GET /api/usuarios/{cpf}`
**Funcionalidade**: Obter usuário por CPF
**Exemplo**: `GET /api/usuarios/12345678901`
**Retorna**: Dados completos do usuário

### `POST /api/usuarios`
**Funcionalidade**: Criar novo usuário
**Campos obrigatórios**: `cpf`, `nome`, `email`, `senha`, `grupo_id`, `inicio_na_empresa`, `uf`
**Campos opcionais**: `tipo_usuario`, `flag_gestor`
**Exemplo**:
```json
{
  "cpf": 12345678901,
  "nome": "Maria Silva",
  "email": "maria@techsolutions.com",
  "senha": "123456",
  "grupo_id": 1,
  "inicio_na_empresa": "2020-01-15",
  "uf": "SP",
  "tipo_usuario": "rh",
  "flag_gestor": "N"
}
```

### `PUT /api/usuarios/{cpf}` e `DELETE /api/usuarios/{cpf}`
**Funcionalidade**: Atualizar e desativar usuário
**Validações**: CPF único, email único

---

## 📅 5. EVENTOS (7 Funcionalidades) - Com CPF

### `GET /api/eventos`
**Funcionalidade**: Listar eventos
**Filtros**:
- `?cpf_usuario=12345678901` - Eventos de um usuário
- `?grupo_id=1` - Eventos de um grupo
- `?status=pendente` - Por status

### `POST /api/eventos`
**Funcionalidade**: Criar novo evento
**Campos obrigatórios**: `cpf_usuario`, `data_inicio`, `data_fim`, `id_tipo_ausencia`, `uf`, `aprovado_por`
**Exemplo**:
```json
{
  "cpf_usuario": 12345678901,
  "data_inicio": "2024-12-15",
  "data_fim": "2024-12-19",
  "id_tipo_ausencia": 1,
  "uf": "SP",
  "aprovado_por": 23456789012
}
```

### `POST /api/eventos/{id}/aprovar` e `POST /api/eventos/{id}/rejeitar`
**Funcionalidade**: Aprovar/rejeitar evento
**Requer**: `aprovador_cpf`
**Permissões**: Gestores (flag_gestor='S') e RH

---

## 🌎 6. UFS (3 Funcionalidades) - NOVA

### `GET /api/ufs`
**Funcionalidade**: Listar todas as UFs brasileiras
**Retorna**: Array com código e sigla da UF

### `GET /api/ufs/{uf}`
**Funcionalidade**: Obter UF específica
**Exemplo**: `GET /api/ufs/SP`

### `POST /api/ufs`
**Funcionalidade**: Criar nova UF (RH apenas)
**Campos**: `cod_uf`, `uf`

---

## 📝 7. TIPOS DE AUSÊNCIA (3 Funcionalidades) - NOVA

### `GET /api/tipos-ausencia`
**Funcionalidade**: Listar tipos de ausência configuráveis
**Retorna**: Array com ID, descrição e flag de uso de turno

### `GET /api/tipos-ausencia/{id}`
**Funcionalidade**: Obter tipo específico

### `POST /api/tipos-ausencia`
**Funcionalidade**: Criar novo tipo (RH apenas)
**Campos**: `descricao_ausencia`, `usa_turno`
**Exemplo**:
```json
{
  "descricao_ausencia": "Licença Médica",
  "usa_turno": false
}
```

---

## ⏰ 8. TURNOS (3 Funcionalidades) - NOVA

### `GET /api/turnos`
**Funcionalidade**: Listar turnos disponíveis
**Retorna**: Array com ID e descrição

### `GET /api/turnos/{id}`
**Funcionalidade**: Obter turno específico

### `POST /api/turnos`
**Funcionalidade**: Criar novo turno (RH apenas)
**Campos**: `descricao_ausencia`

---

## 🎉 9. FERIADOS (4 Funcionalidades) - NOVA

### `GET /api/feriados/nacionais`
**Funcionalidade**: Listar feriados nacionais
**Filtros**: `?uf=SP` - Por estado

### `GET /api/feriados/estaduais`
**Funcionalidade**: Listar feriados estaduais
**Filtros**: `?uf=SP` - Por estado

### `POST /api/feriados/nacionais` e `POST /api/feriados/estaduais`
**Funcionalidade**: Criar feriados (RH apenas)
**Campos**: `data_feriado`, `uf`, `descricao_feriado`
**Exemplo**:
```json
{
  "data_feriado": "2024-01-01",
  "uf": "SP",
  "descricao_feriado": "Confraternização Universal"
}
```

---

## 🔒 Sistema de Permissões V2.0

### Usuário RH
- ✅ CRUD completo em empresas (por CNPJ)
- ✅ CRUD completo em grupos
- ✅ CRUD completo em usuários (por CPF)
- ✅ Criação de UFs, tipos de ausência, turnos, feriados
- ✅ Visualização de todos os eventos
- ✅ Aprovação/rejeição de qualquer evento

### Usuário Gestor (flag_gestor = 'S')
- ❌ Sem acesso a empresas
- ✅ Visualização de grupos
- ✅ CRUD de usuários do seu grupo
- ✅ CRUD de eventos do seu grupo
- ✅ Aprovação/rejeição de eventos do grupo

### Usuário Comum (flag_gestor = 'N')
- ❌ Sem acesso a empresas/grupos
- ✅ Visualização de usuários do grupo
- ✅ CRUD dos próprios eventos
- ❌ Sem permissão de aprovação

---

## 🚀 Casos de Uso com Novo Schema

### 1. **Identificação por CPF/CNPJ**
- Usuários identificados por CPF brasileiro
- Empresas identificadas por CNPJ
- Validações de integridade referencial

### 2. **Gestão de Estados (UF)**
- Usuários vinculados a estados brasileiros
- Eventos registrados por UF
- Feriados específicos por estado

### 3. **Tipos de Ausência Configuráveis**
- Administrador pode criar novos tipos
- Configuração de uso de turnos
- Flexibilidade para diferentes empresas

### 4. **Sistema de Feriados Brasileiro**
- Feriados nacionais válidos para todo país
- Feriados estaduais específicos por UF
- Integração com cálculo de dias úteis

---

## 📊 Métricas da API V2.0

- **Total de Endpoints**: 39 (+10 novos)
- **Módulos**: 9 (+3 novos)
- **Novas Tabelas**: 6
- **Chaves Primárias**: CPF/CNPJ
- **Estados Suportados**: 27 UFs
- **Tipos de Dados**: Configuráveis
- **Relacionamentos**: 8 tabelas principais
- **Validações**: 20+ regras de negócio

---

## 🔧 Tecnologias Utilizadas

- **Backend**: Flask + SQLAlchemy 2.0+
- **Banco**: MySQL na GCP Cloud SQL
- **Autenticação**: JWT com CPF como identificador
- **Validação**: Enums + Type Hints + Integridade referencial
- **Arquitetura**: Blueprints modulares
- **ORM**: SQLAlchemy com Mapped types e relacionamentos explícitos

---

## 💡 Próximos Passos

1. **Executar migração**: `python scripts/seed_data_v2.py`
2. **Testar API**: `node test_complete_api_v2.js`
3. **Validar integridade**: Verificar relacionamentos CPF/CNPJ
4. **Documentar mudanças**: Atualizar documentação do cliente
5. **Treinar usuários**: Novo formato de identificadores
