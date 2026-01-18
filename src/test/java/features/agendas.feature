Feature: Testes de Agendas - API Reserva

  Background:
    * url baseUrl
    * def loginResult = call read('auth-helper.feature') { email: '#(gerenteEmail)', password: '#(gerentePassword)' }
    * def tokenGerente = loginResult.token

  Scenario: Listar todas as agendas
    Given path 'agendas'
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    
    And match response == '#array'
    * print 'Total de agendas:', response.length

  Scenario: Consultar agenda específica
    Given path 'agendas'
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    * def agendaId = response[0].id
    
    Given path 'agendas', agendaId
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    
    And match response.id == agendaId
    And match response.preco == '#string'
    And match response.dia == '#string'
    And match response.h_inicial == '#string'
    And match response.h_final == '#string'
    And match response.status == '#string'

  Scenario: Criar agenda com autenticação
    # Primeiro obtém um espaço válido
    Given path 'espacos'
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    * def espacoId = response[0].id
    * def randomDay = '' + (Math.floor(Math.random() * 28) + 1)
    * def diaFormatado = randomDay.length == 1 ? '0' + randomDay : randomDay
    * def diaUnico = '2027-03-' + diaFormatado
    
    # Cria a agenda
    Given path 'agendas'
    And header Authorization = 'Bearer ' + tokenGerente
    And request 
      """
      {
        "preco": 75.00,
        "dia": "#(diaUnico)",
        "h_inicial": "14:00:00",
        "h_final": "16:00:00",
        "espacoesportivo": #(espacoId),
        "status": "ativo"
      }
      """
    When method post
    Then status 201
    
    And match response.id == '#number'
    And match response.dia == diaUnico
    And match response.status == 'ativo'
    
    * print 'Agenda criada com ID:', response.id

  Scenario: Criar agenda sem autenticação (deve falhar)
    Given path 'agendas'
    And request 
      """
      {
        "preco": 50.00,
        "dia": "2026-02-20",
        "h_inicial": "10:00:00",
        "h_final": "12:00:00",
        "espacoesportivo": 1,
        "status": "ativo"
      }
      """
    When method post
    Then status 401

  Scenario: Validar schema de agenda
    Given path 'agendas'
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    
    And match response[0] contains
      """
      {
        id: '#number',
        preco: '#string',
        dia: '#regex \\d{4}-\\d{2}-\\d{2}',
        h_inicial: '#string',
        h_final: '#string',
        status: '#string'
      }
      """

  Scenario: Validar status de agenda
    Given path 'agendas'
    And header Authorization = 'Bearer ' + tokenGerente
    When method get
    Then status 200
    
    # Valida que todos os status são strings
    And match each response[*].status == '#string'
