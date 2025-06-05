// Teste completo da API Flask - Versão 4.0 (Ampliado com testes abrangentes)
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
  // Armazenar IDs de entidades criadas durante os testes para uso posterior
  entidadesCriadas: {
    eventos: [],
    usuarios: [],
    grupos: [],
  },
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

  return isSuccess
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

  // Testar login com senha incorreta
  const loginSenhaIncorreta = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "maria.rh@techsolutions.com",
    senha: "senha_errada",
  })
  logResult("Login com Senha Incorreta (deve falhar)", loginSenhaIncorreta, 401)

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

  // Testar feriados (pode ser público)
  const feriados = await makeRequest("GET", `${BASE_URL}/feriados`)
  logResult("Listar Feriados (público)", feriados)
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

    // Listar calendário
    const calendario = await makeRequest("GET", `${BASE_URL}/calendario`, null, testState.tokens.rh)
    logResult("RH - Listar Calendário", calendario, 200)
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

    // Listar calendário do grupo
    if (testState.usuarios.gestor && testState.usuarios.gestor.grupo_id) {
      const calendarioGrupo = await makeRequest(
        "GET",
        `${BASE_URL}/calendario/grupo/${testState.usuarios.gestor.grupo_id}`,
        null,
        testState.tokens.gestor,
      )
      logResult("Gestor - Listar Calendário do Grupo", calendarioGrupo, 200)
    }
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

    // Tentar acessar calendário de outro grupo (deve falhar)
    const outroGrupoId = testState.usuarios.comum.grupo_id === 1 ? 2 : 1
    const calendarioOutroGrupo = await makeRequest(
      "GET",
      `${BASE_URL}/calendario/grupo/${outroGrupoId}`,
      null,
      testState.tokens.comum,
    )
    logResult("Usuário - Tentar Acessar Calendário de Outro Grupo (deve falhar)", calendarioOutroGrupo, 403)
  }
}

