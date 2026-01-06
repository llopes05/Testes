from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework.test import APIRequestFactory
from ..serializers import CustomUserSerializer

CustomUser = get_user_model() # é melhor usar isso do que importar diretamente o modelo


class CustomUserModelTest(TestCase):
   

    def setUp(self):
        # configura dados de teste
        self.user_data = {
            'username': 'usuario_teste',
            'email': 'usuario@teste.com',
            'tipo': 'gerente',
            'nome_completo': 'Usuário de Teste',
            'cpf': '12345678901',
            'password': 'senha123'
        }

    def test_criar_usuario_valido(self):
        # verifica se a criação de um usuário válido é bem-sucedida
        user = CustomUser.objects.create_user(**self.user_data)

        self.assertEqual(user.username, 'usuario_teste')
        self.assertEqual(user.email, 'usuario@teste.com')
        self.assertEqual(user.tipo, 'gerente')
        self.assertEqual(user.nome_completo, 'Usuário de Teste')
        self.assertEqual(user.cpf, '12345678901')
        self.assertTrue(user.check_password('senha123'))

    def test_email_e_username_field(self):
        # verifica se o campo de autenticação principal é o email
        self.assertEqual(CustomUser.USERNAME_FIELD, 'email')

    def test_email_unico(self):
        # verifica se não é possível criar dois usuários com o mesmo email
        CustomUser.objects.create_user(**self.user_data)

        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='outro_usuario',
                email='usuario@teste.com',
                tipo='organizador',
                nome_completo='Outro Usuário',
                cpf='98765432100',
                password='senha456'
            )

    def test_cpf_unico(self):
        # verifica se não é possível criar dois usuários com o mesmo cpf
        CustomUser.objects.create_user(**self.user_data)

        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='outro_usuario',
                email='outro@teste.com',
                tipo='organizador',
                nome_completo='Outro Usuário',
                cpf='12345678901',
                password='senha456'
            )

    def test_tipo_usuario_gerente(self):
        # verifica se é possível criar um usuário do tipo gerente
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.tipo, 'gerente')

    def test_tipo_usuario_organizador(self):
        # verifica se é possível criar um usuário do tipo organizador
        self.user_data['tipo'] = 'organizador'
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.tipo, 'organizador')

    def test_str_retorna_email(self):
        # verifica se o método __str__ retorna o email do usuário
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'usuario@teste.com')

    def test_senha_criptografada(self):
        # verifica se a senha é armazenada de forma criptografada
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertNotEqual(user.password, 'senha123')
        self.assertTrue(user.check_password('senha123'))


class CustomUserSerializerTest(TestCase):
    """testes para o serializer CustomUserSerializer"""

    def setUp(self):
        """configura dados de teste"""
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')

        self.user_data = {
            'username': 'usuario_teste',
            'email': 'usuario@teste.com',
            'tipo': 'gerente',
            'nome_completo': 'Usuário de Teste',
            'cpf': '12345678901',
            'password': 'senha123'
        }

    def test_serializer_contem_campos_esperados_na_leitura(self):
        """verifica se o serializer contém os campos esperados na leitura"""
        user = CustomUser.objects.create_user(**self.user_data)
        serializer = CustomUserSerializer(user, context={'request': self.request})

        self.assertIn('id', serializer.data)
        self.assertIn('username', serializer.data)
        self.assertIn('email', serializer.data)
        self.assertIn('tipo', serializer.data)
        self.assertIn('nome_completo', serializer.data)
        self.assertIn('cpf', serializer.data)
        self.assertNotIn('password', serializer.data)

    def test_serializer_cria_usuario_com_dados_validos(self):
        """verifica se o serializer cria um usuário com dados válidos"""
        serializer = CustomUserSerializer(data=self.user_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertEqual(user.username, 'usuario_teste')
        self.assertEqual(user.email, 'usuario@teste.com')
        self.assertEqual(user.tipo, 'gerente')
        self.assertEqual(user.nome_completo, 'Usuário de Teste')
        self.assertEqual(user.cpf, '12345678901')
        self.assertTrue(user.check_password('senha123'))

    def test_serializer_valida_campos_obrigatorios(self):
        """verifica se o serializer valida campos obrigatórios"""
        invalid_data = {}

        serializer = CustomUserSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('email', serializer.errors)
        self.assertIn('tipo', serializer.errors)
        self.assertIn('nome_completo', serializer.errors)
        self.assertIn('cpf', serializer.errors)
        self.assertIn('password', serializer.errors)

    def test_serializer_valida_tamanho_cpf(self):
        """verifica se o serializer valida o tamanho do cpf (11 dígitos)"""
        invalid_data = self.user_data.copy()
        invalid_data['cpf'] = '123'

        serializer = CustomUserSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('cpf', serializer.errors)

    def test_serializer_password_write_only(self):
        """verifica se o campo password é write_only"""
        user = CustomUser.objects.create_user(**self.user_data)
        serializer = CustomUserSerializer(user)

        self.assertNotIn('password', serializer.data)
