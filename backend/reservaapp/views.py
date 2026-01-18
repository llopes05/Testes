from reservaapp.serializers import (
    AgendaSerializer,
    Centro_com_espacosSerializer,
    CentroEsportivoSerializer,
    CustomUserSerializer,
    DashboardGerenteSerializer,
    EspacoEsportivoSerializer,
    HorarioDisponivelSerializer,
    ReservaDetalhadaSerializer,
    ReservaSerializer,
    PagamentoSerializer,
    AgendaDetalhadaSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from .models import (
    CustomUser,
    CentroEsportivo,
    EspacoEsportivo,
    Agenda,
    Reserva,
    Pagamento,
)
from rest_framework import viewsets, generics
from .permissions import IsGerente, IsOrganizador
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import APIView
from .filters import (
    CentroEsportivoFilter,
    EspacoEsportivoFilter,
    AgendaFilter,
    DashboardFilter,
)
from datetime import datetime, time
from django.db.models import Count, Q
from collections import defaultdict


# view para criação de usuário
class CustomUserCreateView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]


# view para verificar se o email já está em uso, caso não esteja vai pra outra tela no front
class VerificarEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email não informado."}, status=status.HTTP_400_BAD_REQUEST
            )
        exists = CustomUser.objects.filter(email=email).exists()
        return Response({"exists": exists})


# crud do centro esportivo, apenas o gerente do seu centro pode criar, editar e deletar
class CentroEsportivoViewSet(viewsets.ModelViewSet):
    queryset = CentroEsportivo.objects.all()
    serializer_class = CentroEsportivoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsGerente]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CentroEsportivoFilter

    # Override perform_create para atribuir o gerente automaticamente
    def perform_create(self, serializer):
        if self.request.user.tipo != "gerente":
            raise PermissionDenied("Apenas gerentes podem criar centros esportivos.")
        serializer.save(gerente=self.request.user)


# crud do espaco esportivo, apenas o gerente do seu centro pode criar, editar e deletar
class EspacoEsportivoViewSet(viewsets.ModelViewSet):
    queryset = EspacoEsportivo.objects.all()
    serializer_class = EspacoEsportivoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsGerente]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EspacoEsportivoFilter

    # Override perform_create para atribuir o gerente automaticamente
    def perform_create(self, serializer):
        centro_esportivo = serializer.validated_data.get("centro_esportivo")
        if (
            self.request.user.tipo != "gerente"
            or centro_esportivo.gerente != self.request.user
        ):
            raise PermissionDenied(
                "Apenas o gerente do centro esportivo pode adicionar espaços esportivos."
            )
        serializer.save()


# crud da agenda, apenas o gerente do seu centro pode criar, editar e deletar, com filtros por status, dia e espaço esportivo
class AgendaViewSet(viewsets.ModelViewSet):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsGerente]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "dia", "espacoesportivo"]
    filterset_class = AgendaFilter

    # Override perform_create para atribuir o gerente automaticamente
    def perform_create(self, serializer):
        espaco = serializer.validated_data.get("espacoesportivo")
        if (
            self.request.user.tipo != "gerente"
            or espaco.centro_esportivo.gerente != self.request.user
        ):
            raise PermissionDenied(
                "Apenas o gerente do centro esportivo pode adicionar horários na agenda."
            )
        serializer.save()


# criação de reservas com o createview, só organizadores conseguem criar
class ReservaCreateview(CreateAPIView):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsOrganizador]

    # atribuir reserva diretamente ao organizador que criou
    def perform_create(self, serializer):
        agenda = serializer.validated_data.get("agenda")
        if agenda.status != "ativo":
            raise ValidationError("Horário não está disponível para reserva.")

        agenda.status = "indisponível"
        agenda.save()
        serializer.save(organizador=self.request.user, status="pendente")


# vai pegar os centros e os espaços dentro dele, retornando os dois juntos (nao ta sendo usado no front)
class Centro_com_espacosRetrieveView(RetrieveAPIView):
    queryset = CentroEsportivo.objects.all()
    serializer_class = Centro_com_espacosSerializer
    permission_classes = [AllowAny]


