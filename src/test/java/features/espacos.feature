Feature: Testes de Espaços Esportivos - API Reserva

  Background:
    * url baseUrl
    * def loginResult = call read('auth-helper.feature') { email: '#(gerenteEmail)', password: '#(gerentePassword)' }
    * def tokenGerente = loginResult.token

  Scenario: Listar todos os espaços esportivos
    Given path 'espacos/'
    When method get
    Then status 200
    
    And match response == '#array'
    * print 'Total de espaços esportivos:', response.length

  Scenario: Consultar espaço esportivo específico
    Given path 'espacos/'
    When method get
    Then status 200
    * def espacoId = response[0].id
    
    Given path 'espacos/', espacoId, '/'
    When method get
    Then status 200
    
    And match response.id == espacoId
    And match response.nome == '#string'
    And match response.categoria == '#string'
    And match response.centro_esportivo == '#number'

  Scenario: Criar espaço esportivo com autenticação
    # Primeiro obtém um centro válido
    Given path 'centros-esportivos/'
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    * def centroId = response[0].id
    
    # Cria o espaço
    Given path 'espacos/'
    And header Authorization = 'Bearer ' + tokenGerente
    And request 
      """
      {
        "nome": "Quadra Karate Teste",
        "categoria": "futebol",
        "centro_esportivo": #(centroId)
      }
      """
    When method post
    Then status 201
    
    And match response.id == '#number'
    And match response.nome == 'Quadra Karate Teste'
    And match response.categoria == 'futebol'
    
    * print 'Espaço criado com ID:', response.id

  Scenario: Criar espaço esportivo sem autenticação (deve falhar)
    Given path 'espacos/'
    And request 
      """
      {
        "nome": "Quadra Sem Auth",
        "categoria": "volei",
        "centro_esportivo": 1
      }
      """
    When method post
    Then status 401

  Scenario: Validar categorias de espaço
    Given path 'espacos/'
    When method get
    Then status 200
    
    # Valida que categoria é uma das opções válidas
    * def categorias = ['futebol', 'volei', 'basquete', 'tenis', 'futsal', 'atletismo', 'outros', 'natação', 'ginástica']
    And match each response[*].categoria == '#? categorias.contains(_)'
