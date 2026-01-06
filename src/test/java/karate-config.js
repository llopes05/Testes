function fn() {
  var env = karate.env;
  karate.log('karate.env system property was:', env);
  
  if (!env) {
    env = 'dev';
  }
  
  var config = {
    baseUrl: 'http://localhost:8000/api',
    apiTimeout: 10000,
    // Credenciais de teste
    gerenteEmail: 'gerente1@email.com',
    gerentePassword: 'senha123',
    organizadorEmail: 'org1@email.com',
    organizadorPassword: 'senha123'
  };
  
  // Configurações específicas por ambiente
  if (env == 'dev') {
    config.baseUrl = 'http://localhost:8000/api';
  } else if (env == 'qa') {
    config.baseUrl = 'http://qa-api.reserva.com/api';
  } else if (env == 'prod') {
    config.baseUrl = 'https://api.reserva.com/api';
  }
  
  karate.configure('connectTimeout', config.apiTimeout);
  karate.configure('readTimeout', config.apiTimeout);
  
  // Função helper para login e obter token JWT
  config.getToken = function(email, password) {
    var result = karate.call('classpath:features/auth-helper.feature', { email: email, password: password });
    return result.token;
  };
  
  return config;
}
