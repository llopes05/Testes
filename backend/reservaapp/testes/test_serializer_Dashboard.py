from django.test import TestCase
from rest_framework.test import APIRequestFactory
from datetime import date, time, timedelta
from decimal import Decimal
from ..models import CustomUser, CentroEsportivo, EspacoEsportivo, Agenda, Reserva
from ..serializers import DashboardGerenteSerializer


class DashboardGerenteSerializerTest(TestCase):

    def setUp(self):
        # configura dados de teste
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')

        self.gerente = CustomUser.objects.create_user(
            email="gerente.dashboard@email.com",
            username="gerente.dashboard",
            tipo="gerente",
            nome_completo="Gerente Dashboard",
            cpf="12345678900",
            password="senha123"
        )

        self.organizador = CustomUser.objects.create_user(
            email="organizador.dashboard@email.com",
            username="organizador.dashboard",
            tipo="organizador",
            nome_completo="Organizador Dashboard",
            cpf="98765432100",
            password="senha123"
        )

        self.centro = CentroEsportivo.objects.create(
            nome="Centro Dashboard",
            descricao="Centro para dashboard",
            latitude=-5.7945,
            longitude=-35.211,
            cidade="Natal",
            UF="RN",
            gerente=self.gerente
        )

        self.espaco = EspacoEsportivo.objects.create(
            nome="Quadra de Futebol",
            categoria="futebol",
            centro_esportivo=self.centro
        )

        self.agenda = Agenda.objects.create(
            preco=Decimal('100.00'),
            dia=date.today() + timedelta(days=3),
            h_inicial=time(15, 0),
            h_final=time(16, 0),
            espacoesportivo=self.espaco,
            status='ativo'
        )

        self.reserva = Reserva.objects.create(
            agenda=self.agenda,
            organizador=self.organizador,
            status='pendente'
        )

    def test_serializer_contem_campos_esperados(self):
        # verifica se o serializer contém os campos esperados
        serializer = DashboardGerenteSerializer(self.reserva, context={'request': self.request})

        self.assertIn('id', serializer.data)
        self.assertIn('status', serializer.data)
        self.assertIn('organizador', serializer.data)
        self.assertIn('espaco', serializer.data)
        self.assertIn('check_in', serializer.data)

    def test_serializer_retorna_status_display(self):
        # verifica se o campo status retorna o display legível
        serializer = DashboardGerenteSerializer(self.reserva, context={'request': self.request})

        self.assertEqual(serializer.data['status'], 'Pendente')

    def test_serializer_retorna_nome_organizador(self):
        # verifica se o campo organizador retorna o nome completo
        serializer = DashboardGerenteSerializer(self.reserva, context={'request': self.request})

        self.assertEqual(serializer.data['organizador'], 'Organizador Dashboard')

    def test_serializer_retorna_espaco_nome_e_categoria(self):
        # verifica se o campo espaco retorna tupla (nome, categoria)
        serializer = DashboardGerenteSerializer(self.reserva, context={'request': self.request})

        self.assertEqual(serializer.data['espaco'], ('Quadra de Futebol', 'futebol'))

    def test_serializer_retorna_check_in_formatado(self):
        # verifica se o campo check_in retorna data e hora formatadas
        serializer = DashboardGerenteSerializer(self.reserva, context={'request': self.request})

        data_esperada = self.agenda.dia.strftime('%d/%m/%Y')
        hora_esperada = self.agenda.h_inicial.strftime('%H:%M')
        check_in_esperado = f"{data_esperada} {hora_esperada}"

        self.assertEqual(serializer.data['check_in'], check_in_esperado)

    def test_serializer_com_diferentes_status(self):
        # verifica se o serializer funciona com diferentes status de reserva
        status_list = ['pendente', 'pago', 'cancelado']

        for status in status_list:
            self.reserva.status = status
            self.reserva.save()

            serializer = DashboardGerenteSerializer(self.reserva, context={'request': self.request})

            self.assertIn('status', serializer.data)
            self.assertEqual(serializer.data['id'], self.reserva.id)
