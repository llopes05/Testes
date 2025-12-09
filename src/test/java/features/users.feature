Feature: Testes de Users - JSONPlaceholder

  Background:
    * url baseUrl

  Scenario: Listar todos os usuários
    Given path 'users'
    When method get
    Then status 200
    
    And match response == '#array'
    And match response == '#[10]'

  Scenario: Consultar usuário específico com validação detalhada
    Given path 'users', 1
    When method get
    Then status 200
    
    # Validações básicas
    And match response.id == 1
    And match response.name == 'Leanne Graham'
    And match response.username == 'Bret'
    And match response.email == 'Sincere@april.biz'
    
    # Validação de objetos aninhados
    And match response.address.street == 'Kulas Light'
    And match response.address.suite == 'Apt. 556'
    And match response.address.city == 'Gwenborough'
    And match response.address.zipcode == '92998-3874'
    And match response.address.geo.lat == '-37.3159'
    And match response.address.geo.lng == '81.1496'
    
    # Validação de contato
    And match response.phone == '1-770-736-8031 x56442'
    And match response.website == 'hildegard.org'
    
    # Validação de company
    And match response.company.name == 'Romaguera-Crona'
    And match response.company.catchPhrase == 'Multi-layered client-server neural-net'
    And match response.company.bs == 'harness real-time e-markets'
    
    * print 'Usuário completo:', response

  Scenario: Validar que o usuário 1 NÃO se chama Jorge Alberto (teste negativo)
    Given path 'users', 1
    When method get
    Then status 200
    
    # Teste negativo - verifica que o nome NÃO é Jorge Alberto
    And match response.name != 'Jorge Alberto'
    
    # Confirma o nome verdadeiro
    And match response.name == 'Leanne Graham'
    
    * print 'Nome real:', response.name
    * print 'Teste negativo passou! O nome NÃO é Jorge Alberto ✓'

  Scenario: Validar schema completo de usuário
    Given path 'users', 1
    When method get
    Then status 200
    
    And match response ==
      """
      {
        id: '#number',
        name: '#string',
        username: '#string',
        email: '#regex .+@.+\\..+',
        address: {
          street: '#string',
          suite: '#string',
          city: '#string',
          zipcode: '#string',
          geo: {
            lat: '#string',
            lng: '#string'
          }
        },
        phone: '#string',
        website: '#string',
        company: {
          name: '#string',
          catchPhrase: '#string',
          bs: '#string'
        }
      }
      """

  Scenario: Criar novo usuário
    Given path 'users'
    And request 
      """
      {
        "name": "João Silva",
        "username": "jsilva",
        "email": "joao@example.com",
        "address": {
          "street": "Rua Teste",
          "city": "São Paulo"
        }
      }
      """
    When method post
    Then status 201
    
    And match response.name == 'João Silva'
    And match response.id == '#number'
