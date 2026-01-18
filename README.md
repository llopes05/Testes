# 🏟️ Sistema de Reservas de Espaços Esportivos - Testes de API

**Testes automatizados com Karate Framework para API REST Django**

---

## 📋 Sobre o Projeto

Este projeto contém testes de API automatizados para um **Sistema de Reservas de Espaços Esportivos**, desenvolvido com:

- **Backend:** Django REST Framework com autenticação JWT (SimpleJWT)
- **Testes:** Karate Framework 1.4.1 com JUnit 5
- **Build:** Maven 3.6+

---

## 🎯 O que é testado?

| Feature | Descrição | Cenários |
|---------|-----------|----------|
| `usuarios.feature` | Cadastro e autenticação de usuários | Registro, login, validação de credenciais |
| `centros.feature` | CRUD de centros esportivos | Listar, criar, validar estrutura |
| `espacos.feature` | CRUD de espaços esportivos | Listar, criar por centro, validar categorias |
| `agendas.feature` | CRUD de agendas/horários | Listar, criar, validar disponibilidade |
| `reservas.feature` | CRUD de reservas | Listar, criar, cancelar reservas |

---

## 🚀 Pré-requisitos

```bash
java -version    # Java 11+
mvn -version     # Maven 3.6+
python --version # Python 3.10+ (para o backend)
```

---

## 📁 Estrutura do Projeto

```
Testes/
├── pom.xml                          # Configuração Maven
├── backend/                         # API Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── popular_banco.py             # Script para popular o banco
│   └── reservaapp/                  # App principal
└── src/test/java/
    ├── karate-config.js             # Configuração (URL, credenciais)
    └── features/
        ├── auth-helper.feature      # Helper de autenticação
        ├── usuarios.feature         # Testes de usuários
        ├── centros.feature          # Testes de centros esportivos
        ├── espacos.feature          # Testes de espaços
        ├── agendas.feature          # Testes de agendas
        ├── reservas.feature         # Testes de reservas
        └── TestRunner.java          # Executor JUnit
```

---

## ⚙️ Configuração

### 1. Iniciar o Backend

```bash
cd backend
pip install -r requirements.txt
python popular_banco.py    # Popular banco com dados de teste
python manage.py runserver
```

### 2. Configurar Credenciais

Edite `src/test/java/karate-config.js`:

```javascript
config.baseUrl = 'http://localhost:8000/api';
config.gerenteEmail = 'gerente@teste.com';
config.gerentePassword = '12345678';
config.organizadorEmail = 'organizador@teste.com';
config.organizadorPassword = '12345678';
```

---

## ▶️ Executar os Testes

```bash
# Executar todos os testes (62 cenários)
mvn test

# Executar testes específicos
mvn test -Dtest=TestRunner#testUsuarios
mvn test -Dtest=TestRunner#testCentros
mvn test -Dtest=TestRunner#testEspacos
mvn test -Dtest=TestRunner#testAgendas
mvn test -Dtest=TestRunner#testReservas

# Limpar e executar
mvn clean test
```

**Resultado esperado:**
```
Tests run: 62, Failures: 0, Errors: 0, Skipped: 0
```

---

## 📊 Relatórios

Após executar os testes, abra no navegador:

```
target/karate-reports/karate-summary.html
```

📈 **O relatório mostra:**
- ✅ Status de cada cenário (passou/falhou)
- 🕒 Tempo de execução
- 📝 Request/Response detalhados
- 🔍 Erros e stack traces

---

## 🧪 Exemplos de Testes

### Autenticação (Login)
```gherkin
Scenario: Login como gerente
  Given url baseUrl + '/login'
  And request { email: '#(gerenteEmail)', password: '#(gerentePassword)' }
  When method post
  Then status 200
  And match response.access == '#string'
```

### Criar Centro Esportivo
```gherkin
Scenario: Criar centro esportivo com autenticação
  Given path 'centros-esportivos'
  And header Authorization = 'Bearer ' + tokenGerente
  And request 
    """
    {
      "nome": "Centro Esportivo Novo",
      "cidade": "São Paulo",
      "UF": "SP"
    }
    """
  When method post
  Then status 201
  And match response.id == '#number'
```

### Listar Espaços
```gherkin
Scenario: Listar espaços esportivos
  Given path 'espacos'
  And header Authorization = 'Bearer ' + tokenGerente
  When method get
  Then status 200
  And match response == '#array'
  And match each response contains { id: '#number', nome: '#string' }
```

---

## 🎓 Principais Validações Karate

```gherkin
# Status HTTP
Then status 200
Then status 201
Then status 401

# Valor exato
And match response.nome == 'Centro Esportivo'

# Tipo de dado
And match response.id == '#number'
And match response.nome == '#string'
And match response.ativo == '#boolean'

# Arrays
And match response == '#array'
And match response == '#[5]'           # Exatamente 5 itens

# Objeto parcial
And match response contains { id: '#number' }

# Cada item do array
And match each response contains { id: '#number', nome: '#string' }

# Regex
And match response.email == '#regex .+@.+\\..+'

# Presente/ausente
And match response.token == '#present'
And match response.error == '#notpresent'
```

---

## 🔧 Endpoints da API

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/login` | Login (retorna JWT) | ❌ |
| POST | `/api/register` | Registrar usuário | ❌ |
| GET | `/api/centros-esportivos` | Listar centros | ✅ |
| POST | `/api/centros-esportivos` | Criar centro | ✅ |
| GET | `/api/espacos` | Listar espaços | ✅ |
| POST | `/api/espacos` | Criar espaço | ✅ |
| GET | `/api/agendas` | Listar agendas | ✅ |
| POST | `/api/agendas` | Criar agenda | ✅ |
| GET | `/api/reservas` | Listar reservas | ✅ |
| POST | `/api/reservas` | Criar reserva | ✅ |

---

## 💡 Dicas

- 🐛 Use `* print response` para debug
- 🔄 O `Background` executa antes de cada cenário
- 📝 Use `auth-helper.feature` para reutilizar autenticação
- 🎯 Nomes de recursos são gerados com UUID para evitar duplicatas
- 📊 Sempre confira o relatório HTML após os testes

---

## 📚 Recursos

- [Karate Framework](https://github.com/karatelabs/karate)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)

---

**🚀 Bons testes!**