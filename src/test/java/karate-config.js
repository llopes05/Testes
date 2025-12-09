function fn() {
  var env = karate.env; // get system property 'karate.env'
  karate.log('karate.env system property was:', env);
  
  if (!env) {
    env = 'dev';
  }
  
  var config = {
    baseUrl: 'https://jsonplaceholder.typicode.com',
    apiTimeout: 10000
  };
  
  // Configurações específicas por ambiente
  if (env == 'dev') {
    // config.baseUrl = 'https://jsonplaceholder.typicode.com';
  } else if (env == 'qa') {
    // config.baseUrl = 'https://qa-api.example.com';
  } else if (env == 'prod') {
    // config.baseUrl = 'https://api.example.com';
  }
  
  karate.configure('connectTimeout', config.apiTimeout);
  karate.configure('readTimeout', config.apiTimeout);
  
  return config;
}
