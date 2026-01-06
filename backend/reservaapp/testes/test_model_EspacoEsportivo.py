from django.test import TestCase, RequestFactory
from ..models import CustomUser, CentroEsportivo, EspacoEsportivo
from ..serializers import EspacoEsportivoSerializer

class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gerente = CustomUser.objects.create_user(
            email="gerente.teste@email.com",
            username="gerente.teste",
            tipo="gerente",
            nome_completo="Gerente de Testes",
            cpf="12332112332"
        )

        cls.centro = CentroEsportivo.objects.create(
            nome="Centro Teste Principal",
            descricao="Descrição do Centro",
            latitude=-23.5505,
            longitude=-46.6333,
            cidade="Natal",
            UF="RN",
            gerente=cls.gerente
        )

class EspacoEsportivoModelTest(BaseTestCase):
    def test_criar_espaco_esportivo(self):
        espaco = EspacoEsportivo.objects.create(
            nome="Quadra de Tênis A",
            categoria="tenis",
            centro_esportivo=self.centro
        )

        self.assertEqual(espaco.nome, "Quadra de Tênis A")
        self.assertEqual(espaco.categoria, "tenis")
        self.assertEqual(espaco.centro_esportivo, self.centro)
    
    def test_str_representation(self):
        espaco = EspacoEsportivo.objects.create(
            nome="Campo Society",
            categoria="futebol",
            centro_esportivo=self.centro
        )

        self.assertEqual(str(espaco), "EspacoEsportivo Campo Society")

class EspacoEsportivoSerializerTest(BaseTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_serializer_contem_campos_esperados_na_leitura(self):
        espaco = EspacoEsportivo.objects.create(
            nome="Piscina Olímpica", 
            categoria="natação", 
            centro_esportivo=self.centro
        )

        request = self.factory.get("/qualquer/url")
        serializer = EspacoEsportivoSerializer(instance=espaco, context={ "request":request })
        data = serializer.data

        expected_keys = [
            "id",
            "nome",
            "categoria",
            "foto_perfil_url",
            "centro_esportivo_details"
        ]

        write_only_keys = [
            "centro_esportivo",
            "foto_perfil",
            "foto_capa"
        ]

        for key in expected_keys:
            self.assertIn(key, data)
        
        for key in write_only_keys:
            self.assertNotIn(key, data)
        
        self.assertEqual(data['nome'], 'Piscina Olímpica')

    def test_serializer_cria_objeto_com_dados_validos(self):
        valid_data = {
            'nome': 'Quadra de Vôlei de Areia',
            'categoria': 'volei',
            'centro_esportivo': self.centro.id
        }

        serializer = EspacoEsportivoSerializer(data=valid_data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        espaco_criado = serializer.save()
        self.assertEqual(espaco_criado.nome, 'Quadra de Vôlei de Areia')
        self.assertEqual(EspacoEsportivo.objects.count(), 1)


    def test_serializer_falha_com_nome_duplicado_no_mesmo_centro(self):
        EspacoEsportivo.objects.create(
            nome='Quadra Poliesportiva',
            categoria='futsal',
            centro_esportivo=self.centro
        )

        invalid_data = {
            'nome': 'Quadra Poliesportiva',
            'categoria': 'basquete',
            'centro_esportivo': self.centro.id
        }

        serializer = EspacoEsportivoSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)