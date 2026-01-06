from django.test import TestCase
from datetime import date, time
from reservaapp.models import CustomUser, CentroEsportivo, EspacoEsportivo, Agenda
from reservaapp.serializers import AgendaDetalhadaSerializer

class AgendaDetalhadaSerializerTest(TestCase):
    def setUp(self):
        # Primeiro cria o usuário gerente
        self.gerente = CustomUser.objects.create(
            email='gerente@teste.com',
            username='gerente',
            tipo='gerente',
            nome_completo='Gerente Teste',
            cpf='123.456.789-00'
        )
        
        # Agora cria o CentroEsportivo
        self.centro = CentroEsportivo.objects.create(
            nome='Centro Esportivo Teste',
            descricao='Descrição do centro teste',
            latitude=-23.5505,
            longitude=-46.6333,
            cidade='São Paulo',
            UF='SP',
            gerente=self.gerente,
            media_avaliacao=4.5
        )
        
        # Cria o Espaço Esportivo
        self.espaco = EspacoEsportivo.objects.create(
            nome='Quadra de Futebol',
            categoria='futebol',
            centro_esportivo=self.centro
        )
        
        # Cria a Agenda
        self.agenda = Agenda.objects.create(
            espacoesportivo=self.espaco,
            dia=date.today(),
            h_inicial=time(8, 0),
            h_final=time(10, 0),
            preco=100.00,
            status='ativo'
        )

    def test_campos_serializados(self):
        """Testa se todos os campos estão sendo serializados"""
        serializer = AgendaDetalhadaSerializer(self.agenda)
        data = serializer.data
        
        # Verifica apenas os campos que realmente existem no serializer
        campos_esperados = ['id', 'dia', 'h_inicial', 'h_final', 'preco', 'espacoesportivo']
        for campo in campos_esperados:
            self.assertIn(campo, data)

    def test_espaco_aninhado(self):
        """Testa se o espaço esportivo está aninhado corretamente"""
        serializer = AgendaDetalhadaSerializer(self.agenda)
        data = serializer.data
        
        # Verifica se o espaço esportivo está aninhado
        self.assertIn('espacoesportivo', data)
        espaco_data = data['espacoesportivo']
        self.assertEqual(espaco_data['nome'], 'Quadra de Futebol')
        self.assertEqual(espaco_data['categoria'], 'futebol')

    def test_dados_formatados_corretamente(self):
        """Testa se os dados estão formatados corretamente"""
        serializer = AgendaDetalhadaSerializer(self.agenda)
        data = serializer.data
        
        # Verifica formatação dos dados que existem no serializer
        self.assertEqual(data['preco'], '100.00')
        self.assertEqual(data['dia'], str(date.today()))
        self.assertEqual(data['h_inicial'], '08:00:00')
        self.assertEqual(data['h_final'], '10:00:00')
        # Remove a verificação do status pois não está no serializer