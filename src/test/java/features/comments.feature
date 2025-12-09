Feature: Testes de Comments - JSONPlaceholder

  Background:
    * url baseUrl

  Scenario: Listar todos os comentários
    Given path 'comments'
    When method get
    Then status 200
    
    And match response == '#array'
    And match response == '#[500]'

  Scenario: Consultar comentário específico
    Given path 'comments', 1
    When method get
    Then status 200
    
    And match response.id == 1
    And match response.postId == 1
    And match response.email == '#string'
    And match response.email == '#regex .+@.+\\..+'

  Scenario: Filtrar comentários por postId
    Given path 'comments'
    And param postId = 1
    When method get
    Then status 200
    
    And match response == '#array'
    And match each response contains { postId: 1 }

  Scenario: Filtrar comentários por email
    Given path 'comments'
    And param email = 'Eliseo@gardner.biz'
    When method get
    Then status 200
    
    And match response == '#array'
    And match response[0].email == 'Eliseo@gardner.biz'
