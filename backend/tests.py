from django.test import TestCase
from rest_framework.test import APIClient
import json
from django.contrib.auth import get_user_model
from reservaapp.models import CentroEsportivo, EspacoEsportivo

class CentroEsportivoTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.gerente = User.objects.create_user(
            username="gerente1",
            email="gerente1@email.com",
            password="senha123",
            tipo="gerente",
            nome_completo="Gerente Um",
            cpf="123.456.789-00"
        )
        self.client = APIClient()
        response = self.client.post('/api/login/', {
            'email': 'gerente1@email.com',
            'password': 'senha123'
        }, format='json')
        print("Login response:", response.status_code, response.data)
        self.login = response.data.get('access')

    def test_criar_centro_esportivo_com_sucesso(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.login)
        dados = {
            "nome": "Centro Esportivo 1",
            "descricao": "Quadras e campos para esportes",
            "latitude": -23.55052,
            "longitude": -46.633308,
            "cidade": "São Paulo",
            "UF": "SP",
            "gerente": self.gerente.id
        }
        response = self.client.post(
            "/api/centros-esportivos/",
            data=json.dumps(dados),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)

    def test_criar_centro_esportivo_sem_autenticacao(self):
        dados = {
            "nome": "Centro Esportivo 2",
            "descricao": "Outro centro esportivo",
            "latitude": -23.55052,
            "longitude": -46.633308,
            "cidade": "São Paulo",
            "UF": "SP",
            "gerente": self.gerente.id
        }
        response = self.client.post(
            "/api/centros-esportivos/",
            data=json.dumps(dados),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

class CheckEmailTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="teste",
            email="teste@email.com",
            password="senha123",
            tipo="organizador",
            nome_completo="Teste",
            cpf="123.456.789-00"
        )
        self.client = APIClient()

    def test_email_existe(self):
        response = self.client.post('/api/check-email/', {'email': 'teste@email.com'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['exists'], True)

    def test_email_nao_existe(self):
        response = self.client.post('/api/check-email/', {'email': 'naoexiste@email.com'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['exists'], False)

    def test_email_nao_informado(self):
        response = self.client.post('/api/check-email/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

class EspacoEsportivoTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.gerente = User.objects.create_user(
            username="gerente1",
            email="gerente1@email.com",
            password="senha123",
            tipo="gerente",
            nome_completo="Gerente Um",
            cpf="123.456.789-00"
        )
        self.client = APIClient()
        response = self.client.post('/api/login/', {
            'email': 'gerente1@email.com',
            'password': 'senha123'
        }, format='json')
        self.login = response.data.get('access')

        self.centro = CentroEsportivo.objects.create(
            nome="Centro Esportivo 1",
            descricao="Quadras e campos para esportes",
            latitude=-23.55052,
            longitude=-46.633308,
            cidade="São Paulo",
            UF="SP",
            gerente=self.gerente
        )

    def test_criar_espaco_esportivo_com_sucesso(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.login)
        dados = {
            "nome": "Quadra de Futebol",
            "foto_perfil": "http://example.com/foto.jpg",
            "categoria": "Futebol",
            "centro_esportivo": self.centro.id
        }
        response = self.client.post(
            "/api/espacos/",
            data=json.dumps(dados),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)

    def test_criar_espaco_esportivo_sem_autenticacao(self):
        dados = {
            "nome": "Quadra de Basquete",
            "foto_perfil": "http://example.com/foto.jpg",
            "categoria": "Basquete",
            "centro_esportivo": self.centro.id
        }
        response = self.client.post(
            "/api/espacos/",
            data=json.dumps(dados),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_criar_agenda_com_sucesso(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.login)
        response_espaco = self.client.post(
            "/api/espacos/",
            data=json.dumps({
                "nome": "Quadra de Futebol",
                "foto_perfil": "http://example.com/foto.jpg",
                "categoria": "Futebol",
                "centro_esportivo": self.centro.id
            }),
            content_type="application/json"
        )
        espaco_id = response_espaco.data["id"]

        dados = {
            "preco": 50.00,
            "dia": "2023-10-01",
            "h_inicial": "10:00:00",
            "h_final": "12:00:00",
            "espacoesportivo": espaco_id,
            "status": "ativo"
        }
        response = self.client.post(
            "/api/agendas/",
            data=json.dumps(dados),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)

    def test_nao_permite_agenda_horario_repetido(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.login)
        response_espaco = self.client.post(
            "/api/espacos/",
            data=json.dumps({
                "nome": "Quadra de Futebol",
                "foto_perfil": "http://example.com/foto.jpg",
                "categoria": "Futebol",
                "centro_esportivo": self.centro.id
            }),
            content_type="application/json"
        )
        espaco_id = response_espaco.data["id"]

        dados_agenda = {
            "preco": 50.00,
            "dia": "2023-10-01",
            "h_inicial": "10:00:00",
            "h_final": "12:00:00",
            "espacoesportivo": espaco_id,
            "status": "ativo"
        }
        response1 = self.client.post(
            "/api/agendas/",
            data=json.dumps(dados_agenda),
            content_type="application/json"
        )
        self.assertEqual(response1.status_code, 201)

        response2 = self.client.post(
            "/api/agendas/",
            data=json.dumps(dados_agenda),
            content_type="application/json"
        )
        self.assertIn(response2.status_code, [400, 409])

class ReservaTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.gerente = User.objects.create_user(
            username="gerente1",
            email="gerente1@email.com",
            password="senha123",
            tipo="gerente",
            nome_completo="Gerente Um",
            cpf="123.456.789-00"
        )
        self.organizador = User.objects.create_user(
            username="org1",
            email="org1@email.com",
            password="senha123",
            tipo="organizador",
            nome_completo="Organizador Um",
            cpf="987.654.321-00"
        )
        self.client = APIClient()
        response = self.client.post('/api/login/', {
            'email': 'org1@email.com',
            'password': 'senha123'
        }, format='json')
        self.login_organizador = response.data.get('access')
        response_gerente = self.client.post('/api/login/', {
            'email': 'gerente1@email.com',
            'password': 'senha123'
        }, format='json')
        self.login_gerente = response_gerente.data.get('access')

        self.centro = CentroEsportivo.objects.create(
            nome="Centro Esportivo 1",
            descricao="Quadras e campos para esportes",
            latitude=-23.55052,
            longitude=-46.633308,
            cidade="São Paulo",
            UF="SP",
            gerente=self.gerente
        )

    def criar_espaco_e_agenda(self, status_agenda="ativo"):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.login_gerente)
        response_espaco = self.client.post(
            "/api/espacos/",
            data=json.dumps({
                "nome": "Quadra de Teste",
                "foto_perfil": "http://example.com/foto.jpg",
                "categoria": "Futebol",
                "centro_esportivo": self.centro.id
            }),
            content_type="application/json"
        )
        espaco_id = response_espaco.data["id"]
        response_agenda = self.client.post(
            "/api/agendas/",
            data=json.dumps({
                "preco": 100.00,
                "dia": "2023-10-10",
                "h_inicial": "15:00:00",
                "h_final": "17:00:00",
                "espacoesportivo": espaco_id,
                "status": status_agenda
            }),
            content_type="application/json"
        )
        return response_agenda.data["id"]

    def test_nao_permite_reserva_em_agenda_reservada(self):
        agenda_id = self.criar_espaco_e_agenda()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.login_organizador)
        response1 = self.client.post(
            "/api/reservas/",
            data=json.dumps({"agenda": agenda_id}),
            content_type="application/json"
        )
        self.assertEqual(response1.status_code, 201)
        response2 = self.client.post(
            "/api/reservas/",
            data=json.dumps({"agenda": agenda_id}),
            content_type="application/json"
        )
        self.assertEqual(response2.status_code, 400)
        self.assertIn("já foi reservado", str(response2.data))

    def test_nao_permite_reserva_em_agenda_indisponivel(self):
        agenda_id = self.criar_espaco_e_agenda(status_agenda="indisponível")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.login_organizador)
        response = self.client.post(
            "/api/reservas/",
            data=json.dumps({"agenda": agenda_id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("não está disponível", str(response.data))