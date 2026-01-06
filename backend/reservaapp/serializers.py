from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.db.models import Min

from .models import CentroEsportivo, EspacoEsportivo, Agenda, Reserva, Pagamento

#serializer para o usuario
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'tipo', 'nome_completo', 'cpf', 'password']
        extra_kwargs = {
            'cpf': {'min_length': 11, 'max_length': 11},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user

#serializer para o centro esportivo
class CentroEsportivoSerializer(serializers.ModelSerializer):
    foto_perfil_url = serializers.SerializerMethodField()
    foto_capa_url = serializers.SerializerMethodField()
    menor_preco = serializers.SerializerMethodField()
    total_avaliacoes = serializers.SerializerMethodField()
    class Meta:
        model = CentroEsportivo
        fields = ['id', 'nome', 'descricao', 'cidade', 'UF', 'latitude', 'longitude', 'media_avaliacao', 'foto_perfil', 'foto_capa', 'foto_perfil_url', 'foto_capa_url', 'menor_preco', 'total_avaliacoes']
        read_only_fields = ['id', 'media_avaliacao', 'foto_perfil_url', 'foto_capa_url', 'menor_preco', 'total_avaliacoes']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=CentroEsportivo.objects.all(),
                fields=['nome', 'cidade', 'UF'],
                message="Já existe um centro esportivo com este nome neste local"
            )
        ]
        extra_kwargs = {
            'foto_perfil': {'write_only': True, 'required': False},
            'foto_capa': {'write_only': True, 'required': False}
        }
    #funções para retornar a url completa das fotos
    def get_foto_perfil_url(self, obj):
        request = self.context.get('request')
        if obj.foto_perfil and hasattr(obj.foto_perfil, 'url'):
            return request.build_absolute_uri(obj.foto_perfil.url)
        return None

    def get_foto_capa_url(self, obj):
        request = self.context.get('request')
        if obj.foto_capa and hasattr(obj.foto_capa, 'url'):
            return request.build_absolute_uri(obj.foto_capa.url)
        return None
    
    def get_menor_preco(self, obj):
        menor = Agenda.objects.filter(
            espacoesportivo__centro_esportivo=obj,
            status='ativo'
        ).aggregate(Min('preco'))['preco__min']
        
        return menor

    def get_total_avaliacoes(self, obj):
        from django.db.models import Q
        total = Reserva.objects.filter(
            Q(nota_atendimento__isnull=False) | 
            Q(nota_espacoesportivo__isnull=False) | 
            Q(nota_limpeza__isnull=False)
        ).filter(
            agenda__espacoesportivo__centro_esportivo=obj
        ).count()
        return total

