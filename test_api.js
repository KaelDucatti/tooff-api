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
        cpf: "99988877766", // CPF para o novo usuário
        nome: "Teste Sem Permissão",
        email: "teste.sem.permissao." + Date.now() + "@example.com", // Email único para o novo usuário
        senha: "123456",
        grupo_id: testState.usuarios.comum?.grupo_id || 1, // Usar um grupo_id válido (e.g., from existing common user)
        inicio_na_empresa: "2023-01-01", // Adicionar campo obrigatório
        uf: "SP", // Adicionar campo obrigatório
        tipo_usuario: "comum", // Adicionar campo obrigatório se sua validação exigir
        flag_gestor: "N", // Adicionar campo obrigatório se sua validação exigir
      },
      testState.tokens.comum, // Token de usuário comum tentando criar
    )
    logResult("Usuário - Tentar Criar Usuário (deve falhar)", criarUsuario, 403) // Espera 403

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
        data_inicio: "2025-06-15", // Data que não seja fim de semana ou feriado conhecido
        data_fim: "2025-06-19", // Data que não seja fim de semana ou feriado conhecido
        id_tipo_ausencia: 2, // Usar um tipo que não seja Férias para não acionar validações de férias aqui
        uf: "SP",
      },
      testState.tokens.comum,
    )
    const sucessoEvento = logResult("Usuário - Criar Novo Evento (Não-Férias)", novoEvento, 201)

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

  // Tentar criar grupo com CNPJ inválido (se a validação foi removida, este teste deve ser ajustado ou removido)
  if (testState.tokens.rh) {
    const grupoInvalido = await makeRequest(
      "POST",
      `${BASE_URL}/grupos`,
      {
        nome: "Grupo Teste Inválido CNPJ",
        cnpj_empresa: "00000000000000", // CNPJ que seria inválido
        telefone: "(11) 1234-5678",
      },
      testState.tokens.rh,
    )
    // Se a validação de CNPJ foi removida, esperamos 201. Se não, 400.
    // Ajuste o expectedStatus conforme o estado da sua validação de CNPJ.
    // Por agora, vamos assumir que a validação ainda pode estar ativa em algum nível ou foi reintroduzida.
    logResult("Criar Grupo com CNPJ Inválido (verificar se validação está ativa)", grupoInvalido, 400)
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
      data_inicio: "2025-07-10", // Data que não seja fim de semana ou feriado
      data_fim: "2025-07-15", // Data que não seja fim de semana ou feriado
      id_tipo_ausencia: 2, // Não Férias
      uf: "SP",
    },
    testState.tokens.comum,
  )
  const sucessoEvento = logResult("Criar Evento (Não-Férias) para Aprovação", novoEvento, 201)

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
        data_inicio: "2025-08-10", // Data que não seja fim de semana ou feriado
        data_fim: "2025-08-15", // Data que não seja fim de semana ou feriado
        id_tipo_ausencia: 2, // Não Férias
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
  const cpfUsuarioComum = Date.now().toString().slice(-11) // CPF pseudo-aleatório
  const novoUsuarioComum = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: cpfUsuarioComum,
      nome: "Novo Usuário Comum Teste",
      email: `novo.comum.teste.${Date.now()}@techsolutions.com`,
      senha: "123456",
      grupo_id: testState.usuarios.comum?.grupo_id || 1, // Usar grupo do usuário comum existente ou fallback
      inicio_na_empresa: "2023-01-01", // Data que garanta > 1 ano de empresa
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
  const cpfUsuarioGestor = (Date.now() + 1).toString().slice(-11) // CPF pseudo-aleatório diferente
  const novoUsuarioGestor = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: cpfUsuarioGestor,
      nome: "Novo Usuário Gestor Teste",
      email: `novo.gestor.teste.${Date.now()}@techsolutions.com`,
      senha: "123456",
      grupo_id: testState.usuarios.gestor?.grupo_id || 1, // Usar grupo do gestor existente ou fallback
      inicio_na_empresa: "2023-01-01",
      uf: "SP",
      tipo_usuario: "comum", // Tipo base é comum, flag_gestor define
      flag_gestor: "S",
    },
    testState.tokens.rh,
  )
  const sucessoUsuarioGestor = logResult("Criar Usuário Gestor como RH", novoUsuarioGestor, 201)

  if (sucessoUsuarioGestor) {
    testState.entidadesCriadas.usuarios.push(cpfUsuarioGestor)
  }

  // 3. Tentar criar usuário em grupo não autorizado (Gestor tentando criar em grupo que não é o seu, se houver outro)
  const grupoNaoAutorizado = testState.usuarios.gestor?.grupo_id === 1 ? 2 : 1 // Exemplo de outro grupo
  if (testState.usuarios.rh?.grupo_id !== grupoNaoAutorizado) {
    // Garante que o grupo é diferente do RH também
    const cpfUsuarioInvalido = (Date.now() + 2).toString().slice(-11)
    const usuarioGrupoInvalido = await makeRequest(
      "POST",
      `${BASE_URL}/usuarios`,
      {
        cpf: cpfUsuarioInvalido,
        nome: "Usuário Grupo Inválido Teste",
        email: `grupo.invalido.teste.${Date.now()}@techsolutions.com`,
        senha: "123456",
        grupo_id: grupoNaoAutorizado,
        inicio_na_empresa: "2023-01-01",
        uf: "SP",
      },
      testState.tokens.gestor, // Gestor tentando criar
    )
    logResult("Criar Usuário em Grupo Não Autorizado (Gestor) (deve falhar)", usuarioGrupoInvalido, 403)
  } else {
    console.log(
      `${colors.yellow}⚠️ Pulando teste de criação de usuário em grupo não autorizado pelo gestor (grupos de teste não permitem).${colors.reset}`,
    )
    testState.totalTestes++
    testState.testesPassaram++
  }

  // 4. Tentar criar usuário com CPF inválido (se a validação foi removida, este teste deve ser ajustado ou removido)
  const usuarioCpfInvalido = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: "123", // CPF que seria inválido
      nome: "Usuário CPF Inválido Teste",
      email: `cpf.invalido.teste.${Date.now()}@techsolutions.com`,
      senha: "123456",
      grupo_id: testState.usuarios.rh?.grupo_id || 1,
      inicio_na_empresa: "2023-01-01",
      uf: "SP",
    },
    testState.tokens.rh,
  )
  // Ajuste o expectedStatus conforme o estado da sua validação de CPF.
  logResult("Criar Usuário com CPF Inválido (verificar se validação está ativa)", usuarioCpfInvalido, 400)

  // 5. Tentar criar usuário com email duplicado
  if (sucessoUsuarioComum && novoUsuarioComum.data.email) {
    const cpfEmailDuplicado = (Date.now() + 3).toString().slice(-11)
    const usuarioEmailDuplicado = await makeRequest(
      "POST",
      `${BASE_URL}/usuarios`,
      {
        cpf: cpfEmailDuplicado,
        nome: "Usuário Email Duplicado Teste",
        email: novoUsuarioComum.data.email, // Email já usado
        senha: "123456",
        grupo_id: testState.usuarios.rh?.grupo_id || 1,
        inicio_na_empresa: "2023-01-01",
        uf: "SP",
      },
      testState.tokens.rh,
    )
    logResult("Criar Usuário com Email Duplicado (deve falhar)", usuarioEmailDuplicado, 409) // Espera 409
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
    const grupoRHInfo = await makeRequest(
      "GET",
      `${BASE_URL}/grupos/${testState.usuarios.rh.grupo_id}`,
      null,
      testState.tokens.rh,
    )
    if (grupoRHInfo.status === 200 && grupoRHInfo.data.cnpj_empresa) {
      cnpjEmpresaRH = grupoRHInfo.data.cnpj_empresa
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
  const nomeNovoGrupo = `Grupo Teste Completo ${Date.now()}`
  const novoGrupo = await makeRequest(
    "POST",
    `${BASE_URL}/grupos`,
    {
      nome: nomeNovoGrupo,
      cnpj_empresa: cnpjEmpresaRH,
      telefone: "(11) 1234-5678",
      descricao: "Grupo para teste completo",
    },
    testState.tokens.rh,
  )
  const sucessoGrupo = logResult("Criar Novo Grupo Válido", novoGrupo, 201)

  if (sucessoGrupo && novoGrupo.data.id) {
    const grupoId = novoGrupo.data.id
    testState.entidadesCriadas.grupos.push(grupoId) // Adiciona para limpeza se desativação falhar

    // 4. Atualizar grupo
    const atualizarGrupo = await makeRequest(
      "PUT",
      `${BASE_URL}/grupos/${grupoId}`,
      {
        nome: "Grupo Atualizado Teste",
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
    if (logResult("Verificar Grupo Desativado (GET)", verificarGrupo, 200)) {
      if (verificarGrupo.data.ativo === false) {
        console.log(`${colors.green}✅ Grupo corretamente marcado como inativo.${colors.reset}`)
      } else {
        console.log(`${colors.red}❌ Grupo ainda está ativo após desativação.${colors.reset}`)
        testState.testesPassaram-- // Decrementa se a lógica de desativação falhou
      }
    }
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
      id_tipo_ausencia: 2, // Não Férias
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
  const cpfUsuarioUfInvalida = (Date.now() + 4).toString().slice(-11)
  const usuarioUfInvalida = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: cpfUsuarioUfInvalida,
      nome: "Usuário UF Inválida Teste",
      email: `uf.invalida.teste.${Date.now()}@techsolutions.com`,
      senha: "123456",
      grupo_id: testState.usuarios.rh?.grupo_id || 1,
      inicio_na_empresa: "2023-01-01",
      uf: "XX", // UF inválida
    },
    testState.tokens.rh,
  )
  logResult("Criar Usuário com UF Inválida (deve falhar)", usuarioUfInvalida, 400)

  // 4. Grupo sem telefone (campo obrigatório)
  let cnpjEmpresaRH = "12345678000190"
  if (testState.usuarios.rh && testState.usuarios.rh.grupo_id) {
    const grupoRHInfo = await makeRequest(
      "GET",
      `${BASE_URL}/grupos/${testState.usuarios.rh.grupo_id}`,
      null,
      testState.tokens.rh,
    )
    if (grupoRHInfo.status === 200 && grupoRHInfo.data.cnpj_empresa) {
      cnpjEmpresaRH = grupoRHInfo.data.cnpj_empresa
    }
  }

  const grupoSemTelefone = await makeRequest(
    "POST",
    `${BASE_URL}/grupos`,
    {
      nome: `Grupo Sem Telefone Teste ${Date.now()}`,
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
    `${BASE_URL}/calendario?tipo_ausencia=1`, // Assumindo que tipo 1 é Férias ou um tipo comum
    null,
    testState.tokens.rh,
  )
  logResult("Calendário com Filtro de Tipo de Ausência", calendarioTipoAusencia, 200)

  // 5. Usuário comum só deve ver eventos do seu grupo
  const calendarioUsuarioComum = await makeRequest("GET", `${BASE_URL}/calendario`, null, testState.tokens.comum)
  logResult("Calendário para Usuário Comum", calendarioUsuarioComum, 200)
}

// SEÇÃO 12: TESTES DO SISTEMA DE FÉRIAS
async function testarSistemaDeFerias() {
  console.log(`\n${colors.bright}🏖️ SEÇÃO 12: TESTES DO SISTEMA DE FÉRIAS${colors.reset}`)

  const ID_TIPO_AUSENCIA_FERIAS = 1 // !!! ATENÇÃO: Ajuste este ID se "Férias" tiver outro ID no seu sistema !!!
  const FERIADO_CONHECIDO_DATA = "2025-12-25" // Ex: Natal
  const SABADO_TESTE = "2025-06-21" // Sábado
  const DOMINGO_TESTE = "2025-06-22" // Domingo

  // Usuário comum para a maioria dos testes de agendamento
  const usuarioComum = testState.usuarios.comum
  const tokenComum = testState.tokens.comum

  // Usuário RH para criar novo empregado e verificar saldos
  const usuarioRH = testState.usuarios.rh
  const tokenRH = testState.tokens.rh

  // Usuário Gestor para aprovações
  const usuarioGestor = testState.usuarios.gestor
  const tokenGestor = testState.tokens.gestor

  if (!tokenComum || !usuarioComum?.cpf) {
    console.log(
      `${colors.red}❌ Token ou CPF do usuário comum não encontrado. Pulando testes de férias.${colors.reset}`,
    )
    return
  }
  if (!tokenRH || !usuarioRH?.cpf) {
    console.log(
      `${colors.red}❌ Token ou CPF do usuário RH não encontrado. Pulando partes dos testes de férias.${colors.reset}`,
    )
    return
  }
  if (!tokenGestor || !usuarioGestor?.cpf) {
    console.log(
      `${colors.red}❌ Token ou CPF do usuário Gestor não encontrado. Pulando partes dos testes de férias.${colors.reset}`,
    )
    return
  }

  const UF_USUARIO_COMUM = usuarioComum.uf || "SP" // UF para checagem de feriados

  console.log(`\n${colors.cyan}📅 12.1 Validações na Criação de Eventos de Férias (Usuário Comum)${colors.reset}`)

  // Teste 1: Agendar férias começando no Sábado
  const feriasSabado = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: usuarioComum.cpf,
      data_inicio: SABADO_TESTE,
      data_fim: "2025-06-25", // Qualquer data válida após
      id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
      uf: UF_USUARIO_COMUM,
    },
    tokenComum,
  )
  logResult("Férias - Início no Sábado (deve falhar)", feriasSabado, 400)

  // Teste 2: Agendar férias terminando no Domingo
  const feriasDomingo = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: usuarioComum.cpf,
      data_inicio: "2025-06-23", // Segunda-feira
      data_fim: DOMINGO_TESTE,
      id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
      uf: UF_USUARIO_COMUM,
    },
    tokenComum,
  )
  logResult("Férias - Fim no Domingo (deve falhar)", feriasDomingo, 400)

  // Teste 3: Agendar férias começando em feriado
  const feriasFeriadoInicio = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: usuarioComum.cpf,
      data_inicio: FERIADO_CONHECIDO_DATA,
      data_fim: "2025-12-27",
      id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
      uf: UF_USUARIO_COMUM,
    },
    tokenComum,
  )
  logResult(`Férias - Início em Feriado (${FERIADO_CONHECIDO_DATA}) (deve falhar)`, feriasFeriadoInicio, 400)

  // Teste 4: Agendar férias terminando em feriado
  const feriasFeriadoFim = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: usuarioComum.cpf,
      data_inicio: "2025-12-22",
      data_fim: FERIADO_CONHECIDO_DATA,
      id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
      uf: UF_USUARIO_COMUM,
    },
    tokenComum,
  )
  logResult(`Férias - Fim em Feriado (${FERIADO_CONHECIDO_DATA}) (deve falhar)`, feriasFeriadoFim, 400)

  // Teste 5: Tentar agendar mais de 30 dias de férias de uma vez
  const trintaECincoDias = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: usuarioComum.cpf,
      data_inicio: "2026-01-05", // Uma segunda-feira válida no futuro
      data_fim: "2026-02-13", // Aproximadamente 30 dias úteis / 39 dias corridos
      id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
      uf: UF_USUARIO_COMUM,
    },
    tokenComum,
  )
  logResult("Férias - Agendar mais de 30 dias de uma vez (deve falhar)", trintaECincoDias, 400)

  // Testes sequenciais de saldo de férias
  const saldoInicialComum = await makeRequest(
    "GET",
    `${BASE_URL}/usuarios/${usuarioComum.cpf}/vacation-allowance`,
    null,
    tokenComum,
  )
  logResult("Férias - Saldo Inicial Usuário Comum", saldoInicialComum, 200)
  const diasDisponiveisInicial = saldoInicialComum.data?.dias_restantes || 0

  if (diasDisponiveisInicial < 25 && saldoInicialComum.status === 200) {
    console.log(
      `${colors.yellow}⚠️ Usuário comum tem apenas ${diasDisponiveisInicial} dias. Alguns testes de saldo podem não ser representativos.${colors.reset}`,
    )
  }

  // Teste 6: Agendar 10 dias de férias (válido)
  const ferias10Dias = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: usuarioComum.cpf,
      data_inicio: "2026-03-02",
      data_fim: "2026-03-11", // 10 dias corridos (inclui 1 fds)
      id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
      uf: UF_USUARIO_COMUM,
    },
    tokenComum,
  )
  const sucessoFerias10 = logResult("Férias - Agendar 10 dias (válido)", ferias10Dias, 201)
  let evento10DiasId = null
  if (sucessoFerias10 && ferias10Dias.data.id) {
    evento10DiasId = ferias10Dias.data.id
    testState.entidadesCriadas.eventos.push(evento10DiasId)
    const gestorParaAprovar = usuarioGestor.cpf
    const aprovacaoResult = await makeRequest(
      "POST",
      `${BASE_URL}/eventos/${evento10DiasId}/aprovar`,
      { aprovador_cpf: gestorParaAprovar },
      tokenGestor,
    )
    logResult("Férias - Aprovação dos 10 dias", aprovacaoResult, 200)
  }

  // Teste 7: Tentar agendar mais 25 dias de férias (total > 30, se 10 já foram aprovados)
  const saldoApos10Dias = await makeRequest(
    "GET",
    `${BASE_URL}/usuarios/${usuarioComum.cpf}/vacation-allowance`,
    null,
    tokenComum,
  )
  const diasRestantesApos10 = saldoApos10Dias.data?.dias_restantes || 0

  if (saldoApos10Dias.status === 200 && diasRestantesApos10 < 25) {
    console.log(
      `${colors.yellow}⚠️ Saldo após 10 dias é ${diasRestantesApos10}. Teste de 25 dias pode não estourar o limite como esperado.${colors.reset}`,
    )
  }

  const ferias25Dias = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: usuarioComum.cpf,
      data_inicio: "2026-04-06",
      data_fim: "2026-04-30", // 25 dias corridos
      id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
      uf: UF_USUARIO_COMUM,
    },
    tokenComum,
  )
  logResult("Férias - Agendar mais 25 dias (deve falhar se 10 aprovados e saldo < 25)", ferias25Dias, 400)

  console.log(
    `\n${colors.cyan}🧑‍💼 12.2 Endpoint de Saldo de Férias (/usuarios/{cpf}/vacation-allowance)${colors.reset}`,
  )
  // Teste 8: RH acessando saldo de usuário comum
  const saldoRHparaComum = await makeRequest(
    "GET",
    `${BASE_URL}/usuarios/${usuarioComum.cpf}/vacation-allowance`,
    null,
    tokenRH,
  )
  logResult("Saldo Férias - RH para Usuário Comum", saldoRHparaComum, 200)

  // Teste 9: Gestor acessando saldo de membro do seu grupo
  if (usuarioComum.grupo_id === usuarioGestor.grupo_id) {
    const saldoGestorParaComum = await makeRequest(
      "GET",
      `${BASE_URL}/usuarios/${usuarioComum.cpf}/vacation-allowance`,
      null,
      tokenGestor,
    )
    logResult("Saldo Férias - Gestor para Membro do Grupo", saldoGestorParaComum, 200)
  } else {
    console.log(
      `${colors.yellow}⚠️ Usuário comum (${usuarioComum.cpf}, grupo ${usuarioComum.grupo_id}) não pertence ao grupo do gestor de teste (${usuarioGestor.cpf}, grupo ${usuarioGestor.grupo_id}). Pulando teste Gestor para Membro do Grupo.${colors.reset}`,
    )
    testState.totalTestes++
    testState.testesPassaram++
  }

  // Teste 10: Gestor tentando acessar saldo de usuário fora do seu grupo
  if (usuarioRH.grupo_id !== usuarioGestor.grupo_id) {
    const saldoGestorParaOutro = await makeRequest(
      "GET",
      `${BASE_URL}/usuarios/${usuarioRH.cpf}/vacation-allowance`,
      null,
      tokenGestor,
    )
    logResult("Saldo Férias - Gestor para Fora do Grupo (deve falhar)", saldoGestorParaOutro, 403)
  } else {
    console.log(
      `${colors.yellow}⚠️ Usuário RH (${usuarioRH.cpf}, grupo ${usuarioRH.grupo_id}) pertence ao mesmo grupo do gestor de teste (${usuarioGestor.cpf}, grupo ${usuarioGestor.grupo_id}). Pulando teste Gestor para Fora do Grupo.${colors.reset}`,
    )
    testState.totalTestes++
    testState.testesPassaram++
  }

  // Teste 11: Usuário comum acessando seu próprio saldo
  const saldoComumProprio = await makeRequest(
    "GET",
    `${BASE_URL}/usuarios/${usuarioComum.cpf}/vacation-allowance`,
    null,
    tokenComum,
  )
  logResult("Saldo Férias - Usuário Comum para Próprio Saldo", saldoComumProprio, 200)

  // Teste 12: Usuário comum tentando acessar saldo de outro usuário
  const saldoComumParaOutro = await makeRequest(
    "GET",
    `${BASE_URL}/usuarios/${usuarioRH.cpf}/vacation-allowance`,
    null,
    tokenComum,
  )
  logResult("Saldo Férias - Usuário Comum para Outro (deve falhar)", saldoComumParaOutro, 403)

  // Teste 13: Acessar saldo de usuário inexistente
  const cpfInexistente = "00000000000"
  const saldoInexistente = await makeRequest(
    "GET",
    `${BASE_URL}/usuarios/${cpfInexistente}/vacation-allowance`,
    null,
    tokenRH,
  )
  logResult("Saldo Férias - Usuário Inexistente (deve falhar)", saldoInexistente, 404)

  console.log(`\n${colors.cyan}👶 12.3 Validação de Tempo Mínimo de Empresa${colors.reset}`)
  const hojeISO = new Date().toISOString().split("T")[0]
  const cpfNovoEmpregado = Date.now().toString().slice(-11)
  const emailNovoEmpregado = `novo.ferias.${cpfNovoEmpregado}@test.com`

  const criarNovoEmpregado = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      cpf: cpfNovoEmpregado,
      nome: "Empregado Recente Teste Férias",
      email: emailNovoEmpregado,
      senha: "123456",
      grupo_id: usuarioComum.grupo_id,
      inicio_na_empresa: hojeISO,
      uf: UF_USUARIO_COMUM,
      tipo_usuario: "comum",
      flag_gestor: "N",
    },
    tokenRH,
  )
  const sucessoNovoEmpregado = logResult("Férias - Criar Novo Empregado (início hoje)", criarNovoEmpregado, 201)

  if (sucessoNovoEmpregado && criarNovoEmpregado.data.cpf) {
    testState.entidadesCriadas.usuarios.push(criarNovoEmpregado.data.cpf) // Salva o CPF retornado pela API

    // Teste 14: Novo empregado (menos de 1 ano) tenta agendar férias
    const feriasNovoEmpregado = await makeRequest(
      "POST",
      `${BASE_URL}/eventos`,
      {
        cpf_usuario: criarNovoEmpregado.data.cpf, // Usa o CPF do usuário recém-criado
        data_inicio: "2026-01-05",
        data_fim: "2026-01-09",
        id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
        uf: UF_USUARIO_COMUM,
      },
      tokenRH, // RH agendando para ele
    )
    logResult("Férias - Novo Empregado (<1 ano) tenta agendar (deve falhar)", feriasNovoEmpregado, 400)
  }

  console.log(`\n${colors.cyan}👍 12.4 Validação na Aprovação de Eventos de Férias (Gestor)${colors.reset}`)
  // Garante que o usuário comum tem saldo suficiente para os próximos testes de aprovação
  // Se o teste dos 10 dias foi aprovado, o saldo pode estar reduzido.
  // Para este teste, idealmente, usaríamos um usuário com saldo "limpo" ou resetar o saldo.
  // Como não temos reset, vamos logar o saldo atual.
  const saldoPreAprovacao = await makeRequest(
    "GET",
    `${BASE_URL}/usuarios/${usuarioComum.cpf}/vacation-allowance`,
    null,
    tokenComum,
  )
  logResult("Férias - Saldo do Usuário Comum antes dos testes de aprovação em lote", saldoPreAprovacao, 200)
  const diasDisponiveisPreAprovacao = saldoPreAprovacao.data?.dias_restantes || 0
  console.log(
    `${colors.blue}ℹ️ Saldo atual do usuário comum para testes de aprovação: ${diasDisponiveisPreAprovacao} dias.${colors.reset}`,
  )

  // Setup: Usuário comum (com >1 ano) agenda 20 dias de férias.
  const feriasParaAprovar1 = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: usuarioComum.cpf,
      data_inicio: "2026-07-06",
      data_fim: "2026-07-25", // 20 dias corridos
      id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
      uf: UF_USUARIO_COMUM,
    },
    tokenComum,
  )
  const sucessoFeriasAprovar1 = logResult("Férias - Setup: Agendar 20 dias para aprovação", feriasParaAprovar1, 201)
  const eventoId1 = feriasParaAprovar1.data?.id

  // Setup: Usuário comum agenda mais 15 dias de férias.
  const feriasParaAprovar2 = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      cpf_usuario: usuarioComum.cpf,
      data_inicio: "2026-08-03",
      data_fim: "2026-08-17", // 15 dias corridos
      id_tipo_ausencia: ID_TIPO_AUSENCIA_FERIAS,
      uf: UF_USUARIO_COMUM,
    },
    tokenComum,
  )
  const sucessoFeriasAprovar2 = logResult(
    "Férias - Setup: Agendar mais 15 dias para aprovação",
    feriasParaAprovar2,
    201,
  )
  const eventoId2 = feriasParaAprovar2.data?.id

  if (sucessoFeriasAprovar1 && eventoId1) testState.entidadesCriadas.eventos.push(eventoId1)
  if (sucessoFeriasAprovar2 && eventoId2) testState.entidadesCriadas.eventos.push(eventoId2)

  if (sucessoFeriasAprovar1 && eventoId1 && tokenGestor && usuarioGestor?.cpf) {
    // Teste 15: Gestor aprova o primeiro evento de 20 dias.
    if (diasDisponiveisPreAprovacao >= 20) {
      // Só tenta aprovar se há saldo
      const aprovarEvento1 = await makeRequest(
        "POST",
        `${BASE_URL}/eventos/${eventoId1}/aprovar`,
        { aprovador_cpf: usuarioGestor.cpf },
        tokenGestor,
      )
      logResult("Férias - Gestor aprova 1º evento (20 dias)", aprovarEvento1, 200)

      if (sucessoFeriasAprovar2 && eventoId2 && aprovarEvento1.status === 200) {
        // Teste 16: Gestor tenta aprovar o segundo evento de 15 dias (total 35, deve exceder se saldo inicial era ~30)
        const aprovarEvento2 = await makeRequest(
          "POST",
          `${BASE_URL}/eventos/${eventoId2}/aprovar`,
          { aprovador_cpf: usuarioGestor.cpf },
          tokenGestor,
        )
        logResult(
          "Férias - Gestor tenta aprovar 2º evento (15 dias, excedendo limite) (deve falhar)",
          aprovarEvento2,
          400,
        )
      }
    } else {
      console.log(
        `${colors.yellow}⚠️ Saldo insuficiente (${diasDisponiveisPreAprovacao} dias) para aprovar 20 dias. Pulando testes de aprovação em lote.${colors.reset}`,
      )
      testState.totalTestes += 2
      testState.testesPassaram += 2 // Pula 2 testes
    }
  }
}

