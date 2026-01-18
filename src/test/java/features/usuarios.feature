Feature: Testes de Usuários - API Reserva

  Background:
    * url baseUrl

  Scenario: Cadastrar novo usuário organizador
    * def sufixo = java.util.UUID.randomUUID().toString().substring(0,8)
    * def emailUnico = 'teste' + sufixo + '@email.com'
    * def usernameUnico = 'user' + sufixo
    * def cpfUnico = '' + Math.floor(Math.random() * 99999999999)
    Given path 'register'
    And request 
      """
      {
        "username": "#(usernameUnico)",
        "email": "#(emailUnico)",
        "password": "senha123",
        "tipo": "organizador",
        "nome_completo": "Teste Karate",
        "cpf": "#(cpfUnico)"
      }
      """
    When method post
    Then status 201
    
    And match response.email == emailUnico
    And match response.tipo == 'organizador'
    And match response.nome_completo == 'Teste Karate'

  Scenario: Login com credenciais válidas
    Given path 'login'
    And request { email: '#(organizadorEmail)', password: '#(organizadorPassword)' }
    When method post
    Then status 200
    
    And match response.access == '#string'
    And match response.refresh == '#string'
    
    * print 'Token de acesso obtido:', response.access

  Scenario: Login com credenciais inválidas
    Given path 'login'
    And request { email: 'invalido@email.com', password: 'senhaerrada' }
    When method post
    Then status 401

  Scenario: Verificar email existente
    Given path 'check-email'
    And request { email: '#(organizadorEmail)' }
    When method post
    Then status 200
    
    And match response.exists == true

  Scenario: Verificar email não existente
    Given path 'check-email'
    And request { email: 'naoexiste999@email.com' }
    When method post
    Then status 200
    
    And match response.exists == false

  Scenario: Acessar dados do usuário logado
    # Primeiro faz login
    Given path 'login'
    And request { email: '#(organizadorEmail)', password: '#(organizadorPassword)' }
    When method post
    Then status 200
    * def token = response.access
    
    # Depois acessa /me
    Given path 'me'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200
    
    And match response.email == organizadorEmail
    And match response.tipo == '#string'
    And match response.nome_completo == '#string'

  Scenario: Acessar /me sem autenticação
    Given path 'me'
    When method get
    Then status 401
