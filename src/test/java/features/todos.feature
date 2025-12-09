Feature: Testes de Todos - JSONPlaceholder

  Background:
    * url baseUrl

  Scenario: Consultar uma tarefa específica (GET)
    Given path 'todos', 1
    When method get
    Then status 200
    
    # Debug - Imprime o JSON retornado
    * print response
    
    # Validações exatas
    And match response.id == 1
    And match response.title == 'delectus aut autem'
    
    # Validações de tipo (mais robustas)
    And match response.userId == '#number'
    And match response.completed == '#boolean'

  Scenario: Listar todas as tarefas (GET)
    Given path 'todos'
    When method get
    Then status 200
    
    # Verifica que retornou um array
    And match response == '#array'
    
    # Verifica que tem pelo menos 1 item
    And match response == '#[_ > 0]'
    
    # Valida a estrutura do primeiro item
    And match response[0] contains { userId: '#number', id: '#number', title: '#string', completed: '#boolean' }
    
    * print 'Total de tarefas:', response.length

  Scenario: Criar uma nova tarefa (POST)
    Given path 'todos'
    And request 
      """
      {
        "userId": 1,
        "title": "Minha tarefa de teste",
        "completed": false
      }
      """
    When method post
    Then status 201
    
    # Valida que retornou os dados criados
    And match response.title == 'Minha tarefa de teste'
    And match response.userId == 1
    And match response.completed == false
    And match response.id == '#number'
    And match response.id == 201
    
    * print 'Tarefa criada com ID:', response.id

  Scenario: Atualizar uma tarefa completamente (PUT)
    Given path 'todos', 1
    And request 
      """
      {
        "userId": 1,
        "id": 1,
        "title": "Tarefa atualizada",
        "completed": true
      }
      """
    When method put
    Then status 200
    
    And match response.title == 'Tarefa atualizada'
    And match response.completed == true

  Scenario: Atualizar parcialmente uma tarefa (PATCH)
    Given path 'todos', 1
    And request { "completed": true }
    When method patch
    Then status 200
    
    And match response.completed == true
    And match response.id == 1

  Scenario: Deletar uma tarefa (DELETE)
    Given path 'todos', 1
    When method delete
    Then status 200

  Scenario: Filtrar tarefas por usuário (Query Parameters)
    Given path 'todos'
    And param userId = 1
    When method get
    Then status 200
    
    And match response == '#array'
    And match response == '#[_ > 0]'
    
    # Valida que todas as tarefas são do userId 1
    And match each response contains { userId: 1 }
    
    * print 'Tarefas do usuário 1:', response.length

  Scenario: Validar tarefa inexistente (GET 404)
    Given path 'todos', 99999
    When method get
    Then status 404

  Scenario Outline: Consultar múltiplas tarefas usando Data-Driven
    Given path 'todos', <todoId>
    When method get
    Then status 200
    And match response.id == <todoId>
    And match response.userId == '#number'
    
    Examples:
      | todoId |
      | 1      |
      | 5      |
      | 10     |
      | 20     |

  Scenario: Validar schema completo de uma tarefa
    Given path 'todos', 1
    When method get
    Then status 200
    
    # Schema validation completo
    And match response ==
      """
      {
        userId: '#number',
        id: '#number',
        title: '#string',
        completed: '#boolean'
      }
      """
