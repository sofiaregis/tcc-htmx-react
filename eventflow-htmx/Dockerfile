FROM python:3.12-slim

# Evitar escrita de arquivos .pyc e forçar stdout/stderr sem buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# Instalar dependências de sistema mínimas para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte da aplicação
COPY . /app/

# Expor portas (8080 padrão do experimento e 8000 alternativa)
EXPOSE 8080 8000

# Comando padrão de execução sem reloader para estabilidade temporal
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080", "--noreload"]