# pega as reservas do organizador
class MinhasReservasListView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReservaDetalhadaSerializer
    permission_classes = [IsOrganizador]

    # somente retorna as reservas do organizador logado, nao consegue ver as dos outros
    def get_queryset(self):
        user = self.request.user
        if user.tipo == "organizador":
            return Reserva.objects.filter(organizador=user)
        return Reserva.objects.none()


# mostrar o nome do usuario logado
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


# view para listar os horários disponíveis de um espaço esportivo em um dia específico
class HorariosDisponiveisView(APIView):
    def get(self, request, espaco_id):
        dia_str = request.query_params.get("dia")
        if not dia_str:
            return Response(
                {"error": 'Parâmetro "dia" é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            dia = datetime.strptime(dia_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Formato de data inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            espaco = EspacoEsportivo.objects.get(id=espaco_id)
        except EspacoEsportivo.DoesNotExist:
            return Response(
                {"error": "Espaço esportivo não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Busca as agendas disponíveis
        agendas_disponiveis = Agenda.objects.filter(
            espacoesportivo=espaco, dia=dia, status="ativo"
        ).exclude(reserva__status="pago")

        # Agrupar os horários
        horarios_categorizados = {"manha": [], "tarde": [], "noite": []}

        for agenda in agendas_disponiveis:
            hora_inicio = agenda.h_inicial

            if time(5, 0) <= hora_inicio < time(12, 0):
                categoria = "manha"
            elif time(12, 0) <= hora_inicio < time(18, 0):
                categoria = "tarde"
            else:
                categoria = "noite"

            horarios_categorizados[categoria].append(
                HorarioDisponivelSerializer(agenda).data
            )

        return Response(horarios_categorizados, status=status.HTTP_200_OK)


# dashboard do gerente com as reservas do seu centro esportivo
class GerenteDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DashboardGerenteSerializer
    permission_classes = [IsAuthenticated, IsGerente]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DashboardFilter

    def get_queryset(self):
        user = self.request.user
        return Reserva.objects.filter(
            agenda__espacoesportivo__centro_esportivo__gerente=user
        ).order_by("-criado_em")


# view para cancelar a reserva, apenas o gerente do centro pode cancelar
class CancelarReservaView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            reserva = Reserva.objects.get(pk=pk)
            user = request.user

            # Verificação de Permissão Manual
            is_dono_reserva = reserva.organizador == user
            is_dono_espaco = (
                reserva.agenda.espacoesportivo.centro_esportivo.gerente == user
            )

            # Se não for nem um nem outro, bloqueia
            if not is_dono_reserva and not is_dono_espaco:
                return Response(
                    {"error": "Você não tem permissão para cancelar esta reserva."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Regra de Negócio: Não cancelar reservas já passadas/concluídas/canceladas
            if reserva.status == "cancelada":
                return Response(
                    {"error": "Esta reserva já está cancelada."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Opcional: Impedir cancelamento de jogos que já aconteceram
            # if reserva.agenda.dia < timezone.now().date(): ...

            # Executa o cancelamento
            reserva.status = "cancelada"
            reserva.cancelar_reserva = datetime.now()
            reserva.save()

            # Libera a agenda novamente
            reserva.agenda.status = "ativo"
            reserva.agenda.save()

            return Response(
                {"message": "Reserva cancelada com sucesso."}, status=status.HTTP_200_OK
            )

        except Reserva.DoesNotExist:
            return Response(
                {"error": "Reserva não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )


# view para concluir a reserva, apenas o gerente do centro pode concluir
class ConcluirReservaView(APIView):
    permission_classes = [IsAuthenticated, IsGerente]

    def put(self, request, pk):
        try:
            # Buscar a reserva
            reserva = Reserva.objects.get(pk=pk)

            # Verificar se o gerente tem permissão para esta reserva
            if reserva.agenda.espacoesportivo.centro_esportivo.gerente != request.user:
                return Response(
                    {"error": "Você não tem permissão para concluir esta reserva."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Verificar se a reserva pode ser concluída
            if reserva.status in ["cancelada", "pago"]:
                return Response(
                    {"error": "Esta reserva não pode ser concluída."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Marcar como pago (concluída)
            reserva.status = "pago"
            reserva.save()

            return Response(
                {"message": "Reserva concluída com sucesso."}, status=status.HTTP_200_OK
            )

        except Reserva.DoesNotExist:
            return Response(
                {"error": "Reserva não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )


# view para listar os centros esportivos do gerente logado
class MeuCentroEsportivoView(APIView):
    permission_classes = [IsGerente]

    def get(self, request, *args, **kwargs):
        centros = CentroEsportivo.objects.filter(gerente=request.user)
        serializer = CentroEsportivoSerializer(
            centros, many=True, context={"request": request}
        )

        return Response(serializer.data)


# view para listar as estatísticas do gerente, como reservas por status, espaços mais reservados, horários mais populares, categorias mais populares, total de reservas, reservas canceladas, reservas pagas e arrecadação total
class EstatisticasGerenteView(APIView):
    permission_classes = [IsAuthenticated, IsGerente]

    def get(self, request):
        user = request.user
        reservas = Reserva.objects.filter(
            agenda__espacoesportivo__centro_esportivo__gerente=user
        )

        stats_status = (
            reservas.values("status").annotate(total=Count("id")).order_by("-total")
        )

        espacos_populares = (
            reservas.values(
                "agenda__espacoesportivo__nome", "agenda__espacoesportivo__categoria"
            )
            .annotate(total_reservas=Count("id"))
            .order_by("-total_reservas")[:5]
        )

        horarios_populares = (
            reservas.values("agenda__h_inicial", "agenda__h_final")
            .annotate(total_reservas=Count("id"))
            .order_by("-total_reservas")[:5]
        )

        categorias_populares = (
            reservas.values("agenda__espacoesportivo__categoria")
            .annotate(total_reservas=Count("id"))
            .order_by("-total_reservas")
        )

        arrecadacao_total = sum(
            reserva.agenda.preco for reserva in reservas if reserva.status == "pago"
        )

        reservas_concluidas = (
            reservas.filter(status="pago")
            .values(
                "agenda__espacoesportivo__nome",
                "agenda__dia",
                "organizador__nome_completo",
                "criado_em",
            )
            .order_by("-criado_em")
        )

        return Response(
            {
                "resumo_status": list(stats_status),
                "espacos_mais_reservados": list(espacos_populares),
                "horarios_mais_reservados": list(horarios_populares),
                "categorias_mais_populares": list(categorias_populares),
                "total_reservas": reservas.count(),
                "reservas_canceladas": reservas.filter(status="cancelada").count(),
                "reservas_pagas": list(reservas_concluidas),
                "arrecadacao_total": arrecadacao_total,
            }
        )


# viewset para o pagamento, apenas o organizador pode criar o pagamento da sua reserva
class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated, IsOrganizador]

    def perform_create(self, serializer):
        reserva = serializer.validated_data.get("reserva")
        valor_pago = serializer.validated_data.get("valor")
        valor_total_reserva = reserva.agenda.preco

        if reserva.organizador != self.request.user:
            raise ValidationError("Você não tem permissão para pagar esta reserva.")

        if reserva.status != "pendente":
            raise ValidationError("Esta reserva não está aguardando pagamento.")

        if hasattr(reserva, "pagamento"):
            raise ValidationError("Já existe um pagamento para esta reserva.")

        if valor_pago < (valor_total_reserva / 2):
            raise ValidationError(
                f"O pagamento mínimo é de 50% do valor total (R$ {valor_total_reserva / 2:.2f})."
            )

        pagamento = serializer.save(confirmado=False)
        # Mantém o status da reserva como 'pendente' para confirmação manual
        # O status só será alterado para 'pago' quando um gerente confirmar o pagamento
