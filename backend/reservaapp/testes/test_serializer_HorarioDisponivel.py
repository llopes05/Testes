from django.test import TestCase
from datetime import date, time
from reservaapp.models import CustomUser, CentroEsportivo, EspacoEsportivo, Agenda
from reservaapp.serializers import HorarioDisponivelSerializer

class HorarioDisponivelSerializerTest(TestCase):
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
        serializer = HorarioDisponivelSerializer(self.agenda)
        data = serializer.data
        
        # Verifica se os campos esperados existem
        campos_esperados = ['id', 'dia', 'h_inicial', 'h_final', 'preco']
        for campo in campos_esperados:
            self.assertIn(campo, data)

    def test_dados_formatados_corretamente(self):
        """Testa se os dados estão formatados corretamente"""
        serializer = HorarioDisponivelSerializer(self.agenda)
        data = serializer.data
        
        # Verifica formatação dos dados
        self.assertEqual(data['preco'], '100.00')
        self.assertEqual(data['dia'], str(date.today()))
        self.assertEqual(data['h_inicial'], '08:00:00')
        self.assertEqual(data['h_final'], '10:00:00')

    def test_nao_inclui_espacoesportivo(self):
        """Testa que o serializer não inclui espacoesportivo (diferente do AgendaDetalhadaSerializer)"""
        serializer = HorarioDisponivelSerializer(self.agenda)
        data = serializer.data
        
        # Verifica que espacoesportivo NÃO está incluído
        self.assertNotIn('espacoesportivo', data)
        
    def test_nao_inclui_status(self):
        """Testa que o serializer não inclui status"""
        serializer = HorarioDisponivelSerializer(self.agenda)
        data = serializer.data
        
        # Verifica que status NÃO está incluído
        self.assertNotIn('status', data)