# 🧪 Oficina: Testes de API com Karate Framework
**Hands-On | Aprenda na Prática**

---

## 🎯 O que é Karate?
Framework Open Source para testes de API em **linguagem Gherkin** (BDD).  
📚 [Documentação Oficial](https://github.com/karatelabs/karate) | [Mais detalhes](https://karatelabs.github.io/karate/)

**Por que usar?**
- ✅ Sintaxe simples (sem programação complexa)
- ✅ Relatórios HTML automáticos
- ✅ Validações poderosas em JSON
- ✅ Fácil de aprender e usar

---

## 🚀 PASSO A PASSO - Tutorial Hands-On

### **PASSO 1: Verificar Pré-requisitos**
Abra o terminal e execute:
```bash
java -version    # Deve mostrar Java 11+
mvn -version     # Deve mostrar Maven 3.6+
```



---

### **PASSO 2: Clonar o Projeto**
```bash
git clone https://github.com/llopes05/Testes.git
cd Testes
```

---

### **PASSO 3: Entender a Estrutura**

```
Testes/
├── pom.xml                    # Configuração Maven (dependências)
└── src/test/java/
    ├── karate-config.js       # URL base da API
    └── features/
        ├── todos.feature      # ⭐ Testes de Tarefas
        ├── posts.feature      # Testes de Posts
        └── TestRunner.java    # Executor dos testes
```

**Foco:** Arquivo `.feature` = onde escrevemos os testes!

---

### **PASSO 4: Entender e Praticar!**

**Agora vamos explorar os testes prontos!** 

Abra o arquivo `src/test/java/features/users.feature` e veja os testes:

#### 🎯 **Teste 1: Validar que o usuário 1 se chama "Leanne Graham"**
```gherkin
Scenario: Validar nome do usuário 1
  Given path 'users', 1
  When method get
  Then status 200
  
  # Valida o nome completo
  And match response.name == 'Leanne Graham'
  And match response.username == 'Bret'
  And match response.email == 'Sincere@april.biz'
  
  # Valida estrutura completa
  And match response.address.street == 'Kulas Light'
  And match response.address.city == 'Gwenborough'
  And match response.company.name == 'Romaguera-Crona'
  
  * print response
```

#### ❌ **Teste 2: Validar um nome ERRADO (deve falhar de propósito)**
```gherkin
Scenario: Verificar se o nome NÃO é Jorge Alberto (teste negativo)
  Given path 'users', 1
  When method get
  Then status 200
  
  # Este teste vai FALHAR pois o nome real é "Leanne Graham"
  And match response.name != 'Jorge Alberto'
  
  # Prova que o nome correto é outro
  And match response.name == 'Leanne Graham'
```

#### 📝 **Agora é sua vez!**
Execute os testes e veja os resultados:

```bash
# Executar testes de usuários
mvn test -Dtest=TestRunner#testUsers
```

**O que você vai ver:**
- ✅ Primeiro teste PASSA (nome correto)
- ✅ Segundo teste PASSA (nome é diferente de Jorge Alberto)
- 📊 Dados completos do usuário no console

---

### **PASSO 5: Executar os Testes**

```bash
# Executar todos os testes
mvn test

# Executar apenas produtos
mvn test -Dtest=TestRunner#testProdutos
```

**Resultado esperado:**
```
Tests run: 3, Failures: 0, Errors: 0, Skipped: 0
```

---

### **PASSO 6: Ver o Relatório HTML**

Abra no navegador:
```bash
target/karate-reports/karate-summary.html
```

📊 **Você verá:**
- ✅ Testes passou/falhou
- 🕒 Tempo de execução
- 📝 Request/Response detalhados
- 📸 Screenshots (se configurado)

---

### **PASSO 7: Explore Mais Testes!**

**Teste outros cenários prontos:**

```bash
# Testar Todos (tarefas)
mvn test -Dtest=TestRunner#testTodos

# Testar Posts
mvn test -Dtest=TestRunner#testPosts

# Testar Comments
mvn test -Dtest=TestRunner#testComments
```

**Desafios para praticar:**

1. **Modifique o teste de usuários:**
   - Teste se o usuário 2 se chama "Ervin Howell"
   - Teste se o email contém "@"
   - Teste se o telefone existe

2. **Crie um teste de falha:**
   - Busque o usuário 999 (não existe)
   - Verifique se retorna status 404

3. **Teste a tarefa 1:**
   - Verifique se o título é "delectus aut autem"
   - Verifique se está incompleta (completed = false)

**Exemplo de teste de erro:**
```gherkin
Scenario: Validar usuário inexistente
  Given path 'users', 999
  When method get
  Then status 404
```

---

## 🎓 Principais Validações Karate

```gherkin
# Validar status HTTP
Then status 200

# Validar valor exato
And match response.id == 1

# Validar tipo de dado
And match response.nome == '#string'
And match response.preco == '#number'
And match response.ativo == '#boolean'

# Validar array
And match response == '#array'
And match response == '#[10]'        # Exatamente 10 itens
And match response == '#[_ > 0]'     # Pelo menos 1 item

# Validar objeto completo
And match response == 
  """
  {
    id: '#number',
    nome: '#string',
    preco: '#number'
  }
  """

# Validar cada item do array
And match each response contains { ativo: true }

# Validar com regex
And match response.email == '#regex .+@.+\\..+'
```

---

## 🔧 Comandos Úteis

```bash
# Executar testes
mvn test

# Limpar e executar
mvn clean test

# Executar feature específica
mvn test -Dtest=TestRunner#testProdutos

# Ver logs detalhados
mvn test -X

# Executar em ambiente específico
mvn test -Dkarate.env=dev
```

---

## 💡 Dicas Finais

- 🐛 Use `* print response` para debug
- 📝 Comece com testes simples (GET) e evolua
- 🔄 Reutilize cenários com `Background`
- 📊 Sempre confira o relatório HTML
- 🎯 Pratique criando seus próprios cenários

---

## 📚 Recursos Adicionais

- [Karate Docs](https://github.com/karatelabs/karate)
- [Karate Examples](https://github.com/karatelabs/karate/tree/master/karate-demo)
- [JSONPlaceholder API](https://jsonplaceholder.typicode.com/) (para praticar)

---

**Boa oficina! 🚀**