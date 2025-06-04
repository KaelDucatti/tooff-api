# 🔍 Documentação do Sistema de Validação de Integridade

## 🏗️ Visão Geral

O sistema de validação de integridade é um componente crítico da API de Gestão de Eventos v2.0, responsável por verificar a consistência e validade dos dados, especialmente CPFs e CNPJs que agora são usados como chaves primárias.

## 🚀 Funcionalidades Principais

### 1. Validação de CPF/CNPJ
- Verificação de formato e dígitos verificadores de CPF
- Verificação de formato e dígitos verificadores de CNPJ
- Formatação para exibição amigável

### 2. Verificação de Integridade Referencial
- Detecção de usuários órfãos (sem grupo válido)
- Detecção de grupos órfãos (sem empresa válida)
- Detecção de eventos órfãos (sem usuário válido)
- Verificação de aprovadores inconsistentes

### 3. Detecção de Duplicatas
- Identificação de CPFs duplicados
- Identificação de CNPJs duplicados

### 4. Validação de UF
- Verificação de referências válidas de UF em usuários
- Verificação de referências válidas de UF em eventos

### 5. Geração de Relatórios
- Relatórios detalhados em formato console
- Relatórios em formato JSON
- Estatísticas gerais do banco de dados

## 📋 Componentes do Sistema

### 1. CPF/CNPJ Validator (`cpf_cnpj_validator.py`)

Responsável pela validação matemática e formatação de CPFs e CNPJs.

**Funções principais:**
- `validar_cpf(cpf: str) -> bool`: Valida um CPF brasileiro
- `validar_cnpj(cnpj: str) -> bool`: Valida um CNPJ brasileiro
- `formatar_cpf(cpf: int) -> str`: Formata CPF para exibição (ex: 123.456.789-01)
- `formatar_cnpj(cnpj: int) -> str`: Formata CNPJ para exibição (ex: 12.345.678/0001-90)
- `cpf_para_int(cpf: str) -> int`: Converte CPF string para int
- `cnpj_para_int(cnpj: str) -> int`: Converte CNPJ string para int

### 2. Integrity Checker (`integrity_checker.py`)

Realiza verificações de integridade no banco de dados.

**Classes:**
- `IntegrityReport`: Armazena resultados das verificações
- `CPFCNPJIntegrityChecker`: Executa as verificações de integridade

**Métodos principais de verificação:**
- `check_cpf_format_validity()`: Verifica formato de CPFs
- `check_cnpj_format_validity()`: Verifica formato de CNPJs
- `check_duplicate_cpfs()`: Verifica CPFs duplicados
- `check_duplicate_cnpjs()`: Verifica CNPJs duplicados
- `check_orphaned_usuarios()`: Verifica usuários órfãos
- `check_orphaned_grupos()`: Verifica grupos órfãos
- `check_orphaned_eventos()`: Verifica eventos órfãos
- `check_invalid_uf_references()`: Verifica referências de UF
- `check_inconsistent_aprovadores()`: Verifica aprovadores inconsistentes
- `generate_statistics()`: Gera estatísticas do banco
- `run_all_checks()`: Executa todas as verificações

### 3. Report Generator (`report_generator.py`)

Gera relatórios a partir dos resultados das verificações.

**Métodos principais:**
- `generate_console_report(report: IntegrityReport) -> str`: Gera relatório para console
- `generate_json_report(report: IntegrityReport) -> str`: Gera relatório em formato JSON
- `save_report_to_file(report: IntegrityReport, filename: Optional[str] = None) -> str`: Salva relatório em arquivo

## 🚀 Como Utilizar

### Via Script de Linha de Comando

