from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

TIPOS_USUARIO = (
    ('gerente', 'Gerente'),
    ('organizador', 'Organizador'),
)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_USUARIO)
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'tipo', 'nome_completo', 'cpf']

    def __str__(self):
        return self.email

class CentroEsportivo(models.Model):
    TIPOS_UF=(
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins')
    )
    foto_perfil = models.ImageField(upload_to='centros_perfil/', blank=True, null=True)
    foto_capa = models.ImageField(upload_to='centros_capa/', blank=True, null=True)
    nome = models.CharField(max_length=64)
    descricao = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    longitude = models.DecimalField(max_digits=12, decimal_places=8)
    cidade = models.CharField(max_length=64)
    UF = models.CharField(max_length=2, choices=TIPOS_UF)
    media_avaliacao = models.DecimalField(max_digits=2, decimal_places=1, blank=True, default=0)
    #recursos_adicionais = models.TextField(blank=True, null=True) //Decidir se irá virar uma tabela ou um dicionario 
    #perguntas_respostas = models.TextField(blank=True, null=True)// Precisa explorar
    gerente = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'tipo': 'gerente'}, related_name="centros_esportivos")

    def __str__(self):
        return self.nome

class EspacoEsportivo(models.Model):
    CATEGORIA_CHOICES = (
        ('futebol', 'Futebol'),
        ('volei', 'Vôlei'),
        ('basquete', 'Basquete'),
        ('tenis', 'Tênis'),
        ('futsal', 'Futsal'),
        ('atletismo', 'Atletismo'),
        ('outros', 'Outros'),
        ('natação', 'Natação'),
        ('ginástica', 'Ginástica')
    )
    nome = models.CharField(max_length=255)
    foto_perfil = models.ImageField(upload_to='espacos_perfil/', blank=True, null=True)
    foto_capa = models.ImageField(upload_to='espacos_capa/', blank=True, null=True)
    foto1= models.ImageField(upload_to='espacos_foto1/', blank=True, null=True)
    foto2= models.ImageField(upload_to='espacos_foto2/', blank=True, null=True)
    foto3= models.ImageField(upload_to='espacos_foto3/', blank=True, null=True)
    foto4= models.ImageField(upload_to='espacos_foto4/', blank=True, null=True)
    categoria = models.CharField(max_length=100, choices=CATEGORIA_CHOICES)
    centro_esportivo = models.ForeignKey(CentroEsportivo, on_delete=models.CASCADE, related_name="espacos")

    def __str__(self):
        return f"EspacoEsportivo {self.nome}"

class Agenda(models.Model):
    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("indisponível", "Indisponível"),
    ]
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    dia = models.DateField()
    h_inicial = models.TimeField()
    h_final = models.TimeField()
    espacoesportivo = models.ForeignKey(EspacoEsportivo, on_delete=models.CASCADE, related_name="agenda")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="ativo")

    def __str__(self):
        return f"{self.espacoesportivo.centro_esportivo.nome} | {self.espacoesportivo.nome} - {self.dia} ({self.h_inicial}-{self.h_final}) - {self.status}"

class Reserva(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("pago", "Pago"),
        ("cancelada", "Cancelada"),
    ]
    organizador = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'tipo': 'organizador'})
    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE)
    nota_atendimento = models.IntegerField(null=True, blank=True)
    nota_espacoesportivo = models.IntegerField(null=True, blank=True)
    nota_limpeza = models.IntegerField(null=True, blank=True)
    comentario_avaliacao = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pendente")
    cancelar_reserva=models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reserva de {self.organizador.nome_completo} - {self.agenda.dia} ({self.status})"

class Pagamento(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name="pagamento")
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateTimeField(default=timezone.now)
    confirmado = models.BooleanField(default=False)
    comprovante=models.ImageField(upload_to='comprovantes/', blank=True, null=True)

    def __str__(self):
        return f"Pagamento de {self.valor} para {self.reserva}"

