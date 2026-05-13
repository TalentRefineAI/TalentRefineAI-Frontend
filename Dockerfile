# Dockerfile para RAG HR Frontend
# Construir: docker build -t rag-hr-frontend:latest .
# Ejecutar: docker run -p 8501:8501 rag-hr-frontend:latest

# Etapa base: Python 3.10 slim
FROM python:3.10-slim AS base

# Metadatos
LABEL maintainer="DevOps Team"
LABEL version="1.0.0"
LABEL description="RAG HR Frontend - Aplicación de Selección de Personal Inteligente"

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Directorio de trabajo
WORKDIR /app

# ============================================================================
# Etapa de construcción: Instalar dependencias
# ============================================================================
FROM base AS builder

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Crear virtualenv y instalar dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

# ============================================================================
# Etapa final: Imagen de producción
# ============================================================================
FROM base AS production

# Copiar virtualenv desde builder
COPY --from=builder /opt/venv /opt/venv

# Establecer PATH para usar venv
ENV PATH="/opt/venv/bin:$PATH"

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app

# Cambiar al usuario no-root
USER streamlit

# Copiar solo el código necesario para ejecutar Streamlit
COPY --chown=streamlit:streamlit app.py .
COPY --chown=streamlit:streamlit components ./components
COPY --chown=streamlit:streamlit utils ./utils
COPY --chown=streamlit:streamlit test_queries.json .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=5)" || exit 1

# Configuración de Streamlit
RUN mkdir -p ~/.streamlit && \
    echo "[client]\n" \
         "showErrorDetails = true\n" \
         "toolbarMode = \"minimal\"\n" \
         "[logger]\n" \
         "level = \"info\"\n" \
         "[server]\n" \
         "headless = true\n" \
         "runOnSave = true\n" \
         "port = 8501\n" \
         "maxUploadSize = 200\n" \
         > ~/.streamlit/config.toml

# Exponer puerto
EXPOSE 8501

# Comando de inicio
CMD ["streamlit", "run", "app.py", "--logger.level=info"]
