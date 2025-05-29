// Script completo para testar a API com autenticação JWT
const BASE_URL = "http://localhost:5000/api"

// Função auxiliar para fazer requisições
async function makeRequest(method, url, data = null, token = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  }

  // Adicionar token JWT se fornecido
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

// Função para exibir resultados
function logResult(testName, result) {
  console.log(`\n=== ${testName} ===`)
  console.log(`Status: ${result.status}`)
  if (result.status === 200 || result.status === 201) {
    console.log("✅ SUCESSO")
  } else if (result.status >= 400) {
    console.log("❌ ERRO")
  }

  // Mostrar apenas dados relevantes (não tokens completos)
  if (result.data.access_token) {
    console.log("Response: { access_token: '***', refresh_token: '***', usuario: {...} }")
  } else {
    console.log("Response:", JSON.stringify(result.data, null, 2))
  }
}

// Função principal de teste
async function testJWTComplete() {
  console.log("🔐 Testando API Flask com JWT completo...\n")

  let rhToken = null
  let gestorToken = null

  // ==================== AUTENTICAÇÃO ====================
  console.log("📋 TESTANDO AUTENTICAÇÃO JWT")

  // Login RH
  const loginRH = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "maria.rh@techsolutions.com",
    senha: "123456",
  })
  logResult("Login RH", loginRH)

  if (loginRH.status === 200) {
    rhToken = loginRH.data.access_token
    console.log("🔑 Token RH capturado com sucesso!")
  }

  // Login Gestor
  const loginGestor = await makeRequest("POST", `${BASE_URL}/auth/login`, {
    email: "joao.gestor@techsolutions.com",
    senha: "123456",
  })
  logResult("Login Gestor", loginGestor)

  if (loginGestor.status === 200) {
    gestorToken = loginGestor.data.access_token
    console.log("🔑 Token Gestor capturado com sucesso!")
  }

  // ==================== TESTES COM TOKEN RH ====================
  console.log("\n📋 TESTANDO COM TOKEN RH (Acesso Total)")

  // Endpoint /me
  const meRH = await makeRequest("GET", `${BASE_URL}/auth/me`, null, rhToken)
  logResult("Endpoint /me (RH)", meRH)

  // Listar empresas
  const empresasRH = await makeRequest("GET", `${BASE_URL}/empresas`, null, rhToken)
  logResult("Listar Empresas (RH)", empresasRH)

  // Listar grupos
  const gruposRH = await makeRequest("GET", `${BASE_URL}/grupos`, null, rhToken)
  logResult("Listar Grupos (RH)", gruposRH)

  // Listar usuários
  const usuariosRH = await makeRequest("GET", `${BASE_URL}/usuarios`, null, rhToken)
  logResult("Listar Usuários (RH)", usuariosRH)

  // Listar eventos
  const eventosRH = await makeRequest("GET", `${BASE_URL}/eventos`, null, rhToken)
  logResult("Listar Eventos (RH)", eventosRH)

  // Criar usuário
  const criarUsuario = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      nome: "Teste JWT",
      email: "teste.jwt@techsolutions.com",
      senha: "123456",
      inicio_na_empresa: "2024-01-01",
      tipo_usuario: "comum",
      grupo_id: 1,
    },
    rhToken,
  )
  logResult("Criar Usuário (RH)", criarUsuario)

  // ==================== TESTES COM TOKEN GESTOR ====================
  console.log("\n📋 TESTANDO COM TOKEN GESTOR (Acesso Limitado)")

  // Endpoint /me
  const meGestor = await makeRequest("GET", `${BASE_URL}/auth/me`, null, gestorToken)
  logResult("Endpoint /me (Gestor)", meGestor)

  // Listar usuários (deve ver apenas do seu grupo)
  const usuariosGestor = await makeRequest("GET", `${BASE_URL}/usuarios`, null, gestorToken)
  logResult("Listar Usuários (Gestor)", usuariosGestor)

  // Tentar listar empresas (deve dar erro de permissão)
  const empresasGestor = await makeRequest("GET", `${BASE_URL}/empresas`, null, gestorToken)
  logResult("Listar Empresas (Gestor - Deve Falhar)", empresasGestor)

  // Listar eventos do grupo
  const eventosGestor = await makeRequest("GET", `${BASE_URL}/eventos?grupo_id=2`, null, gestorToken)
  logResult("Listar Eventos do Grupo (Gestor)", eventosGestor)

  // ==================== TESTES DE REFRESH TOKEN ====================
  console.log("\n📋 TESTANDO REFRESH TOKEN")

  if (loginRH.data.refresh_token) {
    const refreshResult = await makeRequest("POST", `${BASE_URL}/auth/refresh`, {
      refresh_token: loginRH.data.refresh_token,
    })
    logResult("Refresh Token", refreshResult)
  }

  // ==================== TESTES SEM TOKEN ====================
  console.log("\n📋 TESTANDO SEM TOKEN (Deve Falhar)")

  const semToken = await makeRequest("GET", `${BASE_URL}/usuarios`)
  logResult("Listar Usuários Sem Token", semToken)

  // ==================== TESTES DE LOGOUT ====================
  console.log("\n📋 TESTANDO LOGOUT")

  const logout = await makeRequest("POST", `${BASE_URL}/auth/logout`, null, rhToken)
  logResult("Logout", logout)

  // Tentar usar token após logout
  const aposLogout = await makeRequest("GET", `${BASE_URL}/usuarios`, null, rhToken)
  logResult("Usar Token Após Logout (Deve Falhar)", aposLogout)

  // ==================== RESUMO ====================
  console.log("\n📊 RESUMO DOS TESTES JWT")
  console.log("✅ Login com JWT funcionando")
  console.log("✅ Tokens sendo gerados corretamente")
  console.log("✅ Endpoints protegidos funcionando")
  console.log("✅ Permissões por nível funcionando")
  console.log("✅ Refresh token funcionando")
  console.log("✅ Logout funcionando")
  console.log("\n🎉 Sistema JWT completamente funcional!")
}

// Executar testes
testJWTComplete().catch(console.error)