// Função para testar operações CRUD básicas
async function testarOperacoesCRUD() {
  console.log(`\n${colors.bright}📝 SEÇÃO 4: OPERAÇÕES CRUD BÁSICAS${colors.reset}`)

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
  const sucessoGrupo = logResult("Criar Novo Grupo", novoGrupo, 201)

  // Se grupo foi criado, tentar atualizá-lo
  if (sucessoGrupo && novoGrupo.data.id) {
    // Salvar ID do grupo para uso posterior
    testState.entidadesCriadas.grupos.push(novoGrupo.data.id)

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
    const sucessoEvento = logResult("Usuário - Criar Novo Evento", novoEvento, 201)

    // Salvar ID do evento para uso posterior
    if (sucessoEvento && novoEvento.data.id) {
      testState.entidadesCriadas.eventos.push(novoEvento.data.id)
    }
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

  // Tentar acessar recurso de outro usuário
  if (testState.tokens.comum && testState.usuarios.gestor) {
    const acessoNaoAutorizado = await makeRequest(
      "GET",
      `${BASE_URL}/usuarios/${testState.usuarios.gestor.cpf}`,
      null,
      testState.tokens.comum,
    )
    logResult("Acessar Recurso de Outro Usuário (deve falhar)", acessoNaoAutorizado, 403)
  }

  // Tentar criar grupo com CNPJ inválido
  if (testState.tokens.rh) {
    const grupoInvalido = await makeRequest(
      "POST",
      `${BASE_URL}/grupos`,
      {
        nome: "Grupo Teste Inválido",
        cnpj_empresa: "99999999999999", // CNPJ inválido
        telefone: "(11) 1234-5678",
      },
      testState.tokens.rh,
    )
    logResult("Criar Grupo com CNPJ Inválido (deve falhar)", grupoInvalido, 400)
  }
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

// NOVA FUNÇÃO: Testar fluxo de aprovação de eventos
async function testarAprovacaoEventos() {
  console.log(`\n${colors.bright}🗓️ SEÇÃO 7: FLUXO DE APROVAÇÃO DE EVENTOS${colors.reset}`)

  // Verificar se temos tokens necessários
  if (!testState.tokens.comum || !testState.tokens.gestor) {
    console.log(`${colors.red}❌ Tokens de usuário comum e gestor necessários. Pulando.${colors.reset}`)
    return
  }

  // 1. Criar evento como usuário comum
  const novoEvento = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: testState.usuarios.comum?.cpf,
      data_inicio: "2025-07-10",
      data_fim: "2025-07-15",
      id_tipo_ausencia: 1,
      uf: "SP",
    },
    testState.tokens.comum,
  )
  const sucessoEvento = logResult("Criar Evento para Aprovação", novoEvento, 201)

  if (sucessoEvento && novoEvento.data.id) {
    const eventoId = novoEvento.data.id
    testState.entidadesCriadas.eventos.push(eventoId)

    // 2. Tentar aprovar como usuário comum (deve falhar)
    const aprovarComum = await makeRequest(
      "POST",
      `${BASE_URL}/eventos/${eventoId}/aprovar`,
      { aprovador_cpf: testState.usuarios.comum?.cpf },
      testState.tokens.comum,
    )
    logResult("Aprovar Evento como Usuário Comum (deve falhar)", aprovarComum, 403)

    // 3. Aprovar como gestor
    const aprovarGestor = await makeRequest(
      "POST",
      `${BASE_URL}/eventos/${eventoId}/aprovar`,
      { aprovador_cpf: testState.usuarios.gestor?.cpf },
      testState.tokens.gestor,
    )
    logResult("Aprovar Evento como Gestor", aprovarGestor, 200)

    // 4. Verificar status do evento
    const verificarEvento = await makeRequest("GET", `${BASE_URL}/eventos/${eventoId}`, null, testState.tokens.gestor)
    logResult("Verificar Status do Evento Aprovado", verificarEvento, 200)

    // 5. Criar outro evento para rejeição
    const eventoParaRejeitar = await makeRequest(
      "POST",
      `${BASE_URL}/eventos`,
      {
        cpf_usuario: testState.usuarios.comum?.cpf,
        data_inicio: "2025-08-10",
        data_fim: "2025-08-15",
        id_tipo_ausencia: 1,
        uf: "SP",
      },
      testState.tokens.comum,
    )

    if (eventoParaRejeitar.status === 201 && eventoParaRejeitar.data.id) {
      const eventoRejeitadoId = eventoParaRejeitar.data.id
      testState.entidadesCriadas.eventos.push(eventoRejeitadoId)

      // 6. Rejeitar como gestor
      const rejeitarGestor = await makeRequest(
        "POST",
        `${BASE_URL}/eventos/${eventoRejeitadoId}/rejeitar`,
        { aprovador_cpf: testState.usuarios.gestor?.cpf },
        testState.tokens.gestor,
      )
      logResult("Rejeitar Evento como Gestor", rejeitarGestor, 200)

      // 7. Verificar status do evento rejeitado
      const verificarRejeitado = await makeRequest(
        "GET",
        `${BASE_URL}/eventos/${eventoRejeitadoId}`,
        null,
        testState.tokens.gestor,
      )
      logResult("Verificar Status do Evento Rejeitado", verificarRejeitado, 200)
    }
  }
}

