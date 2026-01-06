import os
import django
import random
from datetime import timedelta, time, date
from io import BytesIO

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserva.settings')
django.setup()

from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from faker import Faker
from PIL import Image, ImageDraw, ImageFont  # Requer Pillow instalado

from reservaapp.models import CentroEsportivo, EspacoEsportivo, Agenda, Reserva, Pagamento

fake = Faker('pt_BR')
User = get_user_model()

# Cores para gerar imagens dinâmicas
CORES = [
    (52, 152, 219),   # Azul
    (231, 76, 60),    # Vermelho
    (46, 204, 113),   # Verde
    (241, 196, 15),   # Amarelo
    (155, 89, 182),   # Roxo
    (52, 73, 94),     # Cinza Escuro
    (230, 126, 34),   # Laranja
]

def limpar_banco():
    print("🧹 Limpando banco de dados antigo...")
    Pagamento.objects.all().delete()
    Reserva.objects.all().delete()
    Agenda.objects.all().delete()
    EspacoEsportivo.objects.all().delete()
    CentroEsportivo.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete() # Mantém seu superuser se houver
    print("✨ Banco limpo!")


def criar_superuser():
    print("👑 Verificando superusuário...")
    # Verifica se já existe alguém com esse email ou se já há algum superuser
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@admin.com',
            password='123456', # Mesma senha dos outros para facilitar
            nome_completo='Administrador do Sistema',
            cpf='000.000.000-00', # CPF fictício para passar na validação
            tipo='gerente' # Define um tipo padrão para não quebrar regras do model
        )
        print("   -> Superusuário criado: admin@admin.com / 123456")
    else:
        print("   -> Superusuário já existe (mantido).")

