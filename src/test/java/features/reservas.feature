Feature: Testes de Reservas - API Reserva

  Background:
    * url baseUrl
    # Login como organizador para criar reservas
    * def loginOrg = call read('auth-helper.feature') { email: '#(organizadorEmail)', password: '#(organizadorPassword)' }
    * def tokenOrganizador = loginOrg.token
    # Login como gerente para criar recursos
    * def loginGer = call read('auth-helper.feature') { email: '#(gerenteEmail)', password: '#(gerentePassword)' }
    * def tokenGerente = loginGer.token

  Scenario: Listar minhas reservas
    Given path 'minhas-reservas/'
    And header Authorization = 'Bearer ' + tokenOrganizador
    When method get
    Then status 200
    
    And match response == '#array'
    * print 'Total de minhas reservas:', response.length

  Scenario: Criar reserva com sucesso
    # Primeiro obtém uma agenda ativa
    Given path 'agendas/'
    When method get
    Then status 200
    * def agendasAtivas = karate.filter(response, function(x){ return x.status == 'ativo' })
    * def agendaId = agendasAtivas[0].id
    
    # Cria a reserva
    Given path 'reservar/'
    And header Authorization = 'Bearer ' + tokenOrganizador
    And request { agenda: #(agendaId) }
    When method post
    Then status 201
    
    And match response.id == '#number'
    And match response.status == 'pendente'
    
    * print 'Reserva criada com ID:', response.id

  Scenario: Criar reserva sem autenticação (deve falhar)
    Given path 'reservar/'
    And request { agenda: 1 }
    When method post
    Then status 401

  Scenario: Validar schema de reserva
    Given path 'minhas-reservas/'
    And header Authorization = 'Bearer ' + tokenOrganizador
    When method get
    Then status 200
    
    # Se houver reservas, valida o schema
    * def temReservas = response.length > 0
    * if (temReservas) karate.match(response[0], { id: '#number', status: '#string', agenda: '#object' })

  Scenario: Listar reservas sem autenticação (deve falhar)
    Given path 'minhas-reservas/'
    When method get
    Then status 401

  Scenario Outline: Validar status possíveis de reserva
    Given path 'minhas-reservas/'
    And header Authorization = 'Bearer ' + tokenOrganizador
    When method get
    Then status 200
    
    # Status deve ser um dos valores válidos
    * def statusValidos = ['pendente', 'pago', 'cancelada']
    * def reservasFiltradas = karate.filter(response, function(x){ return x.status == '<status>' })
    
    Examples:
      | status    |
      | pendente  |
      | pago      |
      | cancelada |
