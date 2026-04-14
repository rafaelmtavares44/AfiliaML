# =============
# Dockerfile
# =============
FROM python:3.11-slim-bookworm

WORKDIR /app

# Instalar dependências de sistema para compilação (scikit-learn precisa)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Variáveis de ambiente
ENV ENV=production
ENV PORT=3333
ENV PYTHONPATH=/app

# Expor porta
EXPOSE 3333

# Comando para rodar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3333"]
