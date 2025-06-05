// Teste completo da API Flask - Versão 3.0 (Reescrito do zero)
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

// Estado global dos testes
const testState = {
  totalTestes: 0,
  testesPassaram: 0,
  tokens: {},
  usuarios: {},
  debugMode: true,
}

// Função auxiliar para fazer requisições com debugging melhorado
async function makeRequest(method, url, data = null, token = null, description = "") {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  }

  // Adicionar token se fornecido
  if (token) {
    options.headers["Authorization"] = `Bearer ${token}`
    if (testState.debugMode) {
      console.log(`${colors.yellow}🔑 Token usado: ${token.substring(0, 20)}...${colors.reset}`)
    }
  }

  // Adicionar dados se fornecido
  if (data) {
    options.body = JSON.stringify(data)
    if (testState.debugMode) {
      console.log(`${colors.blue}📤 Dados enviados: ${JSON.stringify(data, null, 2)}${colors.reset}`)
    }
  }

  try {
    if (testState.debugMode) {
      console.log(`${colors.cyan}🌐 ${method} ${url}${colors.reset}`)
    }

    const response = await fetch(url, options)
    const result = await response.json()

    return {
      status: response.status,
      data: result,
      headers: response.headers,
    }
  } catch (error) {
    console.log(`${colors.red}❌ Erro na requisição: ${error.message}${colors.reset}`)
    return {
      status: "ERROR",
      data: { erro: error.message },
      headers: null,
    }
  }
}

// Função para exibir resultados
function logResult(testName, result, expectedStatus = null) {
  testState.totalTestes++

  const isSuccess = expectedStatus ? result.status === expectedStatus : result.status < 400
  const statusColor = isSuccess ? colors.green : colors.red
  const icon = isSuccess ? "✅" : "❌"

  if (isSuccess) testState.testesPassaram++

  console.log(`\n${colors.cyan}=== ${testName} ===${colors.reset}`)
  console.log(`${icon} Status: ${statusColor}${result.status}${colors.reset}`)

  // Exibir resposta de forma inteligente
  if (result.data) {
    if (result.data.access_token) {
      console.log(`${colors.yellow}✅ Token recebido: ${result.data.access_token.substring(0, 30)}...${colors.reset}`)
      if (result.data.usuario) {
        console.log(
          `${colors.yellow}👤 Usuário: ${result.data.usuario.nome} (${result.data.usuario.email})${colors.reset}`,
        )
      }
    } else if (Array.isArray(result.data)) {
      console.log(`${colors.yellow}📋 Array com ${result.data.length} itens${colors.reset}`)
      if (result.data.length > 0) {
        console.log(
          `${colors.yellow}📄 Primeiro item: ${JSON.stringify(result.data[0], null, 2).substring(0, 100)}...${colors.reset}`,
        )
      }
    } else {
      const responseStr = JSON.stringify(result.data, null, 2)
      const truncated = responseStr.length > 300 ? responseStr.substring(0, 300) + "..." : responseStr
      console.log(`${colors.yellow}📄 Response: ${truncated}${colors.reset}`)
    }
  }
}

// Função para verificar se o servidor está rodando
async function verificarServidor() {
  console.log(`${colors.bright}🔍 VERIFICANDO SERVIDOR${colors.reset}`)

  try {
    const response = await fetch(BASE_URL.replace("/api", ""))
    if (response.ok) {
      const data = await response.json()
      console.log(`${colors.green}✅ Servidor Flask rodando${colors.reset}`)
      console.log(`${colors.green}✅ Versão: ${data.version || "N/A"}${colors.reset}`)
      console.log(`${colors.green}✅ Database: ${data.database || "N/A"}${colors.reset}`)
      return true
    }
  } catch (error) {
    console.log(`${colors.red}❌ Servidor não está rodando: ${error.message}${colors.reset}`)
    console.log(`${colors.yellow}💡 Execute: python app.py${colors.reset}`)
    return false
  }
}

