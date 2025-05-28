const BASE_URL = "http://localhost:5000/api"

async function makeRequest(method, url, data = null, headers = {}) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  }

  if (data) options.body = JSON.stringify(data)

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

  // Simulando usuários
  const usuarios = {
    rh: { id: 1, header: { "X-User-ID": "1" } },
    gestor: { id: 2, header: { "X-User-ID": "2" } },
    comum_1: { id: 3, header: { "X-User-ID": "3" } }, // Grupo Dev
    comum_2: { id: 4, header: { "X-User-ID": "4" } }, // Grupo Dev
    comum_outro_grupo: { id: 5, header: { "X-User-ID": "5" } }, // Grupo Marketing
  }

  console.log("=== TESTE 1: Acesso sem autenticação ===")
  const semAuth = await makeRequest("GET", `${BASE_URL}/empresas`)
  console.log(`Status: ${semAuth.status} - ${semAuth.data.erro || "OK"}`)

  console.log("\n=== TESTE 2: RH tentando acessar empresa de outra empresa ===")
  const rhEmpresa = await makeRequest("GET", `${BASE_URL}/empresas/999`, null, usuarios.rh.header)
  console.log(`Status: ${rhEmpresa.status} - ${rhEmpresa.data.erro || "OK"}`)

  console.log("\n=== TESTE 3: Gestor tentando acessar grupo que não gerencia ===")
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
    usuarios.comum_1.header,
  )
  console.log(`Status: ${comumCriar.status} - ${comumCriar.data.erro || "OK"}`)

  console.log("\n=== TESTE 5: Usuário comum tentando ver eventos de outro grupo ===")
  const comumEventos = await makeRequest(
    "GET",
    `${BASE_URL}/eventos?usuario_id=${usuarios.comum_outro_grupo.id}`,
    null,
    usuarios.comum_1.header
  )
  console.log(`Status: ${comumEventos.status} - ${comumEventos.data.erro || "OK"}`)

  console.log("\n=== TESTE 6: Usuário comum vendo eventos de colega do mesmo grupo (somente leitura) ===")
  const eventosMesmoGrupo = await makeRequest(
    "GET",
    `${BASE_URL}/eventos?usuario_id=${usuarios.comum_2.id}`,
    null,
    usuarios.comum_1.header
  )
  console.log(`Status: ${eventosMesmoGrupo.status} - ${eventosMesmoGrupo.data.erro || `${eventosMesmoGrupo.data.length} eventos`}`)

  console.log("\n=== TESTE 7: Usuário comum tentando deletar evento de outro ===")

  // Criar evento para outro usuário (comum_2)
  const eventoOutroUsuario = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      usuario_id: usuarios.comum_2.id,
      data_inicio: "2024-08-01",
      data_fim: "2024-08-05",
      tipo_ausencia: "Férias",
    },
    usuarios.rh.header // RH pode criar evento para qualquer um
  )

  if (eventoOutroUsuario.status === 201) {
    const tentativaDelete = await makeRequest(
      "DELETE",
      `${BASE_URL}/eventos/${eventoOutroUsuario.data.id}`,
      null,
      usuarios.comum_1.header // comum_1 tenta deletar evento de comum_2
    )
    console.log(`Status: ${tentativaDelete.status} - ${tentativaDelete.data.erro || "Evento deletado (NÃO DEVERIA)"}`)
  } else {
    console.log(`Erro ao criar evento de outro usuário para o teste: ${eventoOutroUsuario.status} - ${eventoOutroUsuario.data.erro}`)
  }

  console.log("\n=== TESTE 8: Gestor tentando aprovar evento de outro grupo ===")
  const criarEventoOutroGrupo = await makeRequest(
    "POST",
    `${BASE_URL}/eventos`,
    {
      usuario_id: usuarios.comum_outro_grupo.id,
      data_inicio: "2024-07-01",
      data_fim: "2024-07-05",
      tipo_ausencia: "Férias",
    },
    usuarios.rh.header
  )

  if (criarEventoOutroGrupo.status === 201) {
    const aprovar = await makeRequest(
      "POST",
      `${BASE_URL}/eventos/${criarEventoOutroGrupo.data.id}/aprovar`,
      {
        aprovador_id: usuarios.gestor.id,
        observacoes: "Tentativa fora do escopo",
      },
      usuarios.gestor.header
    )
    console.log(`Status: ${aprovar.status} - ${aprovar.data.erro || "Aprovado (NÃO DEVERIA)"}`)
  } else {
    console.log("Erro ao criar evento para testar aprovação cruzada")
  }

  console.log("\n=== TESTE 9: Acessos válidos dentro do escopo ===")
  const rhValido = await makeRequest("GET", `${BASE_URL}/grupos`, null, usuarios.rh.header)
  console.log(`RH listando grupos: ${rhValido.status} - ${rhValido.data.length || 0} grupos`)

  const gestorValido = await makeRequest("GET", `${BASE_URL}/usuarios?grupo_id=1`, null, usuarios.gestor.header)
  console.log(`Gestor listando usuários: ${gestorValido.status} - ${gestorValido.data.length || 0} usuários`)

  const comumEventosProprios = await makeRequest(
    "GET",
    `${BASE_URL}/eventos?usuario_id=${usuarios.comum_1.id}`,
    null,
    usuarios.comum_1.header
  )
  console.log(`Usuário comum vendo próprios eventos: ${comumEventosProprios.status} - ${comumEventosProprios.data.length || 0} eventos`)

  console.log("\n🔒 Testes de segurança concluídos!")
}

testSecurity().catch(console.error)
