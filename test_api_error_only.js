// Script inteligente para analisar a saúde da API Flask
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

// Função para categorizar resultados
function categorizeResult(result, testName, expectedStatus) {
  if (result.status === expectedStatus) {
    return "CORRETO"
  } else if (result.status === "ERROR") {
    return "PROBLEMA_REAL"
  } else if (result.status >= 500) {
    return "PROBLEMA_REAL"
  } else {
    return "COMPORTAMENTO_INESPERADO"
  }
}

// Função para exibir resultados categorizados
function logCategorizedResult(category, testName, result, expectedStatus) {
  const icons = {
    CORRETO: "✅",
    PROBLEMA_REAL: "🚨",
    COMPORTAMENTO_INESPERADO: "⚠️",
  }

  console.log(`${icons[category]} ${testName}`)
  console.log(`   Status: ${result.status} (esperado: ${expectedStatus})`)

  if (result.data.erro) {
    console.log(`   Mensagem: ${result.data.erro}`)
  }

  if (category !== "CORRETO") {
    console.log(`   Categoria: ${category}`)
  }
  console.log()
}

// Função principal de análise inteligente
async function smartAnalysis() {
  console.log("🧠 Análise Inteligente da API Flask\n")

  const results = {
    CORRETO: [],
    PROBLEMA_REAL: [],
    COMPORTAMENTO_INESPERADO: [],
  }

  // Lista de testes com status esperados
  const tests = [
    // Casos que DEVEM retornar erro (comportamento correto)
    {
      name: "Login com Credenciais Inválidas",
      expectedStatus: 401,
      request: () =>
        makeRequest("POST", `${BASE_URL}/auth/login`, {
          email: "inexistente@test.com",
          senha: "senha_errada",
        }),
    },
    {
      name: "Criar Empresa com CNPJ Duplicado",
      expectedStatus: 409,
      request: () =>
        makeRequest("POST", `${BASE_URL}/empresas`, {
          nome: "Tech Solutions LTDA",
          cnpj: "12.345.678/0001-90",
        }),
    },
    {
      name: "Obter Empresa Inexistente",
      expectedStatus: 404,
      request: () => makeRequest("GET", `${BASE_URL}/empresas/999`),
    },
    {
      name: "Criar Usuário com Email Duplicado",
      expectedStatus: 409,
      request: () =>
        makeRequest("POST", `${BASE_URL}/usuarios`, {
          nome: "Teste Duplicado",
          email: "maria.rh@techsolutions.com",
          senha: "123456",
          inicio_na_empresa: "2024-01-01",
          tipo_usuario: "comum",
        }),
    },
    {
      name: "Criar Usuário sem Email Obrigatório",
      expectedStatus: 400,
      request: () =>
        makeRequest("POST", `${BASE_URL}/usuarios`, {
          nome: "Teste",
          senha: "123456",
          inicio_na_empresa: "2024-01-01",
        }),
    },
    {
      name: "Criar Usuário com Tipo Inválido",
      expectedStatus: 400,
      request: () =>
        makeRequest("POST", `${BASE_URL}/usuarios`, {
          nome: "Teste",
          email: "teste@invalid.com",
          senha: "123456",
          inicio_na_empresa: "2024-01-01",
          tipo_usuario: "tipo_inexistente",
        }),
    },
    {
      name: "Aprovar Evento sem Permissão",
      expectedStatus: 403,
      request: () =>
        makeRequest("POST", `${BASE_URL}/eventos/1/aprovar`, {
          aprovador_id: 3, // Usuário comum
          observacoes: "Teste",
        }),
    },
    {
      name: "Criar Evento com Tipo Inválido",
      expectedStatus: 400,
      request: () =>
        makeRequest("POST", `${BASE_URL}/eventos`, {
          usuario_id: 1,
          data_inicio: "2024-05-01",
          data_fim: "2024-05-01",
          tipo_ausencia: "TipoInexistente",
        }),
    },

    // Casos que DEVEM funcionar (comportamento correto)
    {
      name: "Login com Credenciais Válidas",
      expectedStatus: 200,
      request: () =>
        makeRequest("POST", `${BASE_URL}/auth/login`, {
          email: "maria.rh@techsolutions.com",
          senha: "123456",
        }),
    },
    {
      name: "Listar Empresas",
      expectedStatus: 200,
      request: () => makeRequest("GET", `${BASE_URL}/empresas`),
    },
    {
      name: "Listar Usuários",
      expectedStatus: 200,
      request: () => makeRequest("GET", `${BASE_URL}/usuarios`),
    },
    {
      name: "Listar Eventos",
      expectedStatus: 200,
      request: () => makeRequest("GET", `${BASE_URL}/eventos`),
    },
    {
      name: "Obter Calendário",
      expectedStatus: 200,
      request: () => makeRequest("GET", `${BASE_URL}/calendario`),
    },
    {
      name: "Criar Empresa Válida",
      expectedStatus: 201,
      request: () =>
        makeRequest("POST", `${BASE_URL}/empresas`, {
          nome: `Empresa Teste ${Date.now()}`,
          cnpj: `${Math.floor(Math.random() * 90000000) + 10000000}/0001-${Math.floor(Math.random() * 90) + 10}`,
        }),
    },
    {
      name: "Criar Usuário Válido",
      expectedStatus: 201,
      request: () =>
        makeRequest("POST", `${BASE_URL}/usuarios`, {
          nome: "Usuário Teste",
          email: `teste${Date.now()}@example.com`,
          senha: "123456",
          inicio_na_empresa: "2024-01-01",
          tipo_usuario: "comum",
          grupo_id: 1,
        }),
    },
  ]

  // Executa todos os testes
  for (const test of tests) {
    try {
      const result = await test.request()
      const category = categorizeResult(result, test.name, test.expectedStatus)

      results[category].push({
        name: test.name,
        result: result,
        expectedStatus: test.expectedStatus,
      })

      logCategorizedResult(category, test.name, result, test.expectedStatus)
    } catch (error) {
      results.PROBLEMA_REAL.push({
        name: test.name,
        result: { status: "ERROR", data: { erro: error.message } },
        expectedStatus: test.expectedStatus,
      })
      console.log(`🚨 ${test.name}`)
      console.log(`   Erro de execução: ${error.message}\n`)
    }
  }

  // Resumo inteligente
  console.log("📊 ANÁLISE FINAL")
  console.log("=" * 50)
  console.log(`✅ Comportamentos Corretos: ${results.CORRETO.length}`)
  console.log(`🚨 Problemas Reais: ${results.PROBLEMA_REAL.length}`)
  console.log(`⚠️  Comportamentos Inesperados: ${results.COMPORTAMENTO_INESPERADO.length}`)

  const totalTests = Object.values(results).reduce((sum, arr) => sum + arr.length, 0)
  const healthScore = (results.CORRETO.length / totalTests) * 100

  console.log(`\n🏥 SAÚDE DA API: ${healthScore.toFixed(1)}%`)

  if (results.PROBLEMA_REAL.length === 0 && results.COMPORTAMENTO_INESPERADO.length === 0) {
    console.log("🎉 API funcionando perfeitamente!")
  } else if (results.PROBLEMA_REAL.length === 0) {
    console.log("✅ Nenhum problema crítico encontrado.")
    console.log("⚠️  Alguns comportamentos inesperados podem precisar de revisão.")
  } else {
    console.log("🚨 Problemas críticos encontrados que precisam de correção imediata!")
  }

  // Detalhes dos problemas reais
  if (results.PROBLEMA_REAL.length > 0) {
    console.log("\n🚨 PROBLEMAS CRÍTICOS:")
    results.PROBLEMA_REAL.forEach((item) => {
      console.log(`   - ${item.name}: ${item.result.data.erro}`)
    })
  }

  // Detalhes dos comportamentos inesperados
  if (results.COMPORTAMENTO_INESPERADO.length > 0) {
    console.log("\n⚠️  COMPORTAMENTOS INESPERADOS:")
    results.COMPORTAMENTO_INESPERADOS.forEach((item) => {
      console.log(`   - ${item.name}: Status ${item.result.status} (esperado ${item.expectedStatus})`)
    })
  }
}

// Executar análise
smartAnalysis().catch(console.error)
