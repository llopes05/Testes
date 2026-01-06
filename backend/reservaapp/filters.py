import django_filters
from .models import CentroEsportivo, EspacoEsportivo, Agenda, Reserva

class CentroEsportivoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='nome', lookup_expr='icontains')
    cidade = django_filters.CharFilter(field_name='cidade', lookup_expr='icontains')
    categoria_espaco = django_filters.CharFilter(
        method='filtrar_por_categoria_do_espaco',
        label="Filtrar por categoria do espaço (ex: futebol, vôlei)"
    )
    UF = django_filters.CharFilter(field_name='UF', lookup_expr='iexact')


    class Meta:
        model = CentroEsportivo
        fields = ['nome', 'cidade', 'UF']

    def filtrar_por_categoria_do_espaco(self, queryset, name, value): #isso vai buscar os espaços dentro do centro
        if value:
            return queryset.filter(espacos__categoria__iexact=value).distinct()
        return queryset 

class EspacoEsportivoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='nome', lookup_expr='icontains')
    categoria = django_filters.CharFilter(field_name='categoria', lookup_expr='icontains')

    class Meta:
        model = EspacoEsportivo
        fields = ['nome', 'categoria', 'centro_esportivo']

class AgendaFilter(django_filters.FilterSet):
    class Meta:
        model = Agenda
        fields = ['status', 'dia', 'espacoesportivo']

class DashboardFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    organizador = django_filters.CharFilter(field_name='organizador__nome_completo', lookup_expr='icontains')
    espaco = django_filters.CharFilter(field_name='agenda__espacoesportivo__nome', lookup_expr='icontains')
    categoria = django_filters.CharFilter(field_name='agenda__espacoesportivo__categoria', lookup_expr='iexact')

    data_inicio = django_filters.DateFilter(field_name='criado_em', lookup_expr='gte')
    data_fim = django_filters.DateFilter(field_name='criado_em', lookup_expr='lte')


    class Meta:
        model = Reserva
        fields = ['status', 'organizador', 'espaco']