// NOVA FUNÇÃO: Testar criação de usuários com diferentes papéis
async function testarCriacaoUsuarios() {
  console.log(`\n${colors.bright}👥 SEÇÃO 8: CRIAÇÃO DE USUÁRIOS${colors.reset}`)

  if (!testState.tokens.rh || !testState.tokens.gestor) {
    console.log(`${colors.red}❌ Tokens de RH e gestor necessários. Pulando.${colors.reset}`)
    return
  }

  // 1. Criar usuário comum como RH
  const cpfUsuarioComum = Math.floor(10000000000 + Math.random() * 90000000000)
  const novoUsuarioComum = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: cpfUsuarioComum,
      nome: "Novo Usuário Comum",
      email: `novo.comum.${Date.now()}@techsolutions.com`,
      senha: "123456",
      grupo_id: testState.usuarios.comum?.grupo_id,
      inicio_na_empresa: "2025-01-01",
      uf: "SP",
      tipo_usuario: "comum",
      flag_gestor: "N",
    },
    testState.tokens.rh,
  )
  const sucessoUsuarioComum = logResult("Criar Usuário Comum como RH", novoUsuarioComum, 201)

  if (sucessoUsuarioComum) {
    testState.entidadesCriadas.usuarios.push(cpfUsuarioComum)
  }

  // 2. Criar usuário gestor como RH
  const cpfUsuarioGestor = Math.floor(10000000000 + Math.random() * 90000000000)
  const novoUsuarioGestor = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: cpfUsuarioGestor,
      nome: "Novo Usuário Gestor",
      email: `novo.gestor.${Date.now()}@techsolutions.com`,
      senha: "123456",
      grupo_id: testState.usuarios.gestor?.grupo_id,
      inicio_na_empresa: "2025-01-01",
      uf: "SP",
      tipo_usuario: "comum",
      flag_gestor: "S",
    },
    testState.tokens.rh,
  )
  const sucessoUsuarioGestor = logResult("Criar Usuário Gestor como RH", novoUsuarioGestor, 201)

  if (sucessoUsuarioGestor) {
    testState.entidadesCriadas.usuarios.push(cpfUsuarioGestor)
  }

  // 3. Tentar criar usuário em grupo não autorizado
  const grupoNaoAutorizado = testState.usuarios.gestor?.grupo_id === 1 ? 2 : 1
  const cpfUsuarioInvalido = Math.floor(10000000000 + Math.random() * 90000000000)
  const usuarioGrupoInvalido = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: cpfUsuarioInvalido,
      nome: "Usuário Grupo Inválido",
      email: `grupo.invalido.${Date.now()}@techsolutions.com`,
      senha: "123456",
      grupo_id: grupoNaoAutorizado,
      inicio_na_empresa: "2025-01-01",
      uf: "SP",
    },
    testState.tokens.gestor,
  )
  logResult("Criar Usuário em Grupo Não Autorizado (deve falhar)", usuarioGrupoInvalido, 403)

  // 4. Tentar criar usuário com CPF inválido
  const usuarioCpfInvalido = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: "123", // CPF inválido
      nome: "Usuário CPF Inválido",
      email: `cpf.invalido.${Date.now()}@techsolutions.com`,
      senha: "123456",
      grupo_id: testState.usuarios.rh?.grupo_id,
      inicio_na_empresa: "2025-01-01",
      uf: "SP",
    },
    testState.tokens.rh,
  )
  logResult("Criar Usuário com CPF Inválido (deve falhar)", usuarioCpfInvalido, 400)

  // 5. Tentar criar usuário com email duplicado
  if (sucessoUsuarioComum) {
    const usuarioEmailDuplicado = await makeRequest(
      "POST",
      `${BASE_URL}/usuarios`,
      {
        cpf: Math.floor(10000000000 + Math.random() * 90000000000),
        nome: "Usuário Email Duplicado",
        email: novoUsuarioComum.data.email, // Email já usado
        senha: "123456",
        grupo_id: testState.usuarios.rh?.grupo_id,
        inicio_na_empresa: "2025-01-01",
        uf: "SP",
      },
      testState.tokens.rh,
    )
    logResult("Criar Usuário com Email Duplicado (deve falhar)", usuarioEmailDuplicado, 409)
  }
}

// NOVA FUNÇÃO: Testar gerenciamento completo de grupos
async function testarGerenciamentoGrupos() {
  console.log(`\n${colors.bright}🏢 SEÇÃO 9: GERENCIAMENTO DE GRUPOS${colors.reset}`)

  if (!testState.tokens.rh) {
    console.log(`${colors.red}❌ Token RH necessário. Pulando.${colors.reset}`)
    return
  }

  // 1. Obter CNPJ da empresa do RH
  let cnpjEmpresaRH = "12345678000190"
  if (testState.usuarios.rh && testState.usuarios.rh.grupo_id) {
    const grupoRH = await makeRequest(
      "GET",
      `${BASE_URL}/grupos/${testState.usuarios.rh.grupo_id}`,
      null,
      testState.tokens.rh,
    )
    if (grupoRH.status === 200 && grupoRH.data.cnpj_empresa) {
      cnpjEmpresaRH = grupoRH.data.cnpj_empresa
    }
  }

  // 2. Criar grupo com dados inválidos
  const grupoInvalido = await makeRequest(
    "POST",
    `${BASE_URL}/grupos`,
    {
      nome: "", // Nome vazio
      cnpj_empresa: cnpjEmpresaRH,
      telefone: "(11) 1234-5678",
    },
    testState.tokens.rh,
  )
  logResult("Criar Grupo com Dados Inválidos (deve falhar)", grupoInvalido, 400)

  // 3. Criar grupo válido
  const novoGrupo = await makeRequest(
    "POST",
    `${BASE_URL}/grupos`,
    {
      nome: `Grupo Teste Completo ${Date.now()}`,
      cnpj_empresa: cnpjEmpresaRH,
      telefone: "(11) 1234-5678",
      descricao: "Grupo para teste completo",
    },
    testState.tokens.rh,
  )
  const sucessoGrupo = logResult("Criar Novo Grupo Válido", novoGrupo, 201)

  if (sucessoGrupo && novoGrupo.data.id) {
    const grupoId = novoGrupo.data.id
    testState.entidadesCriadas.grupos.push(grupoId)

    // 4. Atualizar grupo
    const atualizarGrupo = await makeRequest(
      "PUT",
      `${BASE_URL}/grupos/${grupoId}`,
      {
        nome: "Grupo Atualizado",
        descricao: "Descrição atualizada durante teste",
      },
      testState.tokens.rh,
    )
    logResult("Atualizar Grupo", atualizarGrupo, 200)

    // 5. Tentar atualizar como gestor (deve falhar)
    if (testState.tokens.gestor) {
      const atualizarGestor = await makeRequest(
        "PUT",
        `${BASE_URL}/grupos/${grupoId}`,
        {
          descricao: "Tentativa de atualização por gestor",
        },
        testState.tokens.gestor,
      )
      logResult("Atualizar Grupo como Gestor (deve falhar)", atualizarGestor, 403)
    }

    // 6. Desativar grupo
    const desativarGrupo = await makeRequest("DELETE", `${BASE_URL}/grupos/${grupoId}`, null, testState.tokens.rh)
    logResult("Desativar Grupo", desativarGrupo, 200)

    // 7. Verificar se grupo está desativado
    const verificarGrupo = await makeRequest("GET", `${BASE_URL}/grupos/${grupoId}`, null, testState.tokens.rh)
    logResult("Verificar Grupo Desativado", verificarGrupo, 200)
  }
}

