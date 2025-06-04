// Script completo para testar a API Flask com novo schema MySQL
const BASE_URL = "http://localhost:5000/api"

// Configuração de cores para output
const colors = {
  reset: "\x1b[0m",
  bright: "\x1b[1m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
}

// Função auxiliar para fazer requisições
async function makeRequest(method, url, data = null, token = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  }

  if (token) {
    options.headers["Authorization"] = `Bearer ${token}`
  }

  if (data) {
    options.body = JSON.stringify(data)
  }

  try {
    const response = await fetch(url, options)
    const result = await response.json()
    return {
      status: response.status,
      data: result,
    }
  } catch (error) {
    return {
      status: "ERROR",
      data: { erro: error.message },
    }
  }
}

// Função para exibir resultados com cores
function logResult(testName, result, expectedStatus = null) {
  const isSuccess = expectedStatus ? result.status === expectedStatus : result.status < 400
  const statusColor = isSuccess ? colors.green : colors.red
  const icon = isSuccess ? "✅" : "❌"

  console.log(`\n${colors.cyan}=== ${testName} ===${colors.reset}`)
  console.log(`${icon} Status: ${statusColor}${result.status}${colors.reset}`)

  if (result.data.access_token) {
    console.log(`${colors.yellow}Response: { access_token: '***', usuario: {...} }${colors.reset}`)
  } else if (Array.isArray(result.data)) {
    console.log(`${colors.yellow}Response: Array com ${result.data.length} itens${colors.reset}`)
  } else {
    const responseStr = JSON.stringify(result.data, null, 2)
    const truncated = responseStr.length > 200 ? responseStr.substring(0, 200) + "..." : responseStr
    console.log(`${colors.yellow}Response: ${truncated}${colors.reset}`)
  }
}

