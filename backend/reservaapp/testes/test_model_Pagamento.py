from django.test import TestCase, RequestFactory
from django.db import IntegrityError
from datetime import date, time, timedelta
from decimal import Decimal
from ..models import CustomUser, CentroEsportivo, EspacoEsportivo, Agenda, Reserva, Pagamento
from ..serializers import PagamentoSerializer
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """configuração inicial dos dados para os testes"""
        cls.gerente = CustomUser.objects.create_user(
            email="gerente.pagamento@email.com",
            username="gerente.pagamento",
            tipo="gerente",
            nome_completo="Gerente Pagamento",
            cpf="12345678900"
        )

        cls.organizador = CustomUser.objects.create_user(
            email="organizador.pagamento@email.com",
            username="organizador.pagamento",
            tipo="organizador",
            nome_completo="Organizador Pagamento",
            cpf="98765432100"
        )

        cls.centro = CentroEsportivo.objects.create(
            nome="Centro de Teste Pagamento",
            descricao="Centro para testar Pagamento",
            latitude=-5.7945,
            longitude=-35.211,
            cidade="Natal",
            UF="RN",
            gerente=cls.gerente
        )

        cls.espaco = EspacoEsportivo.objects.create(
            nome="Quadra de Vôlei",
            categoria="volei",
            centro_esportivo=cls.centro
        )

        cls.agenda = Agenda.objects.create(
            preco=Decimal('200.00'),
            dia=date.today() + timedelta(days=5),
            h_inicial=time(14, 0),
            h_final=time(16, 0),
            espacoesportivo=cls.espaco,
            status="ativo"
        )

        cls.reserva = Reserva.objects.create(
            organizador=cls.organizador,
            agenda=cls.agenda,
            status="pendente"
        )


class PagamentoModelTest(BaseTestCase):
    def test_criar_pagamento_valido(self):
        """verifica se a criação de um pagamento válido é bem-sucedida"""
        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('100.00'),
            confirmado=False
        )

        self.assertEqual(pagamento.reserva, self.reserva)
        self.assertEqual(pagamento.valor, Decimal('100.00'))
        self.assertFalse(pagamento.confirmado)
        self.assertIsNotNone(pagamento.data_pagamento)

    def test_pagamento_com_comprovante(self):
        """verifica se é possível criar um pagamento com comprovante"""
        comprovante = SimpleUploadedFile(
            name='comprovante_teste.jpg',
            content=b'\x00\x00\x00\x00',
            content_type='image/jpeg'
        )

        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('100.00'),
            comprovante=comprovante
        )

        self.assertIsNotNone(pagamento.comprovante)
        self.assertTrue(pagamento.comprovante.name.startswith('comprovantes/'))

    def test_pagamento_confirmado_por_padrao_false(self):
        """verifica se o campo confirmado é False por padrão"""
        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('50.00')
        )

        self.assertFalse(pagamento.confirmado)

    def test_relacao_onetoone_com_reserva(self):
        """verifica se a relação OneToOne com Reserva funciona corretamente"""
        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('100.00')
        )

        self.assertEqual(self.reserva.pagamento, pagamento)

    def test_nao_permitir_dois_pagamentos_mesma_reserva(self):
        """verifica se não é possível criar dois pagamentos para a mesma reserva"""
        Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('100.00')
        )

        with self.assertRaises(IntegrityError):
            Pagamento.objects.create(
                reserva=self.reserva,
                valor=Decimal('50.00')
            )

    def test_alterar_status_confirmado(self):
        """verifica se é possível alterar o status de confirmado"""
        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('100.00'),
            confirmado=False
        )

        pagamento.confirmado = True
        pagamento.save()
        pagamento.refresh_from_db()

        self.assertTrue(pagamento.confirmado)

    def test_deletar_reserva_deleta_pagamento(self):
        """verifica se ao deletar a reserva, o pagamento também é deletado (CASCADE)"""
        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('100.00')
        )

        pagamento_id = pagamento.id
        self.reserva.delete()

        with self.assertRaises(Pagamento.DoesNotExist):
            Pagamento.objects.get(id=pagamento_id)

    def test_pagamento_valor_metade_reserva(self):
        """verifica se o pagamento pode ser de 50% do valor da reserva"""
        valor_metade = self.reserva.agenda.preco / 2

        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=valor_metade
        )

        self.assertEqual(pagamento.valor, Decimal('100.00'))


class PagamentoSerializerTest(BaseTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_serializer_contem_campos_esperados_na_leitura(self):
        """verifica se o serializer contém os campos esperados na leitura"""
        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('100.00'),
            confirmado=False
        )

        serializer = PagamentoSerializer(instance=pagamento)
        data = serializer.data

        expected_keys = ['id', 'reserva', 'valor', 'data_pagamento', 'comprovante']
        read_only_keys = ['data_pagamento', 'confirmado']

        for key in expected_keys:
            self.assertIn(key, data)

        self.assertEqual(data['valor'], '100.00')
        self.assertEqual(data['reserva'], self.reserva.id)

    def test_serializer_cria_pagamento_com_dados_validos(self):
        """verifica se o serializer cria um pagamento com dados válidos"""
        valid_data = {
            'reserva': self.reserva.id,
            'valor': '100.00'
        }

        serializer = PagamentoSerializer(data=valid_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        pagamento_criado = serializer.save()

        self.assertEqual(pagamento_criado.valor, Decimal('100.00'))
        self.assertEqual(pagamento_criado.reserva, self.reserva)
        self.assertFalse(pagamento_criado.confirmado)
        self.assertEqual(Pagamento.objects.count(), 1)

    def test_serializer_valida_campos_obrigatorios(self):
        """verifica se o serializer valida campos obrigatórios"""
        invalid_data = {}

        serializer = PagamentoSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('reserva', serializer.errors)
        self.assertIn('valor', serializer.errors)

    def test_serializer_aceita_comprovante(self):
        """verifica se o serializer aceita upload de comprovante"""
        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('100.00')
        )

        comprovante = SimpleUploadedFile(
            name='comprovante.jpg',
            content=b'\x00\x00\x00\x00',
            content_type='image/jpeg'
        )

        pagamento.comprovante = comprovante
        pagamento.save()

        self.assertIsNotNone(pagamento.comprovante)
        self.assertTrue(pagamento.comprovante.name.startswith('comprovantes/'))

