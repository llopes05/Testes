from django.test import TestCase, RequestFactory
from ..models import CustomUser, CentroEsportivo, EspacoEsportivo
from ..serializers import Centro_com_espacosSerializer

class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gerente = CustomUser.objects.create_user(
            email="gerente.teste@email.com",
            username="gerente.teste",
            tipo="gerente",
            nome_completo="Gerente de Testes",
            cpf="11122233344"
        )
        cls.centro = CentroEsportivo.objects.create(
            nome="Centro Teste Principal",
            descricao="Descrição do centro",
            latitude=-23.5505,
            longitude=-46.6333,
            cidade="São Paulo",
            UF="SP",
            gerente=cls.gerente
        )

class CentroComEspacosSerializerTest(BaseTestCase):

    def setUp(self):
        self.espaco1 = EspacoEsportivo.objects.create(
            nome='Quadra de Tênis A',
            categoria='tenis',
            centro_esportivo=self.centro
        )
        self.espaco2 = EspacoEsportivo.objects.create(
            nome='Campo Society Principal',
            categoria='futebol',
            centro_esportivo=self.centro
        )
        self.factory = RequestFactory()

    def test_serializa_centro_com_lista_de_espacos_aninhados(self):
        request = self.factory.get('/api/centros/1/')

        serializer = Centro_com_espacosSerializer(instance=self.centro, context={'request': request})
        data = serializer.data

        self.assertIn('id', data)
        self.assertIn('nome', data)
        self.assertIn('espacos', data)
        self.assertEqual(data['nome'], 'Centro Teste Principal')

        espacos_data = data['espacos']
        self.assertIsInstance(espacos_data, list)
        self.assertEqual(len(espacos_data), 2)

        primeiro_espaco_data = espacos_data[0]
        self.assertEqual(primeiro_espaco_data['nome'], self.espaco1.nome)
        self.assertEqual(primeiro_espaco_data['categoria'], self.espaco1.categoria)
        self.assertIn('centro_esportivo_details', primeiro_espaco_data)