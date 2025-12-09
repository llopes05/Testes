Feature: Testes de Posts - JSONPlaceholder

  Background:
    * url baseUrl

  Scenario: Listar todos os posts
    Given path 'posts'
    When method get
    Then status 200
    
    And match response == '#array'
    And match response == '#[100]'
    
    # Valida estrutura do primeiro post
    And match response[0] == 
      """
      {
        userId: '#number',
        id: '#number',
        title: '#string',
        body: '#string'
      }
      """

  Scenario: Consultar um post específico
    Given path 'posts', 1
    When method get
    Then status 200
    
    And match response.id == 1
    And match response.userId == 1
    And match response.title == '#string'
    And match response.body == '#string'

  Scenario: Criar um novo post
    Given path 'posts'
    And request 
      """
      {
        "title": "Meu Post de Teste",
        "body": "Este é o conteúdo do meu post de teste",
        "userId": 1
      }
      """
    When method post
    Then status 201
    
    And match response.id == 101
    And match response.title == 'Meu Post de Teste'
    And match response.body == 'Este é o conteúdo do meu post de teste'
    And match response.userId == 1

  Scenario: Buscar posts de um usuário específico
    Given path 'posts'
    And param userId = 1
    When method get
    Then status 200
    
    And match response == '#array'
    And match each response contains { userId: 1 }

  Scenario: Buscar comentários de um post
    Given path 'posts', 1, 'comments'
    When method get
    Then status 200
    
    And match response == '#array'
    And match response == '#[_ > 0]'
    
    # Valida estrutura dos comentários
    And match response[0] contains 
      """
      {
        postId: 1,
        id: '#number',
        name: '#string',
        email: '#string',
        body: '#string'
      }
      """
