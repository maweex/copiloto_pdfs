# ---- Base: Python 3.11 slim (ligero y suficiente para compilar chroma deps)
FROM python:3.11-slim

# Evitar buffers y cache de pip
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependencias del sistema necesarias (build de wheels como hnswlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements primero (mejora la cache de Docker)
COPY requirements.txt /app/requirements.txt

# Instalar dependencias de Python
RUN pip install -r requirements.txt

# Copiar el resto del código de la app
COPY . /app

# Streamlit: exponer y configurar puerto
EXPOSE 8501
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Apuntar LangChain/Ollama al servicio "ollama" (cuando uses docker-compose)
ENV OLLAMA_HOST=http://ollama:11434
ENV OLLAMA_BASE_URL=http://ollama:11434

# Si usas persistencia de Chroma, la activas con variable de entorno desde compose:
# ENV CHROMA_PERSIST_DIR=/app/chroma_db

# Comando de arranque de la app
CMD ["streamlit", "run", "app.py", "--server.headless=true", "--server.address=0.0.0.0", "--server.port=8501"]