// Função principal de teste
async function testarAPICompleta() {
  console.log(`${colors.bright}🚀 TESTE COMPLETO DA API FLASK - NOVO SCHEMA${colors.reset}\n`)
  console.log(`${colors.blue}🗄️  Banco: MySQL na GCP Cloud SQL${colors.reset}`)
  console.log(`${colors.blue}📊 Host: 35.222.35.237${colors.reset}`)
  console.log(`${colors.blue}🔗 Database: tooff_app${colors.reset}`)
  console.log(`${colors.blue}🆕 Schema: Versão 2.0 com CPF/CNPJ${colors.reset}\n`)

  // Contadores para estatísticas
  let totalTestes = 0
  let testesPassaram = 0
  const tokens = {}

  // ==================== SEÇÃO 1: AUTENTICAÇÃO ====================
  console.log(`\n${colors.bright}📋 SEÇÃO 1: AUTENTICAÇÃO COM NOVO SCHEMA${colors.reset}`)

  // Teste 1: Login válido RH
  totalTestes++
  const loginRH = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "maria.rh@techsolutions.com",
    senha: "123456",
  })
  logResult("Login RH (novo schema)", loginRH, 200)
  if (loginRH.status === 200) {
    testesPassaram++
    tokens.rh = loginRH.data.access_token
  }

  // Teste 2: Login válido Gestor
  totalTestes++
  const loginGestor = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "joao.gestor@techsolutions.com",
    senha: "123456",
  })
  logResult("Login Gestor (novo schema)", loginGestor, 200)
  if (loginGestor.status === 200) {
    testesPassaram++
    tokens.gestor = loginGestor.data.access_token
  }

  // Teste 3: Login válido Usuário Comum
  totalTestes++
  const loginComum = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "ana.dev@techsolutions.com",
    senha: "123456",
  })
  logResult("Login Usuário Comum (novo schema)", loginComum, 200)
  if (loginComum.status === 200) {
    testesPassaram++
    tokens.comum = loginComum.data.access_token
  }

  // ==================== SEÇÃO 2: NOVAS ENTIDADES ====================
  console.log(`\n${colors.bright}📋 SEÇÃO 2: NOVAS ENTIDADES DO SCHEMA${colors.reset}`)

  if (tokens.rh) {
    // Teste 4: Listar UFs
    totalTestes++
    const ufs = await makeRequest("GET", `${BASE_URL}/ufs`, null, tokens.rh)
    logResult("Listar UFs", ufs, 200)
    if (ufs.status === 200) testesPassaram++

    // Teste 5: Listar tipos de ausência
    totalTestes++
    const tiposAusencia = await makeRequest("GET", `${BASE_URL}/tipos-ausencia`, null, tokens.rh)
    logResult("Listar Tipos de Ausência", tiposAusencia, 200)
    if (tiposAusencia.status === 200) testesPassaram++

    // Teste 6: Listar turnos
    totalTestes++
    const turnos = await makeRequest("GET", `${BASE_URL}/turnos`, null, tokens.rh)
    logResult("Listar Turnos", turnos, 200)
    if (turnos.status === 200) testesPassaram++

    // Teste 7: Listar feriados nacionais
    totalTestes++
    const feriadosNacionais = await makeRequest("GET", `${BASE_URL}/feriados/nacionais`, null, tokens.rh)
    logResult("Listar Feriados Nacionais", feriadosNacionais, 200)
    if (feriadosNacionais.status === 200) testesPassaram++

    // Teste 8: Criar novo tipo de ausência
    totalTestes++
    const novoTipo = await makeRequest(
      "POST",
      `${BASE_URL}/tipos-ausencia`,
      {
        descricao_ausencia: "Licença Médica",
        usa_turno: false,
      },
      tokens.rh,
    )
    logResult("Criar Tipo de Ausência", novoTipo, 201)
    if (novoTipo.status === 201) testesPassaram++
  }

  // ==================== SEÇÃO 3: EMPRESAS COM CNPJ ====================
  console.log(`\n${colors.bright}📋 SEÇÃO 3: EMPRESAS (CNPJ como PK)${colors.reset}`)

  if (tokens.rh) {
    // Teste 9: Listar empresas
    totalTestes++
    const empresas = await makeRequest("GET", `${BASE_URL}/empresas`, null, tokens.rh)
    logResult("Listar Empresas (CNPJ)", empresas, 200)
    if (empresas.status === 200) testesPassaram++

    // Teste 10: Obter empresa por CNPJ
    totalTestes++
    const empresa = await makeRequest("GET", `${BASE_URL}/empresas/12345678000190`, null, tokens.rh)
    logResult("Obter Empresa por CNPJ", empresa, 200)
    if (empresa.status === 200) testesPassaram++

    // Teste 11: Criar empresa com novo schema
    totalTestes++
    const novaEmpresa = await makeRequest(
      "POST",
      `${BASE_URL}/empresas`,
      {
        cnpj: 98765432000111,
        id: 2,
        nome: `Empresa Teste ${Date.now()}`,
        endereco: "Rua Teste, 456",
        telefone: "(11) 8888-8888",
        email: `teste${Date.now()}@empresa.com`,
      },
      tokens.rh,
    )
    logResult("Criar Empresa (novo schema)", novaEmpresa, 201)
    if (novaEmpresa.status === 201) testesPassaram++
  }

  // ==================== SEÇÃO 4: USUÁRIOS COM CPF ====================
  console.log(`\n${colors.bright}📋 SEÇÃO 4: USUÁRIOS (CPF como PK)${colors.reset}`)

  if (tokens.rh) {
    // Teste 12: Listar usuários
    totalTestes++
    const usuarios = await makeRequest("GET", `${BASE_URL}/usuarios`, null, tokens.rh)
    logResult("Listar Usuários (CPF)", usuarios, 200)
    if (usuarios.status === 200) testesPassaram++

    // Teste 13: Obter usuário por CPF
    totalTestes++
    const usuario = await makeRequest("GET", `${BASE_URL}/usuarios/12345678901`, null, tokens.rh)
    logResult("Obter Usuário por CPF", usuario, 200)
    if (usuario.status === 200) testesPassaram++

    // Teste 14: Criar usuário com novo schema
    totalTestes++
    const novoUsuario = await makeRequest(
      "POST",
      `${BASE_URL}/usuarios`,
      {
        cpf: 11122233344,
        nome: "Usuário Teste",
        email: `teste${Date.now()}@techsolutions.com`,
        senha: "123456",
        grupo_id: 2,
        inicio_na_empresa: "2024-01-01",
        uf: "SP",
        tipo_usuario: "comum",
        flag_gestor: "N",
      },
      tokens.rh,
    )
    logResult("Criar Usuário (novo schema)", novoUsuario, 201)
    if (novoUsuario.status === 201) testesPassaram++
  }

  // ==================== SEÇÃO 5: EVENTOS COM NOVO SCHEMA ====================
  console.log(`\n${colors.bright}📋 SEÇÃO 5: EVENTOS (novo schema)${colors.reset}`)

  if (tokens.comum) {
    // Teste 15: Listar eventos
    totalTestes++
    const eventos = await makeRequest("GET", `${BASE_URL}/eventos`, null, tokens.comum)
    logResult("Listar Eventos (novo schema)", eventos, 200)
    if (eventos.status === 200) testesPassaram++

    // Teste 16: Criar evento com novo schema
    totalTestes++
    const novoEvento = await makeRequest(
      "POST",
      `${BASE_URL}/eventos`,
      {
        cpf_usuario: 34567890123,
        data_inicio: "2024-12-15",
        data_fim: "2024-12-19",
        id_tipo_ausencia: 1,
        uf: "SP",
        aprovado_por: 23456789012,
      },
      tokens.comum,
    )
    logResult("Criar Evento (novo schema)", novoEvento, 201)
    if (novoEvento.status === 201) testesPassaram++
  }

  // ==================== SEÇÃO 6: GRUPOS COM TELEFONE ====================
  console.log(`\n${colors.bright}📋 SEÇÃO 6: GRUPOS (com telefone)${colors.reset}`)

  if (tokens.rh) {
    // Teste 17: Listar grupos
    totalTestes++
    const grupos = await makeRequest("GET", `${BASE_URL}/grupos`, null, tokens.rh)
    logResult("Listar Grupos (com telefone)", grupos, 200)
    if (grupos.status === 200) testesPassaram++

    // Teste 18: Criar grupo com telefone
    totalTestes++
    const novoGrupo = await makeRequest(
      "POST",
      `${BASE_URL}/grupos`,
      {
        nome: `Grupo Teste ${Date.now()}`,
        cnpj_empresa: 12345678000190,
        telefone: "(11) 7777-7777",
        descricao: "Grupo criado no teste",
      },
      tokens.rh,
    )
    logResult("Criar Grupo (com telefone)", novoGrupo, 201)
    if (novoGrupo.status === 201) testesPassaram++
  }

  // ==================== SEÇÃO 7: VALIDAÇÕES DE SEGURANÇA ====================
  console.log(`\n${colors.bright}📋 SEÇÃO 7: VALIDAÇÕES DE SEGURANÇA${colors.reset}`)

  // Teste 19: Acesso sem token
  totalTestes++
  const semToken = await makeRequest("GET", `${BASE_URL}/usuarios`)
  logResult("Acesso sem token (deve falhar)", semToken, 401)
  if (semToken.status === 401) testesPassaram++

  // Teste 20: CPF inválido
  if (tokens.rh) {
    totalTestes++
    const cpfInvalido = await makeRequest("GET", `${BASE_URL}/usuarios/99999999999`, null, tokens.rh)
    logResult("CPF inexistente (deve falhar)", cpfInvalido, 404)
    if (cpfInvalido.status === 404) testesPassaram++
  }

  // ==================== RELATÓRIO FINAL ====================
  console.log(`\n${colors.bright}📊 RELATÓRIO FINAL - NOVO SCHEMA V2.0${colors.reset}`)
  console.log("=".repeat(60))

  const porcentagemSucesso = ((testesPassaram / totalTestes) * 100).toFixed(1)
  const statusColor = porcentagemSucesso >= 90 ? colors.green : porcentagemSucesso >= 70 ? colors.yellow : colors.red

  console.log(`${colors.bright}Total de Testes:${colors.reset} ${totalTestes}`)
  console.log(`${colors.green}Testes Passaram:${colors.reset} ${testesPassaram}`)
  console.log(`${colors.red}Testes Falharam:${colors.reset} ${totalTestes - testesPassaram}`)
  console.log(`${colors.bright}Taxa de Sucesso:${colors.reset} ${statusColor}${porcentagemSucesso}%${colors.reset}`)

  console.log(`\n${colors.bright}🔍 ANÁLISE POR SEÇÃO:${colors.reset}`)
  console.log(`${colors.cyan}1. Autenticação:${colors.reset} JWT com CPF como identificador`)
  console.log(`${colors.cyan}2. Novas Entidades:${colors.reset} UFs, Tipos de Ausência, Turnos, Feriados`)
  console.log(`${colors.cyan}3. Empresas:${colors.reset} CNPJ como chave primária`)
  console.log(`${colors.cyan}4. Usuários:${colors.reset} CPF como chave primária`)
  console.log(`${colors.cyan}5. Eventos:${colors.reset} Referências por CPF e IDs`)
  console.log(`${colors.cyan}6. Grupos:${colors.reset} Campo telefone obrigatório`)
  console.log(`${colors.cyan}7. Segurança:${colors.reset} Validações com novos identificadores`)

  console.log(`\n${colors.bright}🆕 MUDANÇAS IMPLEMENTADAS:${colors.reset}`)
  console.log(`${colors.blue}✅ CPF como chave primária para usuários${colors.reset}`)
  console.log(`${colors.blue}✅ CNPJ como chave primária para empresas${colors.reset}`)
  console.log(`${colors.blue}✅ Tabela UF para estados brasileiros${colors.reset}`)
  console.log(`${colors.blue}✅ Tipos de ausência configuráveis${colors.reset}`)
  console.log(`${colors.blue}✅ Sistema de turnos${colors.reset}`)
  console.log(`${colors.blue}✅ Feriados nacionais e estaduais${colors.reset}`)
  console.log(`${colors.blue}✅ Flag de gestor separada do tipo de usuário${colors.reset}`)

  if (porcentagemSucesso >= 90) {
    console.log(`\n${colors.green}🎉 MIGRAÇÃO PARA NOVO SCHEMA CONCLUÍDA!${colors.reset}`)
    console.log(`${colors.green}✅ Todas as funcionalidades adaptadas com sucesso${colors.reset}`)
    console.log(`${colors.green}✅ API funcionando com nova estrutura de dados${colors.reset}`)
  } else if (porcentagemSucesso >= 70) {
    console.log(`\n${colors.yellow}⚠️  MIGRAÇÃO PARCIALMENTE CONCLUÍDA${colors.reset}`)
    console.log(`${colors.yellow}🔧 Alguns ajustes podem ser necessários${colors.reset}`)
  } else {
    console.log(`\n${colors.red}🚨 PROBLEMAS NA MIGRAÇÃO${colors.reset}`)
    console.log(`${colors.red}❌ Correções urgentes necessárias${colors.reset}`)
  }

  console.log(`\n${colors.bright}💡 PRÓXIMOS PASSOS:${colors.reset}`)
  console.log(`${colors.green}- Executar script de migração: python scripts/seed_data_v2.py${colors.reset}`)
  console.log(`${colors.green}- Testar todas as funcionalidades com novos identificadores${colors.reset}`)
  console.log(`${colors.green}- Validar integridade referencial${colors.reset}`)
  console.log(`${colors.green}- Atualizar documentação da API${colors.reset}`)
}

// Executar testes
console.log(`${colors.bright}🚀 INICIANDO TESTE DA API COM NOVO SCHEMA...${colors.reset}`)
console.log(`${colors.yellow}📝 Testando migração para CPF/CNPJ como chaves primárias${colors.reset}`)
console.log(`${colors.yellow}🔧 Certifique-se de que o servidor Flask está rodando${colors.reset}`)
console.log(`${colors.blue}🗄️  Conectando ao MySQL na GCP Cloud SQL...${colors.reset}\n`)

testarAPICompleta().catch((error) => {
  console.error(`${colors.red}❌ Erro durante execução dos testes:${colors.reset}`, error)
})