// Função para testar autenticação básica
async function testarAutenticacao() {
  console.log(`\n${colors.bright}🔐 SEÇÃO 1: AUTENTICAÇÃO${colors.reset}`)

  // Credenciais de teste baseadas no seed_data
  const credenciais = [
    {
      nome: "RH",
      email: "maria.rh@techsolutions.com",
      senha: "123456",
      tipo: "rh",
    },
    {
      nome: "Gestor",
      email: "joao.gestor@techsolutions.com",
      senha: "123456",
      tipo: "gestor",
    },
    {
      nome: "Usuário Comum",
      email: "ana.dev@techsolutions.com",
      senha: "123456",
      tipo: "comum",
    },
  ]

  // Testar login para cada tipo de usuário
  for (const cred of credenciais) {
    const result = await makeRequest("POST", `${BASE_URL}/auth/login`, {
      email: cred.email,
      senha: cred.senha,
    })

    logResult(`Login ${cred.nome}`, result, 200)

    if (result.status === 200 && result.data.access_token) {
      testState.tokens[cred.tipo] = result.data.access_token
      testState.usuarios[cred.tipo] = result.data.usuario
      console.log(`${colors.green}🔑 Token ${cred.tipo} salvo com sucesso${colors.reset}`)
    }
  }

  // Testar login inválido
  const loginInvalido = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "inexistente@test.com",
    senha: "senha_errada",
  })
  logResult("Login Inválido (deve falhar)", loginInvalido, 401)

  // Testar endpoint /me se temos token
  if (testState.tokens.rh) {
    console.log(`\n${colors.yellow}🧪 Testando endpoint /me com token RH...${colors.reset}`)
    const me = await makeRequest("GET", `${BASE_URL}/auth/me`, null, testState.tokens.rh)
    logResult("Endpoint /me", me, 200)

    // Se falhar, vamos debugar o token
    if (me.status !== 200) {
      console.log(`${colors.red}🔍 DEBUG: Token RH pode estar inválido${colors.reset}`)
      console.log(`${colors.red}🔍 Token: ${testState.tokens.rh}${colors.reset}`)
    }
  }
}

// Função para testar endpoints básicos (sem autenticação)
async function testarEndpointsPublicos() {
  console.log(`\n${colors.bright}🌍 SEÇÃO 2: ENDPOINTS PÚBLICOS${colors.reset}`)

  // Testar UFs (pode ser público)
  const ufs = await makeRequest("GET", `${BASE_URL}/ufs`)
  logResult("Listar UFs (público)", ufs)

  // Testar tipos de ausência (pode ser público)
  const tiposAusencia = await makeRequest("GET", `${BASE_URL}/tipos-ausencia`)
  logResult("Listar Tipos de Ausência (público)", tiposAusencia)

  // Testar turnos (pode ser público)
  const turnos = await makeRequest("GET", `${BASE_URL}/turnos`)
  logResult("Listar Turnos (público)", turnos)
}

// Função para testar endpoints protegidos
async function testarEndpointsProtegidos() {
  console.log(`\n${colors.bright}🔒 SEÇÃO 3: ENDPOINTS PROTEGIDOS${colors.reset}`)

  // Só continuar se temos pelo menos um token válido
  if (!testState.tokens.rh && !testState.tokens.gestor && !testState.tokens.comum) {
    console.log(`${colors.red}❌ Nenhum token válido disponível. Pulando testes protegidos.${colors.reset}`)
    return
  }

  // Testar com token RH
  if (testState.tokens.rh) {
    console.log(`\n${colors.cyan}👩‍💼 Testando com usuário RH${colors.reset}`)

    // Listar usuários
    const usuarios = await makeRequest("GET", `${BASE_URL}/usuarios`, null, testState.tokens.rh)
    logResult("RH - Listar Usuários", usuarios, 200)

    // Listar grupos
    const grupos = await makeRequest("GET", `${BASE_URL}/grupos`, null, testState.tokens.rh)
    logResult("RH - Listar Grupos", grupos, 200)

    // Listar empresas
    const empresas = await makeRequest("GET", `${BASE_URL}/empresas`, null, testState.tokens.rh)
    logResult("RH - Listar Empresas", empresas, 200)
  }

  // Testar com token Gestor
  if (testState.tokens.gestor) {
    console.log(`\n${colors.cyan}👨‍💼 Testando com usuário Gestor${colors.reset}`)

    // Listar usuários do grupo
    const usuariosGrupo = await makeRequest("GET", `${BASE_URL}/usuarios`, null, testState.tokens.gestor)
    logResult("Gestor - Listar Usuários do Grupo", usuariosGrupo, 200)

    // Tentar acessar empresas (deve falhar)
    const empresasGestor = await makeRequest("GET", `${BASE_URL}/empresas`, null, testState.tokens.gestor)
    logResult("Gestor - Tentar Acessar Empresas (deve falhar)", empresasGestor, 403)
  }

  // Testar com token Usuário Comum
  if (testState.tokens.comum) {
    console.log(`\n${colors.cyan}👤 Testando com usuário Comum${colors.reset}`)

    // Listar eventos próprios
    const eventos = await makeRequest("GET", `${BASE_URL}/eventos`, null, testState.tokens.comum)
    logResult("Usuário - Listar Eventos Próprios", eventos, 200)

    // Tentar criar usuário (deve falhar)
    const criarUsuario = await makeRequest(
      "POST",
      `${BASE_URL}/usuarios`,
      {
        cpf: "99988877766",
        nome: "Teste Sem Permissão",
        email: "teste@test.com",
        senha: "123456",
      },
      testState.tokens.comum,
    )
    logResult("Usuário - Tentar Criar Usuário (deve falhar)", criarUsuario, 403)
  }
}

