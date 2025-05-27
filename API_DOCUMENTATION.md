# 📚 Documentação Completa da API de Gestão de Eventos

## 🏗️ Visão Geral

API Flask para gestão hierárquica de eventos corporativos com sistema de aprovação baseado em níveis de usuário.

### 🎯 Modelo Hierárquico
```
Empresa → Grupo → Usuário → Evento
```

### 👥 Tipos de Usuário
- **RH**: Acesso total ao sistema
- **Gestor**: Gerencia usuários e eventos do seu grupo
- **Comum**: Gerencia apenas seus próprios eventos

---

## 📊 Resumo de Funcionalidades

| Módulo | Endpoints | Funcionalidades |
|--------|-----------|----------------|
| **Autenticação** | 1 | Login com validação |
| **Empresas** | 5 | CRUD completo |
| **Grupos** | 6 | CRUD + estatísticas |
| **Usuários** | 5 | CRUD com filtros |
| **Eventos** | 7 | CRUD + aprovação |
| **Calendário** | 2 | Visualização de eventos |
| **TOTAL** | **26** | **Funcionalidades** |

---

## 🔐 1. AUTENTICAÇÃO

### `POST /api/auth/login`
**Funcionalidade**: Autenticação de usuários
- **Entrada**: `email`, `senha`
- **Saída**: Dados do usuário autenticado
- **Status**: 200 (sucesso), 401 (credenciais inválidas)

```json
{
  "email": "maria.rh@techsolutions.com",
  "senha": "123456"
}
```

---

## 🏢 2. EMPRESAS (5 Funcionalidades)

### `GET /api/empresas`
**Funcionalidade**: Listar todas as empresas
- **Filtros**: `?ativas=true/false`
- **Retorna**: Array de empresas com estatísticas

### `GET /api/empresas/{id}`
**Funcionalidade**: Obter empresa específica
- **Retorna**: Dados completos da empresa + total de grupos

### `POST /api/empresas`
**Funcionalidade**: Criar nova empresa
- **Campos obrigatórios**: `nome`
- **Campos opcionais**: `cnpj`, `endereco`, `telefone`, `email`
- **Validações**: CNPJ único, email único

### `PUT /api/empresas/{id}`
**Funcionalidade**: Atualizar empresa existente
- **Permite**: Atualização parcial de qualquer campo
- **Validações**: Integridade de dados únicos

### `DELETE /api/empresas/{id}`
**Funcionalidade**: Desativar empresa (soft delete)
- **Ação**: Define `ativa = false`
- **Preserva**: Dados históricos

---

## 👥 3. GRUPOS (6 Funcionalidades)

### `GET /api/grupos`
**Funcionalidade**: Listar grupos
- **Filtros**: `?empresa_id=1`, `?ativos=true/false`
- **Retorna**: Grupos com nome da empresa e total de usuários

### `GET /api/grupos/{id}`
**Funcionalidade**: Obter grupo específico
- **Retorna**: Dados completos do grupo + estatísticas

### `POST /api/grupos`
**Funcionalidade**: Criar novo grupo
- **Campos obrigatórios**: `nome`, `empresa_id`
- **Campos opcionais**: `descricao`

### `PUT /api/grupos/{id}`
**Funcionalidade**: Atualizar grupo existente
- **Permite**: Atualização de nome, descrição, empresa

### `DELETE /api/grupos/{id}`
**Funcionalidade**: Desativar grupo (soft delete)
- **Ação**: Define `ativo = false`

### `GET /api/grupos/{id}/estatisticas`
**Funcionalidade**: Estatísticas detalhadas do grupo
- **Retorna**: Total de usuários, eventos pendentes/aprovados

---

## 👤 4. USUÁRIOS (5 Funcionalidades)

### `GET /api/usuarios`
**Funcionalidade**: Listar usuários com filtros avançados
- **Filtros**: 
  - `?grupo_id=1` - Usuários de um grupo específico
  - `?tipo_usuario=gestor` - Por tipo (rh/gestor/comum)
  - `?ativos=true/false` - Por status
- **Retorna**: Lista com nome do grupo e férias tiradas

### `GET /api/usuarios/{id}`
**Funcionalidade**: Obter usuário específico
- **Retorna**: Dados completos + férias tiradas no ano

### `POST /api/usuarios`
**Funcionalidade**: Criar novo usuário
- **Campos obrigatórios**: `nome`, `email`, `senha`, `inicio_na_empresa`
- **Campos opcionais**: `tipo_usuario`, `grupo_id`
- **Validações**: Email único, tipo válido

### `PUT /api/usuarios/{id}`
**Funcionalidade**: Atualizar usuário existente
- **Permite**: Atualização de qualquer campo incluindo senha
- **Validações**: Integridade de dados

### `DELETE /api/usuarios/{id}`
**Funcionalidade**: Desativar usuário (soft delete)
- **Ação**: Define `ativo = false`

---

## 📅 5. EVENTOS (7 Funcionalidades)

### `GET /api/eventos`
**Funcionalidade**: Listar eventos com filtros
- **Filtros**:
  - `?usuario_id=1` - Eventos de um usuário
  - `?grupo_id=1` - Eventos de um grupo
  - `?status=pendente` - Por status (pendente/aprovado/rejeitado)
- **Retorna**: Lista com nome do usuário e aprovador

### `GET /api/eventos/{id}`
**Funcionalidade**: Obter evento específico
- **Retorna**: Dados completos + histórico de aprovação