// NOVA FUNÇÃO: Testar validação de dados e casos de borda
async function testarValidacaoDados() {
  console.log(`\n${colors.bright}🔍 SEÇÃO 10: VALIDAÇÃO DE DADOS${colors.reset}`)

  if (!testState.tokens.comum || !testState.tokens.rh) {
    console.log(`${colors.red}❌ Tokens necessários. Pulando.${colors.reset}`)
    return
  }

  // 1. Evento com data final anterior à data inicial
  const eventoDataInvalida = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: testState.usuarios.comum?.cpf,
      data_inicio: "2025-07-15", // Data posterior à final
      data_fim: "2025-07-10",
      id_tipo_ausencia: 1,
      uf: "SP",
    },
    testState.tokens.comum,
  )
  logResult("Criar Evento com Data Inválida (deve falhar)", eventoDataInvalida, 400)

  // 2. Evento com tipo de ausência inexistente
  const eventoTipoInexistente = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: testState.usuarios.comum?.cpf,
      data_inicio: "2025-07-10",
      data_fim: "2025-07-15",
      id_tipo_ausencia: 9999, // Tipo inexistente
      uf: "SP",
    },
    testState.tokens.comum,
  )
  logResult("Criar Evento com Tipo Inexistente (deve falhar)", eventoTipoInexistente, 400)

  // 3. Usuário com UF inválida
  const cpfUsuarioUfInvalida = Math.floor(10000000000 + Math.random() * 90000000000)
  const usuarioUfInvalida = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: cpfUsuarioUfInvalida,
      nome: "Usuário UF Inválida",
      email: `uf.invalida.${Date.now()}@techsolutions.com`,
      senha: "123456",
      grupo_id: testState.usuarios.rh?.grupo_id,
      inicio_na_empresa: "2025-01-01",
      uf: "XX", // UF inválida
    },
    testState.tokens.rh,
  )
  logResult("Criar Usuário com UF Inválida (deve falhar)", usuarioUfInvalida, 400)

  // 4. Grupo sem telefone (campo obrigatório)
  let cnpjEmpresaRH = "12345678000190"
  if (testState.usuarios.rh && testState.usuarios.rh.grupo_id) {
    const grupoRH = await makeRequest(
      "GET",
      `${BASE_URL}/grupos/${testState.usuarios.rh.grupo_id}`,
      null,
      testState.tokens.rh,
    )
    if (grupoRH.status === 200 && grupoRH.data.cnpj_empresa) {
      cnpjEmpresaRH = grupoRH.data.cnpj_empresa
    }
  }

  const grupoSemTelefone = await makeRequest(
    "POST",
    `${BASE_URL}/grupos`,
    {
      nome: `Grupo Sem Telefone ${Date.now()}`,
      cnpj_empresa: cnpjEmpresaRH,
      // Telefone omitido
    },
    testState.tokens.rh,
  )
  logResult("Criar Grupo Sem Telefone (deve falhar)", grupoSemTelefone, 400)
}