def gerar_imagem_fake(texto, largura=800, altura=600):
    """Gera um arquivo de imagem real usando Pillow"""
    cor = random.choice(CORES)
    image = Image.new('RGB', (largura, altura), color=cor)
    draw = ImageDraw.Draw(image)
    
    # Tenta centralizar um texto simples (sem carregar fontes externas para evitar erro)
    # Apenas desenha um retângulo mais claro no meio para simular conteúdo
    draw.rectangle(
        [(largura//4, altura//4), (largura*3//4, altura*3//4)], 
        outline=(255, 255, 255), 
        width=5
    )
    
    thumb_io = BytesIO()
    image.save(thumb_io, format='JPEG', quality=85)
    
    # Cria um nome de arquivo seguro
    nome_arquivo = f"{texto.lower().replace(' ', '_')}_{random.randint(1, 1000)}.jpg"
    return ContentFile(thumb_io.getvalue(), name=nome_arquivo)

def criar_usuarios():
    print("👤 Criando usuários...")
    usuarios = []

    # 1. Gerente Principal (Fácil de lembrar)
    gerente_principal = User.objects.create_user(
        username='gerente',
        email='gerente@teste.com',
        password='12345678', # Senha padrão
        tipo='gerente',
        nome_completo='Gerente da Silva',
        cpf=fake.unique.cpf()
    )
    usuarios.append(gerente_principal)
    print(f"   -> Gerente criado: gerente@teste.com / 12345678")

    # 2. Organizador Principal (Fácil de lembrar)
    organizador_principal = User.objects.create_user(
        username='organizador',
        email='organizador@teste.com',
        password='12345678', # Senha padrão
        tipo='organizador',
        nome_completo='Organizador Oliveira',
        cpf=fake.unique.cpf()
    )
    usuarios.append(organizador_principal)
    print(f"   -> Organizador criado: organizador@teste.com / 12345678")

    # 3. Usuários Aleatórios extras
    for _ in range(5):
        u = User.objects.create_user(
            username=fake.user_name(),
            email=fake.unique.email(),
            password='12345678',
            tipo='organizador',
            nome_completo=fake.name(),
            cpf=fake.unique.cpf()
        )
        usuarios.append(u)
    
    return usuarios

def criar_centros(usuario_gerente):
    print("imóveis🏢 Criando centros esportivos...")
    centros_data = [
        {
            "nome": "AABB Natal",
            "descricao": "Associação Atlética Banco do Brasil. O melhor clube da cidade com estrutura completa.",
            "cidade": "Natal", "UF": "RN",
            "lat": -5.795, "lon": -35.206
        },
        {
            "nome": "Arena das Dunas",
            "descricao": "Estádio multiuso padrão FIFA. Palco de grandes emoções.",
            "cidade": "Natal", "UF": "RN",
            "lat": -5.819, "lon": -35.206
        },
        {
            "nome": "SESC Ponta Negra",
            "descricao": "Lazer e esporte com vista para o mar.",
            "cidade": "Natal", "UF": "RN",
            "lat": -5.793, "lon": -35.211
        },
        {
            "nome": "Complexo Esportivo IFRN",
            "descricao": "Estrutura de ponta para a comunidade acadêmica e externa.",
            "cidade": "Natal", "UF": "RN",
            "lat": -5.808, "lon": -35.221
        }
    ]

    centros_objs = []
    for info in centros_data:
        # Gera imagens na hora
        img_perfil = gerar_imagem_fake(f"perfil_{info['nome']}", 400, 400)
        img_capa = gerar_imagem_fake(f"capa_{info['nome']}", 1200, 400)

        centro = CentroEsportivo.objects.create(
            nome=info["nome"],
            descricao=info["descricao"],
            latitude=info["lat"],
            longitude=info["lon"],
            cidade=info["cidade"],
            UF=info["UF"],
            gerente=usuario_gerente,
            foto_perfil=img_perfil,
            foto_capa=img_capa
        )
        centros_objs.append(centro)
    
    return centros_objs

def criar_espacos(centros):
    print("⚽ Criando espaços esportivos...")
    categorias = ['futebol', 'volei', 'basquete', 'tenis', 'futsal', 'natação']
    espacos_objs = []

    for centro in centros:
        # Cria 3 a 5 espaços por centro
        qtd_espacos = random.randint(3, 5)
        for i in range(qtd_espacos):
            categoria = random.choice(categorias)
            nome_espaco = f"{categoria.capitalize()} - Quadra {i+1}"
            
            img_espaco = gerar_imagem_fake(f"espaco_{centro.nome}_{i}", 800, 600)

            espaco = EspacoEsportivo.objects.create(
                nome=nome_espaco,
                categoria=categoria,
                centro_esportivo=centro,
                foto_perfil=img_espaco,
                foto_capa=img_espaco # Reusando para simplificar, ou gere outra
            )
            espacos_objs.append(espaco)
    
    return espacos_objs

def criar_agendas(espacos):
    print("📅 Criando agendas (30 dias)...")
    agendas_objs = []
    hoje = timezone.now().date()
    
    for espaco in espacos:
        # Agenda para os próximos 30 dias
        for i in range(30):
            dia = hoje + timedelta(days=i)
            
            # Pula domingos aleatoriamente (simulando folga)
            if dia.weekday() == 6 and random.choice([True, False]):
                continue

            # Cria horários das 08:00 às 22:00
            for h in range(8, 22, 2):
                # 20% de chance de um horário não existir (buraco na agenda)
                if random.random() > 0.8:
                    continue

                agenda = Agenda.objects.create(
                    preco=random.choice([80.00, 100.00, 120.00, 150.00, 200.00]),
                    dia=dia,
                    h_inicial=time(hour=h),
                    h_final=time(hour=h+2),
                    espacoesportivo=espaco,
                    status='ativo'
                )
                agendas_objs.append(agenda)
    
    return agendas_objs

def criar_reservas(agendas, organizadores):
    print("🎟️ Criando reservas aleatórias...")
    # Reserva 30% das agendas disponíveis
    agendas_para_reservar = random.sample(agendas, k=int(len(agendas) * 0.3))
    
    for agenda in agendas_para_reservar:
        user = random.choice(organizadores)
        
        # Atualiza o status da agenda
        agenda.status = 'indisponível' # Ou o status que seu sistema usa quando reservado
        agenda.save()

        status = random.choice(['pago', 'pendente', 'pendente'])  # Mais pendentes
        reserva = Reserva.objects.create(
            organizador=user,
            agenda=agenda,
            status=status,
            criado_em=timezone.now(),
            nota_atendimento=random.randint(4, 5), # Notas altas para ficar bonito
            nota_espacoesportivo=random.randint(4, 5),
            nota_limpeza=random.randint(4, 5),
            comentario_avaliacao=fake.sentence()
        )
        
        # Cria um pagamento para a reserva com 70% de chance de ter comprovante
        tem_comprovante = random.random() > 0.3
        comprovante_img = None
        if tem_comprovante:
            comprovante_img = gerar_imagem_fake(f"comprovante_reserva_{reserva.id}", 600, 800)
        
        Pagamento.objects.create(
            reserva=reserva,
            valor=agenda.preco,
            data_pagamento=timezone.now() - timedelta(days=random.randint(0, 5)),
            confirmado=(status == 'pago'),
            comprovante=comprovante_img
        )

def run():
    # 1. Limpeza
    limpar_banco()

    criar_superuser() 

    # 2. Criação
    usuarios = criar_usuarios()
    # Pega o gerente principal que criamos (índice 0)
    gerente_principal = usuarios[0]
    # Pega os organizadores (todos menos o gerente)
    organizadores = usuarios[1:]

    centros = criar_centros(gerente_principal)
    espacos = criar_espacos(centros)
    agendas = criar_agendas(espacos)
    criar_reservas(agendas, organizadores)

    print("\n✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!")
    print("------------------------------------------------")
    print(f"Centros criados: {len(centros)}")
    print(f"Espaços criados: {len(espacos)}")
    print(f"Agendas criadas: {len(agendas)}")
    print("------------------------------------------------")
    print("🔑 CREDENCIAIS PARA TESTE:")
    print("Gerente:     gerente@teste.com     / 12345678")
    print("Organizador: organizador@teste.com / 12345678")
    print("------------------------------------------------")

if __name__ == '__main__':
    run()