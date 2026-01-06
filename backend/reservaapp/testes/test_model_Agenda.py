from django.test import TestCase
from datetime import date, time, timedelta
from ..models import CustomUser, CentroEsportivo, EspacoEsportivo, Agenda
from ..serializers import AgendaSerializer


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gerente = CustomUser.objects.create_user(
            email="gerente.agenda@email.com",
            username="gerente.agenda",
            tipo="gerente",
            nome_completo="Gerente Agenda",
            cpf="12345678900"
        )

        cls.centro = CentroEsportivo.objects.create(
            nome="Centro de Teste Agenda",
            descricao="Centro para testar a Agenda",
            latitude=-5.7945,
            longitude=-35.211,
            cidade="Natal",
            UF="RN",
            gerente=cls.gerente
        )

        cls.espaco = EspacoEsportivo.objects.create(
            nome="Quadra de Futsal",
            categoria="futsal",
            centro_esportivo=cls.centro
        )


class AgendaModelTest(BaseTestCase):
    def test_criar_agenda_valida(self):
        """Verifica se a criação de uma Agenda válida é bem-sucedida."""
        agenda = Agenda.objects.create(
            preco=150.00,
            dia=date.today() + timedelta(days=1),
            h_inicial=time(8, 0),
            h_final=time(10, 0),
            espacoesportivo=self.espaco,
            status="ativo"
        )

        self.assertEqual(agenda.preco, 150.00)
        self.assertEqual(agenda.status, "ativo")
        self.assertEqual(agenda.espacoesportivo, self.espaco)
        self.assertEqual(str(agenda), f"{self.centro.nome} | {self.espaco.nome} - {agenda.dia} ({agenda.h_inicial}-{agenda.h_final}) - ativo")

    def test_status_padrao_eh_ativo(self):
        """Testa se o campo 'status' é 'ativo' por padrão."""
        agenda = Agenda.objects.create(
            preco=200.00,
            dia=date.today() + timedelta(days=2),
            h_inicial=time(14, 0),
            h_final=time(16, 0),
            espacoesportivo=self.espaco
        )
        self.assertEqual(agenda.status, "ativo")


class AgendaSerializerTest(BaseTestCase):
    def test_serializer_cria_agenda_valida(self):
        """Testa se o serializer cria uma Agenda válida corretamente."""
        data = {
            "preco": "100.00",
            "dia": str(date.today() + timedelta(days=3)),
            "h_inicial": "09:00",
            "h_final": "10:00",
            "espacoesportivo": self.espaco.id
        }

        serializer = AgendaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        agenda = serializer.save()

        self.assertEqual(agenda.espacoesportivo, self.espaco)
        self.assertEqual(agenda.preco, 100.00)
        self.assertEqual(Agenda.objects.count(), 1)

    def test_serializer_falha_horario_invalido(self):
        """Deve falhar quando o horário inicial for igual ou posterior ao final."""
        data = {
            "preco": "120.00",
            "dia": str(date.today() + timedelta(days=1)),
            "h_inicial": "10:00",
            "h_final": "09:00",
            "espacoesportivo": self.espaco.id
        }

        serializer = AgendaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("h_final", serializer.errors)

    def test_serializer_falha_por_sobreposicao(self):
        """Deve falhar se houver sobreposição de horário no mesmo espaço e dia."""
        # Agenda existente: 8h às 10h
        Agenda.objects.create(
            preco=150.00,
            dia=date.today() + timedelta(days=1),
            h_inicial=time(8, 0),
            h_final=time(10, 0),
            espacoesportivo=self.espaco
        )

        # Tentativa de criar outra: 9h às 11h (sobreposição)
        data = {
            "preco": "180.00",
            "dia": str(date.today() + timedelta(days=1)),
            "h_inicial": "09:00",
            "h_final": "11:00",
            "espacoesportivo": self.espaco.id
        }

        serializer = AgendaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_serializer_falha_por_horario_igual(self):
        """Deve falhar se o horário inicial for igual ao final."""
        data = {
            "preco": "150.00",
            "dia": str(date.today() + timedelta(days=1)),
            "h_inicial": "10:00",
            "h_final": "10:00",
            "espacoesportivo": self.espaco.id
        }

        serializer = AgendaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("h_final", serializer.errors)