1. **Verificar integridade:**
\`\`\`bash
python scripts/validate_integrity.py
\`\`\`

Opções disponíveis:
- `--database` ou `-d`: URL do banco de dados (padrão: SQLite local)
- `--output` ou `-o`: Arquivo de saída para relatório JSON
- `--quiet` ou `-q`: Modo silencioso (apenas erros)

2. **Corrigir problemas de integridade:**
\`\`\`bash
python scripts/fix_integrity_issues.py
\`\`\`

Este script:
- Executa verificações de integridade
- Identifica problemas
- Pergunta se deve aplicar correções automáticas
- Aplica correções quando possível
- Executa nova verificação para confirmar resultados

### Via API (apenas RH)

1. **Verificar integridade:**
\`\`\`
GET /api/validation/integrity-check
\`\`\`

2. **Obter relatório formatado:**
\`\`\`
GET /api/validation/integrity-report
\`\`\`

## 📊 Estrutura do Relatório

O relatório de integridade contém as seguintes seções:

### 1. Resumo
- Timestamp da verificação
- Total de erros
- Total de avisos
- Total de informações

### 2. Estatísticas
- Total de empresas (ativas/inativas)
- Total de grupos
- Total de usuários (ativos/inativos)
- Total de eventos
- Total de UFs
- Usuários por tipo
- Eventos por status

### 3. Erros
Lista de erros encontrados, como:
- CPFs/CNPJs inválidos
- Duplicatas
- Registros órfãos
- Referências inválidas

### 4. Avisos
Lista de situações que merecem atenção, mas não são erros críticos.

### 5. Informações
Lista de verificações bem-sucedidas.

## 🔧 Correções Automáticas

O sistema pode aplicar as seguintes correções automáticas:

1. **Usuários órfãos**: Desativa usuários sem grupo válido
2. **Eventos órfãos**: Remove eventos sem usuário válido
3. **Grupos órfãos**: Desativa grupos sem empresa válida

## 🔍 Exemplo de Relatório Console

\`\`\`
================================================================================
🔍 RELATÓRIO DE INTEGRIDADE CPF/CNPJ
================================================================================
📅 Data/Hora: 01/06/2023 10:00:00

📊 RESUMO:
   ❌ Erros: 1
   ⚠️  Avisos: 1
   ℹ️  Informações: 7

📈 ESTATÍSTICAS DO BANCO:
   🏢 Empresas: 1 (Ativas: 1, Inativas: 0)
   👥 Grupos: 3
   👤 Usuários: 5 (Ativos: 5, Inativos: 0)
   📅 Eventos: 6
   🌎 UFs: 27
   👤 Usuários por tipo:
      - rh: 1
      - gestor: 1
      - comum: 3
   📅 Eventos por status:
      - pendente: 3
      - aprovado: 3
      - rejeitado: 0

❌ ERROS ENCONTRADOS:
   1. [ORPHANED_EVENTOS] Encontrados 1 eventos órfãos
      Eventos órfãos: 1

⚠️  AVISOS:
   1. [EVENTOS_PENDENTES] Existem 3 eventos pendentes de aprovação

✅ VERIFICAÇÕES APROVADAS:
   ✓ [CPF_FORMAT] Todos os CPFs no banco são válidos
   ✓ [CNPJ_FORMAT] Todos os CNPJs no banco são válidos
   ✓ [CPF_DUPLICATE] Nenhum CPF duplicado encontrado
   ✓ [CNPJ_DUPLICATE] Nenhum CNPJ duplicado encontrado
   ✓ [ORPHANED_USUARIOS] Nenhum usuário órfão encontrado
   ✓ [ORPHANED_GRUPOS] Nenhum grupo órfão encontrado
   ✓ [INCONSISTENT_APROVADORES] Todos os aprovadores de eventos são válidos

🚨 AÇÃO NECESSÁRIA: Foram encontrados erros que precisam ser corrigidos!
================================================================================
\`\`\`

## 📊 Exemplo de Relatório JSON

\`\`\`json
{
  "summary": {
    "timestamp": "2023-06-01T10:00:00",
    "total_errors": 1,
    "total_warnings": 1,
    "total_info": 7,
    "statistics": {
      "total_empresas": 1,
      "total_grupos": 3,
      "total_usuarios": 5,
      "total_eventos": 6,
      "total_ufs": 27
    }
  },
  "errors": [
    {
      "category": "ORPHANED_EVENTOS",
      "message": "Encontrados 1 eventos órfãos",
      "details": {
        "orphaned_eventos": [
          {
            "id": 6,
            "cpf_usuario": 99999999999,
            "cpf_formatado": "999.999.999-99",
            "data_inicio": "2024-07-20",
            "data_fim": "2024-07-25",
            "status": "pendente"
          }
        ]
      },
      "severity": "ERROR"
    }
  ],
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
    },
    // ... outros itens de informação
  ],
  "statistics": {
    "total_empresas": 1,
    "total_grupos": 3,
    "total_usuarios": 5,
    "total_eventos": 6,
    "total_ufs": 27,
    "usuarios_por_tipo": {
      "rh": 1,
      "gestor": 1,
      "comum": 3
    },
    "eventos_por_status": {
      "pendente": 3,
      "aprovado": 3,
      "rejeitado": 0
    },
    "empresas_ativas": 1,
    "empresas_inativas": 0,
    "usuarios_ativos": 5,
    "usuarios_inativos": 0
  }
}
\`\`\`

## 🔧 Melhores Práticas

1. **Execute verificações regularmente**
   - Recomendamos verificar a integridade semanalmente
   - Considere automatizar via cron job

2. **Corrija problemas imediatamente**
   - Problemas de integridade podem causar comportamentos inesperados
   - Use o script `fix_integrity_issues.py` para correções automáticas

3. **Mantenha backups antes de correções**
   - Sempre faça backup do banco antes de aplicar correções automáticas

4. **Monitore relatórios**
   - Observe tendências nos relatórios
   - Investigue aumentos repentinos em avisos ou erros

5. **Valide CPF/CNPJ na entrada**
   - Use as funções de validação no frontend também
   - Evite problemas de integridade na origem
\`\`\`

Let's create a migration guide:
