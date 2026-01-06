from django.test import TestCase
from rest_framework.test import APIClient
import json
from django.contrib.auth import get_user_model
from reservaapp.models import CentroEsportivo, EspacoEsportivo



class TesteModelos(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.centro = CentroEsportivo.objects.create(
            nome='Centro Esportivo Teste',
            endereco='Rua Teste, 123',
            telefone='(11) 1234-5678'
        )
        self.espaco = EspacoEsportivo.objects.create(
            nome='Quadra de Futebol',
            tipo='Futebol',
            capacidade=22,
            centro_esportivo=self.centro
        )

    def test_criacao_centro_esportivo(self):
        centro = CentroEsportivo.objects.get(nome='Centro Esportivo Teste')
        self.assertEqual(centro.endereco, 'Rua Teste, 123')
        self.assertEqual(centro.telefone, '(11) 1234-5678')

    def test_criacao_espaco_esportivo(self):
        espaco = EspacoEsportivo.objects.get(nome='Quadra de Futebol')
        self.assertEqual(espaco.tipo, 'Futebol')
        self.assertEqual(espaco.capacidade, 22)
        self.assertEqual(espaco.centro_esportivo.nome, 'Centro Esportivo Teste')