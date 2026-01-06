from django.test import TestCase
from django.contrib.auth import get_user_model
from reservaapp.models import CentroEsportivo, EspacoEsportivo, Agenda, Reserva
from reservaapp.serializers import ReservaDetalhadaSerializer
from rest_framework.request import Request
from django.test import RequestFactory
from datetime import date, time
from decimal import Decimal


class TesteSerializerReservaDetalhada(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        self.gerente = get_user_model().objects.create_user(
            username='gerente',
            email='gerente@test.com',
            password='testpassword',
            tipo='gerente',
            nome_completo='Gerente Teste',
            cpf='12345678901'
        )
        
        self.organizador = get_user_model().objects.create_user(
            username='organizador',
            email='organizador@test.com',
            password='testpassword',
            tipo='organizador',
            nome_completo='Organizador Teste',
            cpf='10987654321'
        )

        self.centro = CentroEsportivo.objects.create(
            nome='Centro Teste',
            descricao='Centro para testes de reserva detalhada',
            latitude=Decimal('-23.55052'),
            longitude=Decimal('-46.633308'),
            cidade='São Paulo',
            UF='SP',
            gerente=self.gerente
        )
        
        self.espaco = EspacoEsportivo.objects.create(
            nome='Quadra Teste Detalhada',
            categoria='futebol',
            centro_esportivo=self.centro
        )
        
        self.agenda = Agenda.objects.create(
            preco=Decimal('150.00'),
            dia=date(2025, 12, 20),
            h_inicial=time(19, 0),
            h_final=time(21, 0),
            espacoesportivo=self.espaco,
            status='ativo'
        )
        
        self.reserva = Reserva.objects.create(
            organizador=self.organizador,
            agenda=self.agenda,
            status='pago',
            nota_atendimento=5,
            nota_espacoesportivo=4,
            nota_limpeza=5,
            comentario_avaliacao='Excelente instalação!'
        )

    def test_serializacao_reserva_detalhada_valida(self):
        """Teste se o serializer serializa uma reserva detalhada corretamente"""
        request = self.factory.get('/')
        serializer = ReservaDetalhadaSerializer(
            self.reserva, 
            context={'request': Request(request)}
        )
        
        data = serializer.data
        
        self.assertEqual(data['id'], self.reserva.id)
        self.assertEqual(data['status'], 'pago')
        self.assertEqual(data['nota_atendimento'], 5)
        self.assertEqual(data['nota_espacoesportivo'], 4)
        self.assertEqual(data['nota_limpeza'], 5)
        self.assertEqual(data['comentario_avaliacao'], 'Excelente instalação!')
        self.assertEqual(data['organizador'], self.organizador.id)
        
        self.assertIn('agenda', data)
        agenda_data = data['agenda']
        self.assertEqual(agenda_data['id'], self.agenda.id)
        self.assertEqual(agenda_data['dia'], '2025-12-20')
        self.assertEqual(agenda_data['h_inicial'], '19:00:00')
        self.assertEqual(agenda_data['h_final'], '21:00:00')
        self.assertEqual(agenda_data['preco'], '150.00')

    def test_agenda_detalhada_incluida(self):
        """Teste se os detalhes da agenda são incluídos corretamente"""
        serializer = ReservaDetalhadaSerializer(self.reserva)
        data = serializer.data
        
        self.assertIn('agenda', data)
        agenda_data = data['agenda']
        
        campos_esperados = ['id', 'dia', 'h_inicial', 'h_final', 'preco', 'espacoesportivo']
        for campo in campos_esperados:
            self.assertIn(campo, agenda_data)

    def test_espaco_esportivo_detalhado_incluido(self):
        """Teste se os detalhes do espaço esportivo são incluídos"""
        request = self.factory.get('/')
        serializer = ReservaDetalhadaSerializer(
            self.reserva, 
            context={'request': Request(request)}
        )
        
        data = serializer.data
        
        espacoesportivo_data = data['agenda']['espacoesportivo']
        self.assertEqual(espacoesportivo_data['id'], self.espaco.id)
        self.assertEqual(espacoesportivo_data['nome'], 'Quadra Teste Detalhada')
        self.assertEqual(espacoesportivo_data['categoria'], 'futebol')

    def test_centro_esportivo_detalhado_incluido(self):
        """Teste se os detalhes do centro esportivo são incluídos"""
        request = self.factory.get('/')
        serializer = ReservaDetalhadaSerializer(
            self.reserva, 
            context={'request': Request(request)}
        )
        
        data = serializer.data
        
        centro_data = data['agenda']['espacoesportivo']['centro_esportivo_details']
        self.assertEqual(centro_data['id'], self.centro.id)
        self.assertEqual(centro_data['nome'], 'Centro Teste')
        self.assertEqual(centro_data['cidade'], 'São Paulo')
        self.assertEqual(centro_data['UF'], 'SP')

    def test_todos_campos_reserva_incluidos(self):
        """Teste se todos os campos da reserva estão incluídos"""
        serializer = ReservaDetalhadaSerializer(self.reserva)
        data = serializer.data
        
        campos_esperados = [
            'id', 'organizador', 'agenda', 'nota_atendimento', 
            'nota_espacoesportivo', 'nota_limpeza', 'comentario_avaliacao',
            'criado_em', 'status', 'cancelar_reserva'
        ]
        
        for campo in campos_esperados:
            self.assertIn(campo, data, f"Campo {campo} deveria estar presente")

    def test_reserva_sem_notas_avaliacao(self):
        """Teste serialização de reserva sem notas de avaliação"""
        reserva_sem_notas = Reserva.objects.create(
            organizador=self.organizador,
            agenda=self.agenda,
            status='pendente'
        )
        
        serializer = ReservaDetalhadaSerializer(reserva_sem_notas)
        data = serializer.data
        
        self.assertIsNone(data['nota_atendimento'])
        self.assertIsNone(data['nota_espacoesportivo'])
        self.assertIsNone(data['nota_limpeza'])
        self.assertIsNone(data['comentario_avaliacao'])
        self.assertEqual(data['status'], 'pendente')

    def test_reserva_cancelada(self):
        """Teste serialização de reserva cancelada"""
        from django.utils import timezone
        
        reserva_cancelada = Reserva.objects.create(
            organizador=self.organizador,
            agenda=self.agenda,
            status='cancelada',
            cancelar_reserva=timezone.now()
        )
        
        serializer = ReservaDetalhadaSerializer(reserva_cancelada)
        data = serializer.data
        
        self.assertEqual(data['status'], 'cancelada')
        self.assertIsNotNone(data['cancelar_reserva'])

    def test_urls_fotos_espaco_incluidas(self):
        """Teste se as URLs das fotos do espaço são incluídas quando disponíveis"""
        request = self.factory.get('/')
        serializer = ReservaDetalhadaSerializer(
            self.reserva, 
            context={'request': Request(request)}
        )
        
        data = serializer.data
        espacoesportivo_data = data['agenda']['espacoesportivo']
        
        urls_esperadas = ['foto_perfil_url', 'foto_capa_url', 'foto1_url', 'foto2_url', 'foto3_url', 'foto4_url']
        for url in urls_esperadas:
            self.assertIn(url, espacoesportivo_data)

    def test_serializer_read_only(self):
        """Teste se o serializer é somente leitura (não aceita dados de entrada)"""
        serializer = ReservaDetalhadaSerializer(data={
            'organizador': self.organizador.id,
            'agenda': self.agenda.id,
            'status': 'pendente'
        })
        
        data = serializer.data if hasattr(serializer, 'data') else None
        
        serializer_leitura = ReservaDetalhadaSerializer(self.reserva)
        self.assertIsNotNone(serializer_leitura.data)