Feature: Testes de Centros Esportivos - API Reserva

  Background:
    * url baseUrl
    # Login como gerente para operações autenticadas
    * def loginResult = call read('auth-helper.feature') { email: '#(gerenteEmail)', password: '#(gerentePassword)' }
    * def tokenGerente = loginResult.token

  Scenario: Listar todos os centros esportivos
    Given path 'centros-esportivos'
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    
    And match response == '#array'
    * print 'Total de centros esportivos:', response.length

  Scenario: Consultar centro esportivo específico
    # Primeiro lista para pegar um ID válido
    Given path 'centros-esportivos'
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    * def centroId = response[0].id
    
    Given path 'centros', centroId
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    
    And match response.id == centroId
    And match response.nome == '#string'
    And match response.cidade == '#string'
    And match response.UF == '#string'
    And match response contains { espacos: '#array' }

  Scenario: Criar centro esportivo com autenticação
    * def nomeUnico = 'Centro Karate ' + java.util.UUID.randomUUID().toString().substring(0,8)
    Given path 'centros-esportivos'
    And header Authorization = 'Bearer ' + tokenGerente
    And request 
      """
      {
        "nome": "#(nomeUnico)",
        "descricao": "Centro criado pelo teste Karate",
        "latitude": -23.55052,
        "longitude": -46.633308,
        "cidade": "São Paulo",
        "UF": "SP"
      }
      """
    When method post
    Then status 201
    
    And match response.id == '#number'
    And match response.nome == nomeUnico
    And match response.cidade == 'São Paulo'
    
    * print 'Centro criado com ID:', response.id

  Scenario: Criar centro esportivo sem autenticação (deve falhar)
    Given path 'centros-esportivos'
    And request 
      """
      {
        "nome": "Centro Sem Auth",
        "descricao": "Teste sem autenticação",
        "latitude": -23.55052,
        "longitude": -46.633308,
        "cidade": "Rio de Janeiro",
        "UF": "RJ"
      }
      """
    When method post
    Then status 401

  Scenario: Validar schema de centro esportivo
    Given path 'centros-esportivos'
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    
    And match response[0] contains
      """
      {
        id: '#number',
        nome: '#string',
        descricao: '#string',
        cidade: '#string',
        UF: '#string'
      }
      """
