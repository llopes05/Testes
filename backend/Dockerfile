# Imagem base
FROM python:3.12-slim

# Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para psycopg2, pois usamos a slim
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos
COPY requirements.txt /app/

# Instala as dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia o código da aplicação
COPY . /app/

# Cria o script de entrada das migrações e inicialização do Gunicorn
RUN echo '#!/bin/sh\n\
python manage.py makemigrations\n\
python manage.py migrate\n\
python manage.py collectstatic --noinput\n\
exec gunicorn reserva.wsgi:application --bind 0.0.0.0:8000' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Expõe a porta 8000
EXPOSE 8000

# Define o comando de entrada
ENTRYPOINT ["/app/entrypoint.sh"]
