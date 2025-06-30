FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements primeiro para cache de layer
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Baixa modelo spacy para português (opcional, se disponível)
RUN python -m spacy download pt_core_news_sm || echo "Modelo spacy não disponível, usando fallback"

# Baixa dados do NLTK
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" || echo "NLTK data download failed"

# Copia código da aplicação
COPY app/ ./app/

# Expõe porta
EXPOSE 8000

# Define variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 