// Função para testar operações CRUD
async function testarOperacoesCRUD() {
  console.log(`\n${colors.bright}📝 SEÇÃO 4: OPERAÇÕES CRUD${colors.reset}`)

  if (!testState.tokens.rh) {
    console.log(`${colors.red}❌ Token RH necessário para testes CRUD. Pulando.${colors.reset}`)
    return
  }

  // Primeiro, vamos obter informações do usuário RH para usar o CNPJ correto
  let cnpjEmpresaRH = "12345678000190" // CNPJ padrão como fallback

  if (testState.usuarios.rh && testState.usuarios.rh.grupo_id) {
    // Tentar obter o CNPJ da empresa do RH
    const grupoRH = await makeRequest(
      "GET",
      `${BASE_URL}/grupos/${testState.usuarios.rh.grupo_id}`,
      null,
      testState.tokens.rh,
    )
    if (grupoRH.status === 200 && grupoRH.data.cnpj_empresa) {
      cnpjEmpresaRH = grupoRH.data.cnpj_empresa
      console.log(`${colors.blue}🏢 CNPJ da empresa do RH: ${cnpjEmpresaRH}${colors.reset}`)
    }
  }

  // Criar um novo grupo usando o CNPJ correto da empresa do RH
  const novoGrupo = await makeRequest(
    "POST",
    `${BASE_URL}/grupos`,
    {
      nome: `Grupo Teste ${Date.now()}`,
      cnpj_empresa: cnpjEmpresaRH, // Usar o CNPJ da empresa do RH
      telefone: "(11) 1234-5678",
      descricao: "Grupo criado durante teste automatizado",
    },
    testState.tokens.rh,
  )
  logResult("Criar Novo Grupo", novoGrupo, 201)

  // Se grupo foi criado, tentar atualizá-lo
  if (novoGrupo.status === 201 && novoGrupo.data.id) {
    const atualizarGrupo = await makeRequest(
      "PUT",
      `${BASE_URL}/grupos/${novoGrupo.data.id}`,
      {
        descricao: "Grupo atualizado durante teste",
      },
      testState.tokens.rh,
    )
    logResult("Atualizar Grupo Criado", atualizarGrupo, 200)
  }

  // Criar um novo evento
  if (testState.tokens.comum) {
    const novoEvento = await makeRequest(
      "POST",
      `${BASE_URL}/eventos`,
      {
        cpf_usuario: testState.usuarios.comum?.cpf || "34567890123",
        data_inicio: "2025-06-15",
        data_fim: "2025-06-19",
        id_tipo_ausencia: 1,
        uf: "SP",
      },
      testState.tokens.comum,
    )
    logResult("Usuário - Criar Novo Evento", novoEvento, 201)
  }
}

// Função para testar validações de segurança
async function testarSeguranca() {
  console.log(`\n${colors.bright}🛡️ SEÇÃO 5: VALIDAÇÕES DE SEGURANÇA${colors.reset}`)

  // Acesso sem token
  const semToken = await makeRequest("GET", `${BASE_URL}/usuarios`)
  logResult("Acesso sem token (deve falhar)", semToken, 401)

  // Token inválido
  const tokenInvalido = await makeRequest("GET", `${BASE_URL}/usuarios`, null, "token-completamente-invalido")
  logResult("Token inválido (deve falhar)", tokenInvalido, 401)

  // Token malformado
  const tokenMalformado = await makeRequest("GET", `${BASE_URL}/usuarios`, null, "Bearer token-malformado")
  logResult("Token malformado (deve falhar)", tokenMalformado, 401)
}

// Função para testar logout
async function testarLogout() {
  console.log(`\n${colors.bright}🚪 SEÇÃO 6: LOGOUT${colors.reset}`)

  if (testState.tokens.rh) {
    const logout = await makeRequest("POST", `${BASE_URL}/auth/logout`, null, testState.tokens.rh)
    logResult("Logout RH", logout, 200)

    // Tentar usar token após logout
    const aposLogout = await makeRequest("GET", `${BASE_URL}/auth/me`, null, testState.tokens.rh)
    logResult("Usar token após logout (deve falhar)", aposLogout, 401)
  }
}

