Feature: Testes de Usuários - API Reserva

  Background:
    * url baseUrl

  Scenario: Cadastrar novo usuário organizador
    Given path 'register/'
    And request 
      """
      {
        "username": "testekarate",
        "email": "testekarate@email.com",
        "password": "senha123",
        "tipo": "organizador",
        "nome_completo": "Teste Karate",
        "cpf": "111.222.333-44"
      }
      """
    When method post
    Then status 201
    
    And match response.email == 'testekarate@email.com'
    And match response.tipo == 'organizador'
    And match response.nome_completo == 'Teste Karate'

  Scenario: Login com credenciais válidas
    Given path 'login/'
    And request { email: '#(organizadorEmail)', password: '#(organizadorPassword)' }
    When method post
    Then status 200
    
    And match response.access == '#string'
    And match response.refresh == '#string'
    
    * print 'Token de acesso obtido:', response.access

  Scenario: Login com credenciais inválidas
    Given path 'login/'
    And request { email: 'invalido@email.com', password: 'senhaerrada' }
    When method post
    Then status 401

  Scenario: Verificar email existente
    Given path 'check-email/'
    And request { email: '#(organizadorEmail)' }
    When method post
    Then status 200
    
    And match response.exists == true

  Scenario: Verificar email não existente
    Given path 'check-email/'
    And request { email: 'naoexiste999@email.com' }
    When method post
    Then status 200
    
    And match response.exists == false

  Scenario: Acessar dados do usuário logado
    # Primeiro faz login
    Given path 'login/'
    And request { email: '#(organizadorEmail)', password: '#(organizadorPassword)' }
    When method post
    Then status 200
    * def token = response.access
    
    # Depois acessa /me/
    Given path 'me/'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200
    
    And match response.email == organizadorEmail
    And match response.tipo == '#string'
    And match response.nome_completo == '#string'

  Scenario: Acessar /me/ sem autenticação
    Given path 'me/'
    When method get
    Then status 401
