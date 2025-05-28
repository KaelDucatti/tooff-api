// Script para testar as validações de segurança e escopo
const BASE_URL = "http://localhost:5000/api"

async function makeRequest(method, url, data = null, headers = {}) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
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

async function testSecurity() {
  console.log("🔒 Testando Validações de Segurança e Escopo\n")

  // Simula diferentes usuários (em produção seria JWT)
  const usuarios = {
    rh: { id: 1, header: { "X-User-ID": "1" } }, // Maria (RH)
    gestor: { id: 2, header: { "X-User-ID": "2" } }, // João (Gestor)
    comum: { id: 3, header: { "X-User-ID": "3" } }, // Ana (Comum)
  }

  console.log("=== TESTE 1: Acesso sem autenticação ===")
  const semAuth = await makeRequest("GET", `${BASE_URL}/empresas`)
  console.log(`Status: ${semAuth.status} - ${semAuth.data.erro || "OK"}`)

  console.log("\n=== TESTE 2: RH tentando acessar empresa de outra empresa ===")
  const rhEmpresa = await makeRequest("GET", `${BASE_URL}/empresas/999`, null, usuarios.rh.header)
  console.log(`Status: ${rhEmpresa.status} - ${rhEmpresa.data.erro || "OK"}`)

  console.log("\n=== TESTE 3: Gestor tentando acessar dados de outro grupo ===")
  const gestorGrupo = await makeRequest("GET", `${BASE_URL}/grupos/999`, null, usuarios.gestor.header)
  console.log(`Status: ${gestorGrupo.status} - ${gestorGrupo.data.erro || "OK"}`)

  console.log("\n=== TESTE 4: Usuário comum tentando criar usuário ===")
  const comumCriar = await makeRequest(
    "POST",
    `${BASE_URL}/usuarios`,
    {
      nome: "Teste",
      email: "teste@test.com",
      senha: "123456",
      inicio_na_empresa: "2024-01-01",
      grupo_id: 1,
    },
    usuarios.comum.header,
  )
  console.log(`Status: ${comumCriar.status} - ${comumCriar.data.erro || "OK"}`)

  console.log("\n=== TESTE 5: Usuário comum tentando ver eventos de outro usuário ===")
  const comumEventos = await makeRequest("GET", `${BASE_URL}/eventos?usuario_id=4`, null, usuarios.comum.header)
  console.log(`Status: ${comumEventos.status} - ${comumEventos.data.erro || "OK"}`)

  console.log("\n=== TESTE 6: Gestor tentando aprovar evento de outro grupo ===")
  // Primeiro cria um evento para usuário de outro grupo
  const eventoOutroGrupo = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      usuario_id: 5, // Usuário do grupo Marketing
      data_inicio: "2024-06-01",
      data_fim: "2024-06-01",
      tipo_ausencia: "Férias",
    },
    usuarios.rh.header,
  )

  if (eventoOutroGrupo.status === 201) {
    const aprovar = await makeRequest(
      "POST",
      `${BASE_URL}/eventos/${eventoOutroGrupo.data.id}/aprovar`,
      {
        aprovador_id: 2, // João (gestor do grupo Dev)
        observacoes: "Teste",
      },
      usuarios.gestor.header,
    )
    console.log(`Status: ${aprovar.status} - ${aprovar.data.erro || "OK"}`)
  }

  console.log("\n=== TESTE 7: Acessos válidos dentro do escopo ===")

  // RH acessando sua empresa
  const rhValido = await makeRequest("GET", `${BASE_URL}/grupos`, null, usuarios.rh.header)
  console.log(`RH listando grupos: ${rhValido.status} - ${rhValido.data.length || 0} grupos`)

  // Gestor acessando seu grupo
  const gestorValido = await makeRequest("GET", `${BASE_URL}/usuarios?grupo_id=1`, null, usuarios.gestor.header)
  console.log(`Gestor listando usuários do grupo: ${gestorValido.status} - ${gestorValido.data.length || 0} usuários`)

  // Usuário comum acessando próprios eventos
  const comumValido = await makeRequest("GET", `${BASE_URL}/eventos?usuario_id=3`, null, usuarios.comum.header)
  console.log(`Usuário comum vendo próprios eventos: ${comumValido.status} - ${comumValido.data.length || 0} eventos`)

  console.log("\n🔒 Testes de segurança concluídos!")
}

testSecurity().catch(console.error)