// Função para gerar relatório final
function gerarRelatorio() {
  console.log(`\n${colors.bright}📊 RELATÓRIO FINAL${colors.reset}`)
  console.log("=".repeat(60))

  const porcentagemSucesso = ((testState.testesPassaram / testState.totalTestes) * 100).toFixed(1)
  const statusColor = porcentagemSucesso >= 90 ? colors.green : porcentagemSucesso >= 70 ? colors.yellow : colors.red

  console.log(`${colors.bright}Total de Testes:${colors.reset} ${testState.totalTestes}`)
  console.log(`${colors.green}Testes Passaram:${colors.reset} ${testState.testesPassaram}`)
  console.log(`${colors.red}Testes Falharam:${colors.reset} ${testState.totalTestes - testState.testesPassaram}`)
  console.log(`${colors.bright}Taxa de Sucesso:${colors.reset} ${statusColor}${porcentagemSucesso}%${colors.reset}`)

  console.log(`\n${colors.bright}🔑 TOKENS OBTIDOS:${colors.reset}`)
  Object.keys(testState.tokens).forEach((tipo) => {
    console.log(`${colors.green}✅ ${tipo.toUpperCase()}: ${testState.tokens[tipo] ? "OK" : "FALHOU"}${colors.reset}`)
  })

  console.log(`\n${colors.bright}💡 DIAGNÓSTICO:${colors.reset}`)
  if (porcentagemSucesso >= 90) {
    console.log(`${colors.green}🎉 API funcionando perfeitamente!${colors.reset}`)
  } else if (porcentagemSucesso >= 70) {
    console.log(`${colors.yellow}⚠️ API funcionando com alguns problemas${colors.reset}`)
  } else if (Object.keys(testState.tokens).length === 0) {
    console.log(`${colors.red}🚨 PROBLEMA CRÍTICO: Nenhum login funcionou${colors.reset}`)
    console.log(`${colors.yellow}🔧 Verifique as credenciais no banco de dados${colors.reset}`)
    console.log(`${colors.yellow}🔧 Execute: python scripts/seed_data_complete.py${colors.reset}`)
  } else if (testState.testesPassaram < 5) {
    console.log(`${colors.red}🚨 PROBLEMA CRÍTICO: Tokens não estão funcionando${colors.reset}`)
    console.log(`${colors.yellow}🔧 Verifique a configuração JWT no Flask${colors.reset}`)
    console.log(`${colors.yellow}🔧 Verifique a variável JWT_SECRET_KEY${colors.reset}`)
  } else {
    console.log(`${colors.yellow}⚠️ Alguns endpoints podem estar com problemas${colors.reset}`)
  }

  console.log(`\n${colors.bright}🔧 COMANDOS ÚTEIS:${colors.reset}`)
  console.log(`${colors.cyan}- Recriar dados: python scripts/seed_data_complete.py${colors.reset}`)
  console.log(`${colors.cyan}- Verificar integridade: python scripts/validate_integrity.py${colors.reset}`)
  console.log(`${colors.cyan}- Verificar ambiente: python scripts/check_environment.py${colors.reset}`)
}

// Função principal
async function executarTestes() {
  console.log(`${colors.bright}🚀 TESTE COMPLETO DA API - VERSÃO 3.0${colors.reset}`)
  console.log(`${colors.blue}📅 ${new Date().toLocaleString("pt-BR")}${colors.reset}`)
  console.log(`${colors.blue}🔗 Base URL: ${BASE_URL}${colors.reset}\n`)

  // Verificar se servidor está rodando
  const servidorOk = await verificarServidor()
  if (!servidorOk) {
    console.log(`${colors.red}❌ Não é possível continuar sem o servidor${colors.reset}`)
    return
  }

  try {
    // Executar todas as seções de teste
    await testarAutenticacao()
    await testarEndpointsPublicos()
    await testarEndpointsProtegidos()
    await testarOperacoesCRUD()
    await testarSeguranca()
    await testarLogout()

    // Gerar relatório final
    gerarRelatorio()
  } catch (error) {
    console.log(`${colors.red}❌ Erro durante execução dos testes: ${error.message}${colors.reset}`)
    console.log(`${colors.red}Stack: ${error.stack}${colors.reset}`)
  }
}

// Executar testes
console.log(`${colors.bright}🎯 Iniciando testes da API Flask...${colors.reset}`)
console.log(`${colors.yellow}⚙️ Modo debug: ${testState.debugMode ? "ATIVADO" : "DESATIVADO"}${colors.reset}`)
console.log(`${colors.yellow}🔧 Para desativar debug, mude debugMode para false${colors.reset}\n`)

executarTestes().catch((error) => {
  console.error(`${colors.red}💥 Erro fatal: ${error.message}${colors.reset}`)
})