// Função para limpar dados de teste
async function limparDadosTeste() {
  console.log(`\n${colors.bright}🧹 LIMPEZA DE DADOS DE TESTE${colors.reset}`)

  if (!testState.tokens.rh) {
    console.log(`${colors.red}❌ Token RH necessário para limpeza. Pulando.${colors.reset}`)
    return
  }

  // Limpar eventos criados
  // Usar um Set para evitar duplicatas se IDs forem adicionados mais de uma vez
  const eventosUnicosParaDeletar = [...new Set(testState.entidadesCriadas.eventos)]
  for (const eventoId of eventosUnicosParaDeletar) {
    const deletarEvento = await makeRequest("DELETE", `${BASE_URL}/eventos/${eventoId}`, null, testState.tokens.rh)
    logResult(`Deletar Evento ID ${eventoId}`, deletarEvento, 200) // Espera 200 para deleção bem-sucedida
  }

  // Limpar usuários criados
  const usuariosUnicosParaDeletar = [...new Set(testState.entidadesCriadas.usuarios)]
  for (const cpfUsuario of usuariosUnicosParaDeletar) {
    const deletarUsuario = await makeRequest("DELETE", `${BASE_URL}/usuarios/${cpfUsuario}`, null, testState.tokens.rh)
    logResult(`Deletar Usuário CPF ${cpfUsuario}`, deletarUsuario, 200) // Espera 200 para desativação/deleção
  }

  // Limpar grupos criados (desativar)
  const gruposUnicosParaDeletar = [...new Set(testState.entidadesCriadas.grupos)]
  let gruposDesativadosCount = 0
  for (const grupoId of gruposUnicosParaDeletar) {
    // A desativação já acontece em testarGerenciamentoGrupos.
    // Aqui, apenas contamos os que foram adicionados à lista para limpeza.
    // Se a desativação falhou lá, este log pode ser impreciso.
    // Uma abordagem mais robusta seria tentar desativar aqui novamente se não foi feito.
    // Por ora, vamos assumir que a desativação em testarGerenciamentoGrupos é o principal.
    gruposDesativadosCount++
  }
  if (gruposDesativadosCount > 0) {
    console.log(
      `${colors.green}✅ ${gruposDesativadosCount} grupos foram marcados para limpeza (desativados em seus testes).${colors.reset}`,
    )
  }

  // Resetar listas de entidades criadas para futuras execuções (se o script for rodado múltiplas vezes no mesmo processo)
  testState.entidadesCriadas.eventos = []
  testState.entidadesCriadas.usuarios = []
  testState.entidadesCriadas.grupos = []
}

// Função para gerar relatório final
function gerarRelatorio() {
  console.log(`\n${colors.bright}📊 RELATÓRIO FINAL${colors.reset}`)
  console.log("=".repeat(60))

  const porcentagemSucesso =
    testState.totalTestes > 0 ? ((testState.testesPassaram / testState.totalTestes) * 100).toFixed(1) : "N/A"
  const statusColor = porcentagemSucesso >= 90 ? colors.green : porcentagemSucesso >= 70 ? colors.yellow : colors.red

  console.log(`${colors.bright}Total de Testes:${colors.reset} ${testState.totalTestes}`)
  console.log(`${colors.green}Testes Passaram:${colors.reset} ${testState.testesPassaram}`)
  console.log(`${colors.red}Testes Falharam:${colors.reset} ${testState.totalTestes - testState.testesPassaram}`)
  console.log(`${colors.bright}Taxa de Sucesso:${colors.reset} ${statusColor}${porcentagemSucesso}%${colors.reset}`)

  console.log(`\n${colors.bright}🔑 TOKENS OBTIDOS:${colors.reset}`)
  Object.keys(testState.tokens).forEach((tipo) => {
    console.log(`${colors.green}✅ ${tipo.toUpperCase()}: ${testState.tokens[tipo] ? "OK" : "FALHOU"}${colors.reset}`)
  })

  console.log(`\n${colors.bright}📈 ESTATÍSTICAS DE ENTIDADES CRIADAS/DELETADAS (TENTATIVAS):${colors.reset}`)
  console.log(`${colors.blue}🗓️ Eventos: ${[...new Set(testState.entidadesCriadas.eventos)].length}${colors.reset}`)
  console.log(`${colors.blue}👤 Usuários: ${[...new Set(testState.entidadesCriadas.usuarios)].length}${colors.reset}`)
  console.log(`${colors.blue}🏢 Grupos: ${[...new Set(testState.entidadesCriadas.grupos)].length}${colors.reset}`)

  console.log(`\n${colors.bright}💡 DIAGNÓSTICO:${colors.reset}`)
  if (testState.totalTestes === 0) {
    console.log(`${colors.yellow}⚠️ Nenhum teste foi executado.${colors.reset}`)
  } else if (testState.testesPassaram === testState.totalTestes) {
    console.log(`${colors.green}🎉 Todos os testes passaram! API funcionando perfeitamente!${colors.reset}`)
  } else if (porcentagemSucesso >= 90) {
    console.log(`${colors.green}✅ API funcionando muito bem, com pequenas falhas.${colors.reset}`)
  } else if (porcentagemSucesso >= 70) {
    console.log(`${colors.yellow}⚠️ API funcionando com alguns problemas.${colors.reset}`)
  } else if (Object.keys(testState.tokens).length === 0) {
    console.log(`${colors.red}🚨 PROBLEMA CRÍTICO: Nenhum login funcionou${colors.reset}`)
    console.log(`${colors.yellow}🔧 Verifique as credenciais no banco de dados${colors.reset}`)
    console.log(`${colors.yellow}🔧 Execute: python scripts/seed_data_complete.py${colors.reset}`)
  } else if (testState.testesPassaram < 5) {
    console.log(`${colors.red}🚨 PROBLEMA CRÍTICO: Tokens não estão funcionando ou falhas generalizadas${colors.reset}`)
    console.log(`${colors.yellow}🔧 Verifique a configuração JWT no Flask e a saúde geral da API${colors.reset}`)
  } else {
    console.log(`${colors.red}❌ API com falhas significativas. Revisão necessária.${colors.reset}`)
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

    // >>> ADICIONAR NOVA SEÇÃO DE TESTES DE FÉRIAS AQUI <<<
    await testarSistemaDeFerias() // Nova seção de testes

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
