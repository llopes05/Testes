@ignore
Feature: Helper para autenticação JWT

  Scenario: Obter token de acesso
    Given url baseUrl + '/login/'
    And request { email: '#(email)', password: '#(password)' }
    When method post
    Then status 200
    * def token = response.access
