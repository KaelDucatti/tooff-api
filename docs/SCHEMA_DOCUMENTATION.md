# 📊 Documentação do Schema do Banco de Dados v2.0

## 🏗️ Visão Geral

Este documento descreve o schema do banco de dados da API de Gestão de Eventos v2.0, que utiliza CPF e CNPJ como chaves primárias. O sistema suporta MySQL na GCP Cloud SQL (produção) e SQLite (desenvolvimento).

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

## 📝 Diagrama de Entidade-Relacionamento

\`\`\`
+----------------+       +---------------+       +----------------+       +---------------+
|      UF        |       |    EMPRESA    |       |     GRUPO      |       |    USUARIO    |
+----------------+       +---------------+       +----------------+       +---------------+
| PK: uf (CHAR)  |       | PK: cnpj (BIG)|       | PK: id (INT)   |       | PK: cpf (BIG) |
| cod_uf (INT)   |<---+  | id (INT)      |       | nome (STR)     |       | nome (STR)    |
+----------------+    |  | nome (STR)    |       | descricao (TXT)|       | email (STR)   |
                      |  | endereco (TXT)|       | cnpj_empresa   |------>| senha_hash    |
                      |  | telefone (STR)|<------| telefone (STR) |       | tipo_usuario  |
                      |  | email (STR)   |       | ativo (BOOL)   |       | grupo_id      |----+
                      |  | ativa (BOOL)  |       | criado_em      |       | inicio_empresa|    |
                      |  | criado_em     |       +----------------+       | ativo (BOOL)  |    |
                      |  +---------------+                                | criado_em     |    |
                      |                                                   | UF            |----+
                      +-------------------------------------------------->| flag_gestor   |    |
                      |                                                   +---------------+    |
                      |                                                                        |
                      |  +----------------+       +----------------+                           |
                      |  | TIPO_AUSENCIA  |       |     EVENTO     |                           |
                      |  +----------------+       +----------------+                           |
                      |  | PK: id (INT)   |       | PK: id (INT)   |                           |
                      |  | descricao (STR)|<------| cpf_usuario    |---------------------------+
                      |  | usa_turno      |       | data_inicio    |                           |
                      |  +----------------+       | data_fim       |                           |
                      |         ^                 | total_dias     |                           |
                      |         |                 | id_tipo_ausenc |                           |
                      |  +------+------+          | status (STR)   |                           |
                      |  |AUSENCIA_TURNO|          | criado_em      |                           |
                      |  +-------------+          | UF             |---------------------------+
                      |  | id_tipo_aus  |          | aprovado_por   |---------------------------+
                      |  | id_turno     |          +----------------+
                      |  +------+------+
                      |         |
                      |         v
                      |  +----------------+
                      |  |     TURNO      |
                      |  +----------------+
                      |  | PK: id (INT)   |
                      |  | descricao (STR)|
                      |  +----------------+
                      |
                      |  +----------------+       +----------------+
                      |  |FERIADO_NACIONAL|       |FERIADO_ESTADUAL|
                      |  +----------------+       +----------------+
                      |  | PK: data (DATE)|       | PK: data (DATE)|
                      +->| PK: uf (CHAR)  |       | PK: uf (CHAR)  |<-+
                         | descricao (STR)|       | descricao (STR)|  |
                         +----------------+       +----------------+  |
                                                                      |
                                                                      +
\`\`\`

## 📋 Descrição Detalhada das Tabelas

### 1. UF

**Descrição**: Armazena os estados brasileiros (Unidades Federativas).

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| `uf` | CHAR(2) | Sigla do estado | PK, NOT NULL |
| `cod_uf` | INTEGER | Código numérico do estado | NOT NULL |

**Relacionamentos**:
- Um para muitos com `Usuario`
- Um para muitos com `Evento`
- Um para muitos com `FeriadoNacional`
- Um para muitos com `FeriadoEstadual`

### 2. EMPRESA

**Descrição**: Armazena informações das empresas.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| `cnpj` | BIGINT | CNPJ da empresa | PK, NOT NULL |
| `id` | INTEGER | ID interno da empresa | UNIQUE, NOT NULL |
| `nome` | VARCHAR(100) | Nome da empresa | NOT NULL |
| `endereco` | TEXT | Endereço completo | NOT NULL |
| `telefone` | VARCHAR(20) | Telefone de contato | NOT NULL |
| `email` | VARCHAR(100) | Email de contato | NOT NULL |
| `ativa` | BOOLEAN | Status da empresa | NOT NULL, DEFAULT TRUE |
| `criado_em` | DATE | Data de criação | NOT NULL |

**Relacionamentos**:
- Um para muitos com `Grupo`

### 3. GRUPO

**Descrição**: Armazena grupos/departamentos das empresas.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| `id` | INTEGER | ID do grupo | PK, AUTOINCREMENT, NOT NULL |
| `nome` | VARCHAR(100) | Nome do grupo | NOT NULL |
| `descricao` | TEXT | Descrição do grupo | NULL |
| `cnpj_empresa` | BIGINT | CNPJ da empresa | FK (empresa.cnpj), NOT NULL |
| `telefone` | VARCHAR(20) | Telefone do grupo | NOT NULL |
| `ativo` | BOOLEAN | Status do grupo | NOT NULL, DEFAULT TRUE |
| `criado_em` | DATE | Data de criação | NOT NULL |

**Relacionamentos**:
- Muitos para um com `Empresa`
- Um para muitos com `Usuario`

### 4. TIPO_AUSENCIA

**Descrição**: Armazena tipos de ausência configuráveis.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| `id_tipo_ausencia` | INTEGER | ID do tipo | PK, AUTOINCREMENT, NOT NULL |
| `descricao_ausencia` | VARCHAR(50) | Descrição do tipo | NOT NULL |
| `usa_turno` | BOOLEAN | Se usa turno | NOT NULL, DEFAULT FALSE |

**Relacionamentos**:
- Um para muitos com `Evento`
- Muitos para muitos com `Turno` (via `ausencia_turno`)

### 5. TURNO

**Descrição**: Armazena turnos de trabalho.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| `id` | INTEGER | ID do turno | PK, AUTOINCREMENT, NOT NULL |
| `descricao_ausencia` | VARCHAR(20) | Descrição do turno | NOT NULL |

**Relacionamentos**:
- Muitos para muitos com `TipoAusencia` (via `ausencia_turno`)

### 6. AUSENCIA_TURNO

**Descrição**: Tabela de relacionamento entre tipos de ausência e turnos.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| `id_tipo_ausencia` | INTEGER | ID do tipo de ausência | PK, FK (tipo_ausencia.id_tipo_ausencia), NOT NULL |
| `id_turno` | INTEGER | ID do turno | PK, FK (turno.id), NOT NULL |

### 7. USUARIO

**Descrição**: Armazena informações dos usuários.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| `cpf` | BIGINT | CPF do usuário | PK, NOT NULL |
| `nome` | VARCHAR(100) | Nome completo | NOT NULL |
| `email` | VARCHAR(100) | Email | NOT NULL |
| `senha_hash` | VARCHAR(515) | Hash da senha | NOT NULL |
| `tipo_usuario` | VARCHAR(10) | Tipo (rh/gestor/comum) | NOT NULL |
| `grupo_id` | INTEGER | ID do grupo | FK (grupo.id), NOT NULL |
| `inicio_na_empresa` | DATE | Data de início | NOT NULL |
| `ativo` | BOOLEAN | Status do usuário | NOT NULL, DEFAULT TRUE |
| `criado_em` | DATETIME | Data/hora de criação | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| `UF` | CHAR(2) | Estado do usuário | FK (uf.uf), NOT NULL |
| `flag_gestor` | CHAR(1) | Se é gestor (S/N) | NOT NULL |

**Relacionamentos**:
- Muitos para um com `Grupo`
- Muitos para um com `UF`
- Um para muitos com `Evento` (como usuário)
- Um para muitos com `Evento` (como aprovador)

### 8. EVENTO

**Descrição**: Armazena eventos de ausência dos usuários.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| `id` | INTEGER | ID do evento | PK, AUTOINCREMENT, NOT NULL |
| `cpf_usuario` | BIGINT | CPF do usuário | FK (usuario.cpf), NOT NULL |
| `data_inicio` | DATE | Data de início | NOT NULL |
| `data_fim` | DATE | Data de término | NOT NULL |
| `total_dias` | INTEGER | Total de dias | NOT NULL |
| `id_tipo_ausencia` | INTEGER | Tipo de ausência | FK (tipo_ausencia.id_tipo_ausencia), NOT NULL |
| `status` | VARCHAR(15) | Status (pendente/aprovado/rejeitado) | NOT NULL, DEFAULT 'pendente' |
| `criado_em` | DATETIME | Data/hora de criação | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| `UF` | CHAR(2) | Estado do evento | FK (uf.uf), NOT NULL |
| `aprovado_por` | BIGINT | CPF do aprovador | FK (usuario.cpf), NOT NULL |

**Relacionamentos**:
- Muitos para um com `Usuario` (cpf_usuario)
- Muitos para um com `Usuario` (aprovado_por)
