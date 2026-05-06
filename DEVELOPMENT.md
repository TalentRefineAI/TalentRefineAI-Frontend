# 🚀 Guía de Desarrollo - RAG HR Frontend

Guía completa para desarrolladores que trabajen con el Frontend RAG HR.

## 📋 Tabla de Contenidos

1. [Arquitectura](#arquitectura)
2. [Estándares de Código](#estándares-de-código)
3. [Estructura de Carpetas](#estructura-de-carpetas)
4. [Convenciones de Naming](#convenciones-de-naming)
5. [Desarrollo de Componentes](#desarrollo-de-componentes)
6. [Integración con API](#integración-con-api)
7. [Testing](#testing)
8. [Deploy](#deploy)

## 🏗️ Arquitectura

La aplicación sigue una arquitectura modular en capas:

```
┌─────────────────────────────────────┐
│        Streamlit UI (app.py)        │  Capa de presentación
├─────────────────────────────────────┤
│     Components (upload, query,       │  Capa de componentes
│      results, etc.)                 │
├─────────────────────────────────────┤
│        Utils (API Client, Mocks)    │  Capa de servicios
├─────────────────────────────────────┤
│       FastAPI Backend (Fase 2)      │  API externa
└─────────────────────────────────────┘
```

## 📐 Estándares de Código

### Python Style Guide

Seguimos **PEP 8** con las siguientes consideraciones:

```python
# ✓ Bueno
def calculate_candidate_score(experience_years: int, skills: List[str]) -> float:
    """Calcula el score de un candidato basado en experiencia y habilidades."""
    base_score = experience_years * 10
    skill_bonus = len(skills) * 5
    return base_score + skill_bonus


# ✗ Malo
def calc(y, s):
    return y * 10 + len(s) * 5
```

### Docstrings

Usar formato Google Docstring:

```python
def upload_cv_documents(files: List[bytes], filenames: List[str]) -> Dict[str, Any]:
    """
    Sube documentos CV a la API para procesamiento.
    
    Args:
        files (List[bytes]): Lista de contenidos de archivos
        filenames (List[str]): Lista de nombres de archivos
        
    Returns:
        Dict[str, Any]: Respuesta de la API con IDs de documentos
        
    Raises:
        ValueError: Si no hay archivos o están vacíos
        ConnectionError: Si falla la conexión a la API
    """
```

### Type Hints

Siempre incluir type hints en funciones:

```python
from typing import List, Dict, Optional, Tuple, Any

def process_query(query: str, limit: int = 10) -> Tuple[List[Dict], float]:
    """..."""
```

## 📁 Estructura de Carpetas

```
RAG-HR-Frontend/
├── app.py                          # Punto de entrada principal
├── requirements.txt                # Dependencias
├── Dockerfile                      # Configuración Docker
├── docker-compose.yml              # Orquestación
├── Makefile                        # Automatización
├── README.md                       # Documentación principal
├── DEVELOPMENT.md                  # Este archivo
├── CHANGELOG.md                    # Historial de cambios
│
├── .streamlit/
│   └── config.toml                # Configuración de Streamlit
│
├── components/                     # Componentes reutilizables
│   ├── __init__.py
│   ├── upload_view.py             # Vista de subida
│   ├── query_view.py              # Vista de búsqueda
│   └── results_view.py            # Vista de resultados
│
├── utils/                          # Utilidades
│   ├── __init__.py
│   ├── api_client.py              # Cliente HTTP
│   └── mock_data.py               # Datos simulados
│
├── tests/                          # Tests (Fase 2)
│   ├── __init__.py
│   ├── test_api_client.py
│   ├── test_components.py
│   └── test_integration.py
│
└── docs/                           # Documentación adicional (Fase 2)
    ├── API.md
    ├── DEPLOYMENT.md
    └── TROUBLESHOOTING.md
```

## 🏷️ Convenciones de Naming

### Variables y Funciones

```python
# ✓ Bueno
candidate_score = 95
total_results = 5
def render_candidate_card(candidate: Dict) -> None:
    pass

# ✗ Malo
candidateScore = 95
TR = 5
def rc(c):
    pass
```

### Componentes y Vistas

```python
# Funciones que renderizan deben empezar con render_
def render_upload_view():
    pass

def render_query_view():
    pass

# Funciones privadas (internas) empiezan con _
def _process_files(uploaded_files):
    pass

def _get_score_color(score: int) -> str:
    pass
```

### Constantes

```python
# En mayúsculas y con guiones bajos
MAX_FILE_SIZE = 26214400  # 25 MB
DEFAULT_EXPERIENCE_MIN = 0
DEFAULT_EXPERIENCE_MAX = 20
API_TIMEOUT = 30
```

## 🧩 Desarrollo de Componentes

### Crear un Nuevo Componente

1. Crear archivo en `components/`
2. Implementar función `render_<name>_view()`
3. Añadir función en `app.py`

**Ejemplo: Nueva vista de reportes**

```python
# components/reports_view.py
import streamlit as st
from typing import Dict, List

def render_reports_view():
    """Renderiza la vista de reportes y análisis."""
    st.header("📊 Reportes y Análisis")
    
    # Implementar lógica aquí
    st.info("Vista de reportes en construcción")


# Luego en app.py, agregar en _render_main_content():
elif page == "📊 Reportes":
    from components.reports_view import render_reports_view
    render_reports_view()
```

### Mejores Prácticas en Componentes

```python
import streamlit as st
from typing import Dict, List, Optional

def render_example_view():
    """
    Renderiza una vista de ejemplo.
    
    Sigue estas prácticas:
    1. Documentar con docstring
    2. Usar type hints
    3. Separar lógica de presentación
    4. Usar st.session_state para estado
    5. Manejar excepciones gracefully
    6. Mostrar feedback visual al usuario
    """
    
    # 1. Header y descripción
    st.header("🎯 Título de la Vista")
    st.markdown("Descripción breve de qué hace esta vista")
    
    # 2. Dividers visuales
    st.divider()
    
    # 3. Formularios validados
    with st.form(key="example_form"):
        input_value = st.text_input("Etiqueta", placeholder="Placeholder")
        submit = st.form_submit_button("Enviar")
    
    # 4. Manejo de estado
    if submit:
        if not input_value.strip():
            st.error("⚠️ El campo es requerido")
            return
        
        # 5. Feedback visual
        st.success("✅ Éxito")
    
    # 6. Secciones expandibles para detalles
    with st.expander("📋 Más Información"):
        st.write("Detalles adicionales...")
```

## 🔌 Integración con API

### Cliente API (Phase 1 - Mocks)

```python
from utils.api_client import get_api_client

# Usar mocks en desarrollo
api_client = get_api_client(use_mock=True)
results = api_client.query_rag(query="...", experience_min=5)
```

### Migración a API Real (Fase 2)

```python
# En .env
USE_MOCK_DATA=False
API_URL=http://api.production.com

# En app.py
api_client = get_api_client(use_mock=False)
```

### Añadir Nuevo Endpoint

1. Actualizar `RAGAPIClient` en `utils/api_client.py`:

```python
def new_endpoint(self, param: str) -> Dict[str, Any]:
    """Nueva funcionalidad."""
    if self.use_mock:
        return {"status": "success", "data": []}
    
    try:
        url = f"{self.base_url}/api/v1/new-endpoint"
        response = self.session.post(url, json={"param": param})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
```

2. Usar en componentes:

```python
api_client = get_api_client()
result = api_client.new_endpoint("value")
```

## 🧪 Testing (Fase 2)

### Estructura de Tests

```
tests/
├── __init__.py
├── test_api_client.py       # Tests del cliente API
├── test_components.py       # Tests de componentes
├── test_integration.py      # Tests de integración
└── conftest.py             # Fixtures compartidas
```

### Ejemplo de Test

```python
import pytest
from utils.api_client import RAGAPIClient

@pytest.fixture
def api_client():
    return RAGAPIClient(use_mock=True)

def test_query_rag_returns_candidates(api_client):
    """Verifica que query_rag retorna candidatos."""
    result = api_client.query_rag(query="developer")
    
    assert result["status"] == "success"
    assert len(result["candidates"]) > 0
    assert "name" in result["candidates"][0]

def test_query_rag_with_filters(api_client):
    """Verifica que los filtros funcionan."""
    result = api_client.query_rag(
        query="test",
        experience_min=5,
        locations=["Madrid"]
    )
    
    for candidate in result["candidates"]:
        assert candidate["experience_years"] >= 5
        assert candidate["location"] in ["Madrid"]
```

### Ejecutar Tests

```bash
pytest tests/ -v                    # Ejecutar todos
pytest tests/test_api_client.py -v # Archivo específico
pytest -k "test_query" -v          # Tests que coincidan
pytest --cov=utils tests/          # Con cobertura
```

## 🚀 Deploy

### Deploy Local

```bash
# Opción 1: Directo con Streamlit
source venv/bin/activate
streamlit run app.py

# Opción 2: Con Docker
docker build -t rag-hr-frontend:latest .
docker run -p 8501:8501 rag-hr-frontend:latest

# Opción 3: Con Docker Compose
docker-compose up
```

### Deploy en Servidor (Fase 2)

```bash
# 1. SSH al servidor
ssh user@server.com

# 2. Clonar repositorio
git clone https://github.com/org/rag-hr-frontend.git
cd rag-hr-frontend

# 3. Usar docker-compose en producción
docker-compose -f docker-compose.prod.yml up -d

# 4. Configurar Nginx como reverse proxy (opcional)
# Ver docs/DEPLOYMENT.md
```

## 🔍 Debugging

### Logs en Streamlit

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Información")
logger.warning("Advertencia")
logger.error("Error")
```

### Usar st.write() para Debug

```python
st.write("Debug:", variable)
st.json({"key": "value"})
```

### Inspeccionar Session State

```python
st.write("Session State:")
st.write(st.session_state)
```

## 📚 Recursos Útiles

- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Components](https://docs.streamlit.io/library/components)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

## 👥 Contribuir

1. Crear rama desde `main`: `git checkout -b feature/mi-feature`
2. Hacer cambios y commits
3. Push a la rama: `git push origin feature/mi-feature`
4. Crear Pull Request
5. Esperar review y aprobación

## 📞 Contacto

Preguntas o sugerencias: support@example.com
