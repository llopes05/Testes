from django.urls import path, include
from .views import (
    AgendaViewSet,
    CancelarReservaView,
    Centro_com_espacosRetrieveView,
    CentroEsportivoViewSet,
    ConcluirReservaView,
    CustomUserCreateView,
    EspacoEsportivoViewSet,
    GerenteDashboardViewSet,
    HorariosDisponiveisView,
    MeView,
    MinhasReservasListView,
    ReservaCreateview,
    VerificarEmailView,
    MeuCentroEsportivoView,
    EstatisticasGerenteView,
    PagamentoViewSet
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)
from django.conf import settings             
from django.conf.urls.static import static   

#Swagger
schema_view = get_schema_view(
   openapi.Info(
      title="Reserva API",
      default_version='v1',
      description="O projeto Reserva é um sistema web para facilitar a reserva de quadras e campos esportivos. Ele permite aos usuários encontrar locais, consultar preços e horários, ver avaliações e realizar reservas. O sistema também visa simplificar a comunicação entre usuários e proprietários dos espaços esportivos.",
      
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

#Routers
router = DefaultRouter(trailing_slash=False)
router.register(r'centros-esportivos', CentroEsportivoViewSet, basename='espacos-esportivos')
router.register(r'espacos', EspacoEsportivoViewSet)
router.register(r'agendas', AgendaViewSet)
#router.register(r'reservas', ReservaViewSet)
router.register(r'minhas-reservas', MinhasReservasListView, basename='minhas-reservas')
router.register(r'dashboard-gerente', GerenteDashboardViewSet, basename='dashboard-gerente')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamentos')


urlpatterns = [
    #urls do swagger
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    #urls das views - sem barra final para compatibilidade com Karate
    path('api/register', CustomUserCreateView.as_view(), name='register'),
    path('api/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/me', MeView.as_view(), name='me'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/centros/<int:pk>', Centro_com_espacosRetrieveView.as_view(), name='centro-com-espacos'),
    path('api/check-email', VerificarEmailView.as_view(), name='verificar-email'),
    path('api/reservar', ReservaCreateview.as_view(), name='reservar'),
    path('api/me/centros', MeuCentroEsportivoView.as_view(), name='meu-centro-esportivo'),
    path('api/reservas/<int:pk>/cancelar', CancelarReservaView.as_view(), name='cancelar-reserva'),
    path('api/reservas/<int:pk>/concluir', ConcluirReservaView.as_view(), name='concluir-reserva'),
    path('api/espacos/<int:espaco_id>/horarios_disponiveis', HorariosDisponiveisView.as_view(), name='horarios_disponiveis'),
    path('api/estatisticas-gerente', EstatisticasGerenteView.as_view(), name='estatisticas-gerente'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)