#serializer para o espaço esportivo
class EspacoEsportivoSerializer(serializers.ModelSerializer):
    centro_esportivo_details = CentroEsportivoSerializer(source='centro_esportivo', read_only=True)
    centro_esportivo = serializers.PrimaryKeyRelatedField(queryset=CentroEsportivo.objects.all())
    foto_perfil_url = serializers.SerializerMethodField()
    foto_capa_url = serializers.SerializerMethodField()
    foto1_url = serializers.SerializerMethodField()
    foto2_url = serializers.SerializerMethodField()
    foto3_url = serializers.SerializerMethodField()
    foto4_url = serializers.SerializerMethodField()
    preco = serializers.SerializerMethodField()
    total_avaliacoes = serializers.SerializerMethodField()

    class Meta:
        model = EspacoEsportivo
        fields = ['id', 'nome', 'categoria', 'foto_perfil', 'foto_capa', 'foto_perfil_url', 'foto_capa_url','foto1', 'foto2', 'foto3', 'foto4', 'foto1_url', 'foto2_url', 'foto3_url', 'foto4_url', 'centro_esportivo', 'centro_esportivo_details', 'preco', 'total_avaliacoes']
        extra_kwargs = {
            'centro_esportivo': {'write_only': True},
            'foto_perfil': {'write_only': True, 'required': False},
            'foto_capa': {'write_only': True, 'required': False}
        }
        #validators para garantir que o nome do espaço esportivo seja único dentro do centro esportivo
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=EspacoEsportivo.objects.all(),
                fields=['nome', 'centro_esportivo'],
                message="Já existe um espaço esportivo com este nome neste centro esportivo."
            )
        ]

    def get_foto_perfil_url(self, obj):
        request = self.context.get('request')
        if obj.foto_perfil and hasattr(obj.foto_perfil, 'url'):
            return request.build_absolute_uri(obj.foto_perfil.url)
        return None

    def get_foto_capa_url(self, obj):
        request = self.context.get('request')
        if obj.foto_capa and hasattr(obj.foto_capa, 'url'):
            return request.build_absolute_uri(obj.foto_capa.url)
        return None
    
    def get_foto1_url(self, obj):
        request = self.context.get('request')
        if obj.foto1 and hasattr(obj.foto1, 'url'):
            return request.build_absolute_uri(obj.foto1.url)
        return None

    def get_foto2_url(self, obj):
        request = self.context.get('request')
        if obj.foto2 and hasattr(obj.foto2, 'url'):
            return request.build_absolute_uri(obj.foto2.url)
        return None

    def get_foto3_url(self, obj):
        request = self.context.get('request')
        if obj.foto3 and hasattr(obj.foto3, 'url'):
            return request.build_absolute_uri(obj.foto3.url)
        return None
        
    def get_foto4_url(self, obj):
        request = self.context.get('request')
        if obj.foto4 and hasattr(obj.foto4, 'url'):
            return request.build_absolute_uri(obj.foto4.url)
        return None

    def get_preco(self, obj):
        menor = Agenda.objects.filter(
            espacoesportivo=obj,
            status='ativo'
        ).aggregate(Min('preco'))['preco__min']
        
        return menor

    def get_total_avaliacoes(self, obj):
        from django.db.models import Q
        total = Reserva.objects.filter(
            Q(nota_atendimento__isnull=False) | 
            Q(nota_espacoesportivo__isnull=False) | 
            Q(nota_limpeza__isnull=False)
        ).filter(
            agenda__espacoesportivo=obj
        ).count()
        return total


class AgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agenda
        fields = '__all__'
    #validação para garantir que o horário final seja posterior ao horário inicial e que não haja sobreposição de horários na agenda
    def validate(self, data):
        if data['h_inicial'] >= data['h_final']:
            raise serializers.ValidationError(
                {"h_final": "O horário final deve ser posterior ao horário inicial."}
            )
        existe_sobreposicao = Agenda.objects.filter(
            espacoesportivo=data['espacoesportivo'],
            dia=data['dia'],
            h_inicial__lt=data['h_final'],
            h_final__gt=data['h_inicial']
        )
        if existe_sobreposicao.exists():
            raise serializers.ValidationError(
                "O horário informado entra em conflito com um agendamento já existente."
            )
        return data

#serializer para a reserva, com validação para garantir que o organizador não tenha uma reserva duplicada para o mesmo horário
class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        exclude = ['organizador']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Reserva.objects.all(),
                fields=['agenda'],
                message="Já existe uma reserva para este organizador neste horário."
            )
        ]