### `POST /api/eventos`
**Funcionalidade**: Criar novo evento
- **Campos obrigatórios**: `usuario_id`, `data_inicio`, `data_fim`, `tipo_ausencia`
- **Campos opcionais**: `turno`, `descricao`
- **Status inicial**: `pendente`

### `PUT /api/eventos/{id}`
**Funcionalidade**: Atualizar evento existente
- **Permite**: Modificação de datas, tipo, descrição
- **Recalcula**: Total de dias automaticamente

### `DELETE /api/eventos/{id}`
**Funcionalidade**: Deletar evento (hard delete)
- **Ação**: Remove permanentemente do banco

### `POST /api/eventos/{id}/aprovar`
**Funcionalidade**: Aprovar evento
- **Requer**: `aprovador_id`, `observacoes` (opcional)
- **Permissões**: Apenas gestores e RH
- **Registra**: Data e observações da aprovação

### `POST /api/eventos/{id}/rejeitar`
**Funcionalidade**: Rejeitar evento
- **Requer**: `aprovador_id`, `observacoes` (opcional)
- **Permissões**: Apenas gestores e RH
- **Registra**: Data e motivo da rejeição

---

## 📊 6. CALENDÁRIO (2 Funcionalidades)

### `GET /api/calendario`
**Funcionalidade**: Calendário geral de eventos
- **Filtros**: `?apenas_aprovados=true/false`
- **Formato**: Compatível com bibliotecas de calendário (FullCalendar)
- **Cores**: Por tipo de ausência

### `GET /api/calendario/grupo/{id}`
**Funcionalidade**: Calendário específico de um grupo
- **Filtros**: `?apenas_aprovados=true/false`
- **Retorna**: Eventos + metadados do grupo
- **Uso**: Calendário compartilhado do grupo

---

## 🎨 Tipos de Dados Suportados

### Tipos de Usuário
- `rh` - Recursos Humanos
- `gestor` - Gestor de Grupo
- `comum` - Usuário Comum

### Tipos de Ausência
- `Férias`
- `Assiduidade`
- `Plantão`
- `Licença Maternidade/Paternidade`
- `Evento Especial`
- `Licença (Geral)`

### Turnos
- `Dia`
- `Noite`
- `Madrugada`

### Status de Evento
- `pendente` - Aguardando aprovação
- `aprovado` - Aprovado pelo gestor/RH
- `rejeitado` - Rejeitado pelo gestor/RH

---

## 🔒 Sistema de Permissões

### Usuário RH
- ✅ CRUD completo em empresas
- ✅ CRUD completo em grupos
- ✅ CRUD completo em usuários
- ✅ Visualização de todos os eventos
- ✅ Aprovação/rejeição de qualquer evento

### Usuário Gestor
- ❌ Sem acesso a empresas
- ✅ Visualização de grupos
- ✅ CRUD de usuários do seu grupo
- ✅ CRUD de eventos do seu grupo
- ✅ Aprovação/rejeição de eventos do grupo
- ✅ Calendário compartilhado do grupo

### Usuário Comum
- ❌ Sem acesso a empresas/grupos
- ✅ Visualização de usuários do grupo
- ✅ CRUD dos próprios eventos
- ✅ Visualização do calendário do grupo
- ❌ Sem permissão de aprovação

---

## 📈 Funcionalidades Avançadas

### 1. **Cálculo Automático de Férias**
- Soma dias de férias aprovados no ano atual
- Retornado em todos os endpoints de usuário

### 2. **Estatísticas de Grupo**
- Total de usuários ativos
- Eventos pendentes de aprovação
- Eventos aprovados
- Usuários por status

### 3. **Validações de Integridade**
- CNPJ único por empresa
- Email único por usuário
- Relacionamentos consistentes

### 4. **Soft Delete**
- Empresas e usuários são desativados, não deletados
- Preserva histórico e integridade referencial

### 5. **Formatação para Calendário**
- Eventos formatados para bibliotecas de calendário
- Cores por tipo de ausência
- Metadados estendidos

### 6. **Sistema de Aprovação Completo**
- Histórico de aprovações
- Observações do aprovador
- Data e hora da decisão

---

## 🚀 Casos de Uso Principais

### 1. **Gestão de Férias Corporativas**
- Funcionários solicitam férias
- Gestores aprovam/rejeitam
- RH monitora o processo
- Calendário compartilhado para planejamento

### 2. **Controle de Ausências**
- Registro de faltas, consultas médicas
- Aprovação por gestores
- Relatórios para RH

### 3. **Gestão de Plantões**
- Escala de plantões por turno
- Visualização em calendário
- Controle por grupo/equipe

### 4. **Administração Multi-Empresa**
- Suporte a múltiplas empresas
- Grupos independentes por empresa
- Gestão hierárquica

---

## 📊 Métricas da API

- **Total de Endpoints**: 26
- **Módulos**: 6
- **Tipos de Operação**: CRUD + Aprovação + Relatórios
- **Níveis de Permissão**: 3
- **Tipos de Dados**: 12 enums
- **Relacionamentos**: 4 tabelas principais
- **Validações**: 15+ regras de negócio

---

## 🔧 Tecnologias Utilizadas

- **Backend**: Flask + SQLAlchemy
- **Banco**: SQLite (desenvolvimento)
- **Autenticação**: Hash de senhas (Werkzeug)
- **Validação**: Enums + Type Hints
- **Arquitetura**: Blueprints modulares
- **ORM**: SQLAlchemy 2.0+ com Mapped types
