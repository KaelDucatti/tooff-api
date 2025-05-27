// Script para testar todos os endpoints da API Flask
const BASE_URL = "http://localhost:5000/api"

// Função auxiliar para fazer requisições
async function makeRequest(method, url, data = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
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

// Função para exibir resultados
function logResult(testName, result) {
  console.log(`\n=== ${testName} ===`)
  console.log(`Status: ${result.status}`)
  console.log("Response:", JSON.stringify(result.data, null, 2))
}

// Função principal de teste
async function testAllEndpoints() {
  console.log("🚀 Iniciando testes da API Flask...\n")

  // ==================== AUTENTICAÇÃO ====================
  console.log("📋 TESTANDO AUTENTICAÇÃO")

  // Login válido - RH
  const loginResult = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "maria.rh@techsolutions.com",
    senha: "123456",
  })
  logResult("Login RH", loginResult)

  // Login válido - Gestor
  const loginGestor = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "joao.gestor@techsolutions.com",
    senha: "123456",
  })
  logResult("Login Gestor", loginGestor)

  // Login inválido
  const loginInvalido = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "inexistente@test.com",
    senha: "senha_errada",
  })
  logResult("Login Inválido", loginInvalido)

  // ==================== EMPRESAS ====================
  console.log("\n📋 TESTANDO EMPRESAS")

  // Listar empresas
  const empresas = await makeRequest("GET", `${BASE_URL}/empresas`)
  logResult("Listar Empresas", empresas)

  // Obter empresa específica
  const empresa = await makeRequest("GET", `${BASE_URL}/empresas/1`)
  logResult("Obter Empresa 1", empresa)

  // Criar nova empresa
  const novaEmpresa = await makeRequest("POST", `${BASE_URL}/empresas`, {
    nome: "Nova Empresa LTDA",
    cnpj: "98.765.432/0001-10",
    endereco: "Rua Nova, 456",
    telefone: "(11) 9876-5432",
    email: "contato@novaempresa.com",
  })
  logResult("Criar Empresa", novaEmpresa)

  // Atualizar empresa (se criação foi bem-sucedida)
  if (novaEmpresa.status === 201) {
    const atualizarEmpresa = await makeRequest("PUT", `${BASE_URL}/empresas/2`, {
      nome: "Nova Empresa LTDA - Atualizada",
      telefone: "(11) 1111-2222",
    })
    logResult("Atualizar Empresa", atualizarEmpresa)
  }

  // ==================== GRUPOS ====================
  console.log("\n📋 TESTANDO GRUPOS")

  // Listar grupos
  const grupos = await makeRequest("GET", `${BASE_URL}/grupos`)
  logResult("Listar Grupos", grupos)

  // Listar grupos por empresa
  const gruposEmpresa = await makeRequest("GET", `${BASE_URL}/grupos?empresa_id=1`)
  logResult("Grupos da Empresa 1", gruposEmpresa)

  // Obter grupo específico
  const grupo = await makeRequest("GET", `${BASE_URL}/grupos/1`)
  logResult("Obter Grupo 1", grupo)

  // Criar novo grupo
  const novoGrupo = await makeRequest("POST", `${BASE_URL}/grupos`, {
    nome: "Vendas",
    empresa_id: 1,
    descricao: "Equipe de vendas e relacionamento com cliente",
  })
  logResult("Criar Grupo", novoGrupo)

  // Estatísticas do grupo
  const statsGrupo = await makeRequest("GET", `${BASE_URL}/grupos/1/estatisticas`)
  logResult("Estatísticas Grupo 1", statsGrupo)

  // ==================== USUÁRIOS ====================
  console.log("\n📋 TESTANDO USUÁRIOS")

  // Listar usuários
  const usuarios = await makeRequest("GET", `${BASE_URL}/usuarios`)
  logResult("Listar Usuários", usuarios)

  // Listar usuários por grupo
  const usuariosGrupo = await makeRequest("GET", `${BASE_URL}/usuarios?grupo_id=1`)
  logResult("Usuários do Grupo 1", usuariosGrupo)

  // Listar usuários por tipo
  const gestores = await makeRequest("GET", `${BASE_URL}/usuarios?tipo_usuario=gestor`)
  logResult("Listar Gestores", gestores)

  // Obter usuário específico
  const usuario = await makeRequest("GET", `${BASE_URL}/usuarios/1`)
  logResult("Obter Usuário 1", usuario)

  // Criar novo usuário
  const novoUsuario = await makeRequest("POST", `${BASE_URL}/usuarios`, {
    nome: "Pedro Silva",
    email: "pedro.silva@techsolutions.com",
    senha: "123456",
    inicio_na_empresa: "2024-01-15",
    tipo_usuario: "comum",
    grupo_id: 1,
  })
  logResult("Criar Usuário", novoUsuario)

  // ==================== EVENTOS ====================
  console.log("\n📋 TESTANDO EVENTOS")

  // Listar eventos
  const eventos = await makeRequest("GET", `${BASE_URL}/eventos`)
  logResult("Listar Eventos", eventos)

  // Listar eventos por usuário
  const eventosUsuario = await makeRequest("GET", `${BASE_URL}/eventos?usuario_id=3`)
  logResult("Eventos do Usuário 3", eventosUsuario)

  // Listar eventos por grupo
  const eventosGrupo = await makeRequest("GET", `${BASE_URL}/eventos?grupo_id=1`)
  logResult("Eventos do Grupo 1", eventosGrupo)

  // Listar eventos pendentes
  const eventosPendentes = await makeRequest("GET", `${BASE_URL}/eventos?status=pendente`)
  logResult("Eventos Pendentes", eventosPendentes)

  // Obter evento específico
  const evento = await makeRequest("GET", `${BASE_URL}/eventos/1`)
  logResult("Obter Evento 1", evento)

  // Criar novo evento
  const novoEvento = await makeRequest("POST", `${BASE_URL}/eventos`, {
    usuario_id: 3,
    data_inicio: "2024-03-15",
    data_fim: "2024-03-19",
    tipo_ausencia: "Férias",
    turno: "Dia",
    descricao: "Férias de março",
  })
  logResult("Criar Evento", novoEvento)

  // Aprovar evento (se criação foi bem-sucedida)
  if (novoEvento.status === 201) {
    const aprovarEvento = await makeRequest("POST", `${BASE_URL}/eventos/3/aprovar`, {
      aprovador_id: 2,
      observacoes: "Aprovado pelo gestor",
    })
    logResult("Aprovar Evento", aprovarEvento)
  }

  // Criar outro evento para rejeitar
  const eventoRejeitar = await makeRequest("POST", `${BASE_URL}/eventos`, {
    usuario_id: 4,
    data_inicio: "2024-04-01",
    data_fim: "2024-04-01",
    tipo_ausencia: "Assiduidade",
    descricao: "Consulta médica",
  })
  logResult("Criar Evento para Rejeitar", eventoRejeitar)

  // Rejeitar evento
  if (eventoRejeitar.status === 201) {
    const rejeitarEvento = await makeRequest("POST", `${BASE_URL}/eventos/4/rejeitar`, {
      aprovador_id: 2,
      observacoes: "Precisa reagendar",
    })
    logResult("Rejeitar Evento", rejeitarEvento)
  }

  // ==================== CALENDÁRIO ====================
  console.log("\n📋 TESTANDO CALENDÁRIO")

  // Calendário geral
  const calendario = await makeRequest("GET", `${BASE_URL}/calendario`)
  logResult("Calendário Geral", calendario)

  // Calendário do grupo 1
  const calendarioGrupo = await makeRequest("GET", `${BASE_URL}/calendario/grupo/1`)
  logResult("Calendário Grupo 1", calendarioGrupo)

  // Calendário incluindo eventos pendentes
  const calendarioCompleto = await makeRequest("GET", `${BASE_URL}/calendario?apenas_aprovados=false`)
  logResult("Calendário Completo", calendarioCompleto)

  // ==================== TESTES DE ERRO ====================
  console.log("\n📋 TESTANDO CASOS DE ERRO")

  // Empresa inexistente
  const empresaInexistente = await makeRequest("GET", `${BASE_URL}/empresas/999`)
  logResult("Empresa Inexistente", empresaInexistente)

  // Usuário inexistente
  const usuarioInexistente = await makeRequest("GET", `${BASE_URL}/usuarios/999`)
  logResult("Usuário Inexistente", usuarioInexistente)

  // Criar usuário com dados inválidos
  const usuarioInvalido = await makeRequest("POST", `${BASE_URL}/usuarios`, {
    nome: "Teste",
    // email ausente
    senha: "123456",
  })
  logResult("Criar Usuário Inválido", usuarioInvalido)

  // Criar evento com tipo inválido
  const eventoInvalido = await makeRequest("POST", `${BASE_URL}/eventos`, {
    usuario_id: 1,
    data_inicio: "2024-05-01",
    data_fim: "2024-05-01",
    tipo_ausencia: "TipoInexistente",
  })
  logResult("Criar Evento Inválido", eventoInvalido)

  console.log("\n✅ Testes concluídos!")
}

// Executar testes
testAllEndpoints().catch(console.error)