#serializer para o centro esportivo com seus espaços esportivos
class Centro_com_espacosSerializer(serializers.ModelSerializer):
    foto_perfil_url = serializers.SerializerMethodField()
    foto_capa_url = serializers.SerializerMethodField()
    menor_preco = serializers.SerializerMethodField()
    total_avaliacoes = serializers.SerializerMethodField()
    espacos = EspacoEsportivoSerializer(many=True, read_only=True)

    class Meta:
        model = CentroEsportivo
        fields = ['id', 'nome', 'descricao', 'cidade', 'UF', 'espacos', 'foto_perfil_url', 'foto_capa_url', 'menor_preco', 'total_avaliacoes', 'media_avaliacao']

    def get_foto_perfil_url(self, obj):
        request = self.context.get('request')
        if obj.foto_perfil and hasattr(obj.foto_perfil, 'url'):
            return request.build_absolute_uri(obj.foto_perfil.url)
        return None

    def get_foto_capa_url(self, obj):
        request = self.context.get('request')
        if obj.foto_capa and hasattr(obj.foto_capa, 'url'):
            return request.build_absolute_uri(obj.foto_capa.url)
        return None

    def get_menor_preco(self, obj):
        menor = Agenda.objects.filter(
            espacoesportivo__centro_esportivo=obj,
            status='ativo'
        ).aggregate(Min('preco'))['preco__min']
        
        return menor

    def get_total_avaliacoes(self, obj):
        from django.db.models import Q
        total = Reserva.objects.filter(
            Q(nota_atendimento__isnull=False) | 
            Q(nota_espacoesportivo__isnull=False) | 
            Q(nota_limpeza__isnull=False)
        ).filter(
            agenda__espacoesportivo__centro_esportivo=obj
        ).count()
        return total

#serializer para a agenda detalhada (não usado por enquanto)
class AgendaDetalhadaSerializer(serializers.ModelSerializer):
    espacoesportivo = EspacoEsportivoSerializer(read_only=True)

    class Meta:
        model = Agenda
        fields = ['id', 'dia', 'h_inicial', 'h_final', 'preco', 'espacoesportivo']

#serializer para a reserva detalhada, serve para o minhas reservas, porque mostra a reserva junto com detalhes da agenda
class ReservaDetalhadaSerializer(serializers.ModelSerializer):
    agenda = AgendaDetalhadaSerializer(read_only=True)

    class Meta:
        model = Reserva
        fields = '__all__'

#serializer para os horários disponíveis
class HorarioDisponivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agenda
        fields = ['id', 'dia', 'h_inicial', 'h_final', 'preco']


#serializer para o dashboard do gerente, vai colocar informações resumidas das reservas (nao usado por enquanto)
class DashboardGerenteSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    organizador = serializers.SerializerMethodField()
    espaco = serializers.SerializerMethodField()
    check_in = serializers.SerializerMethodField()
    cancelamento = serializers.SerializerMethodField()
    comprovante = serializers.SerializerMethodField()
    valor_pagamento = serializers.SerializerMethodField()
    data_pagamento = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = ['id', 'status', 'organizador', 'espaco', 'check_in', 'cancelamento', 'comprovante', 'valor_pagamento', 'data_pagamento']

    def get_organizador(self, obj):
        return obj.organizador.nome_completo

    def get_espaco(self, obj):
        # Retorna apenas o nome para evitar lista/tupla na resposta JSON
        return obj.agenda.espacoesportivo.nome

    def get_check_in(self, obj):
        data_formatada = obj.agenda.dia.strftime('%d/%m/%Y')
        hora_formatada = obj.agenda.h_inicial.strftime('%H:%M')
        return f"{data_formatada} {hora_formatada}"

    def get_cancelamento(self, obj):
        if obj.cancelar_reserva:
            return obj.cancelar_reserva.strftime('%d/%m/%Y %H:%M')
        return None

    def get_comprovante(self, obj):
        pagamento = getattr(obj, 'pagamento', None)
        if pagamento and pagamento.comprovante:
            request = self.context.get('request')
            url = pagamento.comprovante.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_valor_pagamento(self, obj):
        pagamento = getattr(obj, 'pagamento', None)
        if pagamento:
            return str(pagamento.valor)
        return None

    def get_data_pagamento(self, obj):
        pagamento = getattr(obj, 'pagamento', None)
        if pagamento:
            return pagamento.data_pagamento.strftime('%d/%m/%Y %H:%M')
        return None
#serializer para o pagamento
class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'
        read_only_fields = ['data_pagamento', 'confirmado']