// NOVA FUNÇÃO: Testar calendário e visualizações
async function testarCalendario() {
  console.log(`\n${colors.bright}📅 SEÇÃO 11: CALENDÁRIO E VISUALIZAÇÕES${colors.reset}`)

  if (!testState.tokens.rh || !testState.tokens.gestor || !testState.tokens.comum) {
    console.log(`${colors.red}❌ Tokens necessários. Pulando.${colors.reset}`)
    return
  }

  // 1. Calendário geral (RH)
  const calendarioRH = await makeRequest("GET", `${BASE_URL}/calendario`, null, testState.tokens.rh)
  logResult("Calendário Geral (RH)", calendarioRH, 200)

  // 2. Calendário com filtro de data
  const dataInicio = new Date()
  const dataFim = new Date()
  dataFim.setMonth(dataFim.getMonth() + 3) // 3 meses à frente

  const calendarioFiltrado = await makeRequest(
    "GET",
    `${BASE_URL}/calendario?inicio=${dataInicio.toISOString().split("T")[0]}&fim=${dataFim.toISOString().split("T")[0]}`,
    null,
    testState.tokens.rh,
  )
  logResult("Calendário com Filtro de Data", calendarioFiltrado, 200)

  // 3. Calendário de grupo específico
  if (testState.usuarios.gestor && testState.usuarios.gestor.grupo_id) {
    const calendarioGrupo = await makeRequest(
      "GET",
      `${BASE_URL}/calendario/grupo/${testState.usuarios.gestor.grupo_id}`,
      null,
      testState.tokens.gestor,
    )
    logResult("Calendário de Grupo Específico", calendarioGrupo, 200)
  }

  // 4. Calendário com filtro de tipo de ausência
  const calendarioTipoAusencia = await makeRequest(
    "GET",
    `${BASE_URL}/calendario?tipo_ausencia=1`,
    null,
    testState.tokens.rh,
  )
  logResult("Calendário com Filtro de Tipo de Ausência", calendarioTipoAusencia, 200)

  // 5. Usuário comum só deve ver eventos do seu grupo
  const calendarioUsuarioComum = await makeRequest("GET", `${BASE_URL}/calendario`, null, testState.tokens.comum)
  logResult("Calendário para Usuário Comum", calendarioUsuarioComum, 200)
}

// Função para limpar dados de teste
async function limparDadosTeste() {
  console.log(`\n${colors.bright}🧹 LIMPEZA DE DADOS DE TESTE${colors.reset}`)

  if (!testState.tokens.rh) {
    console.log(`${colors.red}❌ Token RH necessário para limpeza. Pulando.${colors.reset}`)
    return
  }

  // Limpar eventos criados
  for (const eventoId of testState.entidadesCriadas.eventos) {
    const deletarEvento = await makeRequest("DELETE", `${BASE_URL}/eventos/${eventoId}`, null, testState.tokens.rh)
    logResult(`Deletar Evento ID ${eventoId}`, deletarEvento, 200)
  }

  // Limpar usuários criados
  for (const cpfUsuario of testState.entidadesCriadas.usuarios) {
    const deletarUsuario = await makeRequest("DELETE", `${BASE_URL}/usuarios/${cpfUsuario}`, null, testState.tokens.rh)
    logResult(`Deletar Usuário CPF ${cpfUsuario}`, deletarUsuario, 200)
  }

  // Limpar grupos criados (já foram desativados nos testes)
  console.log(
    `${colors.green}✅ ${testState.entidadesCriadas.grupos.length} grupos foram desativados durante os testes${colors.reset}`,
  )
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

  console.log(`\n${colors.bright}📈 ESTATÍSTICAS DE ENTIDADES:${colors.reset}`)
  console.log(`${colors.blue}🗓️ Eventos testados: ${testState.entidadesCriadas.eventos.length}${colors.reset}`)
  console.log(`${colors.blue}👤 Usuários testados: ${testState.entidadesCriadas.usuarios.length}${colors.reset}`)
  console.log(`${colors.blue}🏢 Grupos testados: ${testState.entidadesCriadas.grupos.length}${colors.reset}`)

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
  console.log(`${colors.bright}🚀 TESTE COMPLETO DA API - VERSÃO 4.0${colors.reset}`)
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

    // Novas seções de teste
    await testarAprovacaoEventos()
    await testarCriacaoUsuarios()
    await testarGerenciamentoGrupos()
    await testarValidacaoDados()
    await testarCalendario()

    // Limpar dados de teste
    await limparDadosTeste()

    // Testar logout por último
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
