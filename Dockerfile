# Dockerfile optimizado para producción de RAG-HR-Frontend
# Esta app es un frontend Python/Streamlit, no necesita Nginx o Node para servir estáticos.
# La imagen se construye con un stage de dependencias y un stage final más limpio.

FROM python:3.10-slim AS builder

LABEL maintainer="DevOps Team"
LABEL description="RAG HR Frontend - Streamlit app para Azure Container Apps"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

ARG CACHE_BUST=0
RUN echo "cache-bust: ${CACHE_BUST}"
COPY . .

FROM python:3.10-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--logger.level=info"]
