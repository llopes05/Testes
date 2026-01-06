from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from reservaapp.models import CentroEsportivo, EspacoEsportivo, Agenda, Reserva
from reservaapp.serializers import ReservaSerializer
from rest_framework.request import Request
from django.test import RequestFactory
from datetime import date, time
from decimal import Decimal


class TesteModeloReserva(TestCase):
    def setUp(self):
        self.client = APIClient()
        
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
            descricao='Centro para testes',
            latitude=Decimal('-23.55052'),
            longitude=Decimal('-46.633308'),
            cidade='São Paulo',
            UF='SP',
            gerente=self.gerente
        )
        
        self.espaco = EspacoEsportivo.objects.create(
            nome='Quadra Teste',
            categoria='futebol',
            centro_esportivo=self.centro
        )
        
        self.agenda = Agenda.objects.create(
            preco=Decimal('100.00'),
            dia=date(2025, 12, 15),
            h_inicial=time(18, 0),
            h_final=time(20, 0),
            espacoesportivo=self.espaco,
            status='ativo'
        )
        
        self.reserva = Reserva.objects.create(
            organizador=self.organizador,
            agenda=self.agenda,
            status='pendente'
        )

    def test_criacao_reserva(self):
        """Teste se a reserva foi criada corretamente"""
        reserva = Reserva.objects.get(organizador=self.organizador, agenda=self.agenda)
        self.assertEqual(reserva.organizador.nome_completo, 'Organizador Teste')
        self.assertEqual(reserva.agenda.espacoesportivo.nome, 'Quadra Teste')
        self.assertEqual(reserva.status, 'pendente')
        self.assertIsNotNone(reserva.criado_em)
        self.assertIsNone(reserva.nota_atendimento)
        self.assertIsNone(reserva.comentario_avaliacao)

    def test_criacao_reserva_organizador_invalido(self):
        """Teste se falha ao criar reserva com organizador inválido"""
        with self.assertRaises(ValueError):
            Reserva.objects.create(
                organizador=None,
                agenda=self.agenda,
                status='pendente'
            )

    def test_criacao_reserva_agenda_invalida(self):
        """Teste se falha ao criar reserva com agenda inválida"""
        with self.assertRaises(ValueError):
            Reserva.objects.create(
                organizador=self.organizador,
                agenda=None,
                status='pendente'
            )

    def test_str_reserva(self):
        """Teste se o método __str__ da reserva está funcionando"""
        reserva_str = str(self.reserva)
        self.assertIn('Organizador Teste', reserva_str)
        self.assertIn('2025-12-15', reserva_str)
        self.assertIn('pendente', reserva_str)

    def test_status_choices(self):
        """Teste se os status choices estão funcionando"""
        self.reserva.status = 'pago'
        self.reserva.save()
        self.assertEqual(self.reserva.status, 'pago')
        
        self.reserva.status = 'cancelada'
        self.reserva.save()
        self.assertEqual(self.reserva.status, 'cancelada')

    def test_notas_avaliacao(self):
        """Teste se as notas de avaliação podem ser definidas"""
        self.reserva.nota_atendimento = 5
        self.reserva.nota_espacoesportivo = 4
        self.reserva.nota_limpeza = 3
        self.reserva.comentario_avaliacao = 'Ótimo serviço!'
        self.reserva.save()
        
        reserva_atualizada = Reserva.objects.get(id=self.reserva.id)
        self.assertEqual(reserva_atualizada.nota_atendimento, 5)
        self.assertEqual(reserva_atualizada.nota_espacoesportivo, 4)
        self.assertEqual(reserva_atualizada.nota_limpeza, 3)
        self.assertEqual(reserva_atualizada.comentario_avaliacao, 'Ótimo serviço!')


class TesteSerializerReserva(TestCase):
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
            descricao='Centro para testes',
            latitude=Decimal('-23.55052'),
            longitude=Decimal('-46.633308'),
            cidade='São Paulo',
            UF='SP',
            gerente=self.gerente
        )
        
        self.espaco = EspacoEsportivo.objects.create(
            nome='Quadra Teste',
            categoria='futebol',
            centro_esportivo=self.centro
        )
        
        self.agenda = Agenda.objects.create(
            preco=Decimal('100.00'),
            dia=date(2025, 12, 15),
            h_inicial=time(18, 0),
            h_final=time(20, 0),
            espacoesportivo=self.espaco,
            status='ativo'
        )
        
        self.reserva_data = {
            'agenda': self.agenda.id,
            'status': 'pendente'
        }

    def test_serializacao_reserva_valida(self):
        """Teste se o serializer serializa dados válidos corretamente"""
        reserva = Reserva.objects.create(
            organizador=self.organizador,
            agenda=self.agenda,
            status='pendente'
        )
        
        serializer = ReservaSerializer(reserva)
        
        data = serializer.data
        self.assertEqual(data['agenda'], self.agenda.id)
        self.assertEqual(data['status'], 'pendente')
        self.assertIn('id', data)
        self.assertIn('criado_em', data)

    def test_desserializacao_dados_validos(self):
        """Teste se o serializer deserializa dados válidos corretamente"""
        serializer = ReservaSerializer(data=self.reserva_data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['agenda'], self.agenda)
        self.assertEqual(serializer.validated_data['status'], 'pendente')

    def test_validacao_agenda_obrigatoria(self):
        """Teste se o serializer valida que a agenda é obrigatória"""
        data_sem_agenda = self.reserva_data.copy()
        del data_sem_agenda['agenda']
        
        serializer = ReservaSerializer(data=data_sem_agenda)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('agenda', serializer.errors)

    def test_validacao_reserva_duplicada(self):
        """Teste se o serializer valida reservas duplicadas para a mesma agenda"""
        Reserva.objects.create(
            organizador=self.organizador,
            agenda=self.agenda,
            status='pendente'
        )
        
        serializer = ReservaSerializer(data=self.reserva_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn('Já existe uma reserva', str(serializer.errors))

    def test_campo_organizador_excluido(self):
        """Teste se o campo organizador está excluído do serializer"""
        data_com_organizador = self.reserva_data.copy()
        data_com_organizador['organizador'] = self.organizador.id
        
        serializer = ReservaSerializer(data=data_com_organizador)
        
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('organizador', serializer.validated_data)

    def test_status_choices_validos(self):
        """Teste se o serializer aceita status válidos"""
        for status_code, status_name in Reserva.STATUS_CHOICES:
            data = self.reserva_data.copy()
            data['status'] = status_code
            
            serializer = ReservaSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Status {status_code} deveria ser válido")

    def test_notas_avaliacao_opcionalais(self):
        """Teste se as notas de avaliação são opcionais"""
        data_com_notas = self.reserva_data.copy()
        data_com_notas.update({
            'nota_atendimento': 5,
            'nota_espacoesportivo': 4,
            'nota_limpeza': 3,
            'comentario_avaliacao': 'Excelente!'
        })
        
        serializer = ReservaSerializer(data=data_com_notas)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['nota_atendimento'], 5)
        self.assertEqual(serializer.validated_data['comentario_avaliacao'], 'Excelente!')

    def test_agenda_inexistente(self):
        """Teste se o serializer valida agenda inexistente"""
        data_agenda_inexistente = self.reserva_data.copy()
        data_agenda_inexistente['agenda'] = 99999
        
        serializer = ReservaSerializer(data=data_agenda_inexistente)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('agenda', serializer.errors)