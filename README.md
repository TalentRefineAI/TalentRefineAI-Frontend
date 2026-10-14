# TalentRefineAI-Frontend

Frontend de **TalentRefine AI**, plataforma de reclutamiento inteligente que permite subir CVs en PDF y buscar candidatos mediante lenguaje natural, con resultados clasificados por un score híbrido (semántico + LLM).

Construido con **Streamlit 1.30** y desplegado en Azure Container Apps.

---

## Funcionalidades

| Vista | Descripción |
|-------|-------------|
| **Subida de CVs** | Carga múltiples PDFs con Drag & Drop; seguimiento de estado por documento ("en proceso" vs indexado); panel de candidatos indexados; botón de borrado global |
| **Búsqueda** | Consulta semántica libre + filtros (experiencia mínima, ubicación con tags custom, habilidades con tags custom); 5 ejemplos de consulta predefinidos |
| **Resultados** | Candidatos ordenados por score híbrido con resumen, justificación y datos de contacto del LLM; descarga de PDF; generación de reporte |

---

## Estructura del proyecto

```
TalentRefineAI-Frontend/
├── app.py                    # Punto de entrada: navegación, session state, layout
├── Dockerfile
├── requirements.txt
├── components/
│   ├── upload_view.py        # Vista de subida y gestión de CVs
│   ├── query_view.py         # Vista de búsqueda con filtros y tags custom
│   └── results_view.py       # Vista de resultados y tarjetas de candidatos
└── utils/
    ├── api_client.py         # Cliente HTTP hacia ingest-service y rag-service
    └── mock_data.py          # Datos simulados para desarrollo local sin backend
```

---

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `BACKEND_BASE_URL` | URL base del ingest-service | `http://localhost:8000` |
| `RAG_SERVICE_URL` | URL base del rag-service | `http://localhost:8001` |
| `USE_MOCK_DATA` | Usar datos simulados sin backend real | `false` |

En producción estos valores se inyectan como env vars en la Container App.

---

## Desarrollo local

### Con backend real (docker-compose)

```bash
# Desde la raíz del repositorio backend:
docker compose -f docker-compose.local-fake.yml up --build

# Luego en el repositorio frontend:
cd TalentRefineAI-Frontend
pip install -r requirements.txt
BACKEND_BASE_URL=http://localhost:8000 RAG_SERVICE_URL=http://localhost:8001 streamlit run app.py
```

### Sin backend (modo mock)

```bash
pip install -r requirements.txt
USE_MOCK_DATA=true streamlit run app.py
```

La aplicación se abre en `http://localhost:8501`.

---

## Dockerización

```bash
docker build -t rag-hr-frontend:local .
docker run -p 8501:8501 \
  -e BACKEND_BASE_URL=http://host.docker.internal:8000 \
  -e RAG_SERVICE_URL=http://host.docker.internal:8001 \
  rag-hr-frontend:local
```

---

## Despliegue en producción

Ver `OPERATIONS.md` en el repositorio backend para el flujo completo de build y deploy.

```bash
ACR=crtalentrefinedevspc
RG=rg-talentrefine-dev-spc

az acr build --registry $ACR \
  --image rag-hr-frontend:latest \
  --file Dockerfile . \
  --resource-group $RG

az containerapp update \
  --name ca-frontend-talentrefine-dev-spc \
  --resource-group $RG \
  --image $ACR.azurecr.io/rag-hr-frontend:latest \
  --revision-suffix v$(date +%Y%m%d)
```

---

## Session state keys principales

| Key | Tipo | Descripción |
|-----|------|-------------|
| `last_search` | `dict` | Parámetros de la última búsqueda + flag `should_search` |
| `_searching` | `bool` | `True` mientras la búsqueda está en curso; deshabilita el botón Buscar y activa el `st.status` en la vista de resultados |
| `_results_cache` | `dict` | Respuesta cacheada del rag-service para la última consulta |
| `_results_cache_key` | `str` | Clave derivada de los parámetros de búsqueda para invalidación de caché |
| `_page` | `str` | Página activa: `"Subida de CVs"`, `"Búsqueda"` o `"Resultados"` |
| `_uploader_key` | `int` | Contador para forzar reset del widget `file_uploader` tras "Limpiar" |
| `uploaded_docs` | `dict` | `{doc_id: filename}` — documentos subidos en la sesión; permite distinguir "en proceso" vs indexados |
| `_custom_skills` | `list` | Skills añadidas manualmente por el usuario (tags custom en el multiselect) |
| `_custom_locations` | `list` | Ubicaciones añadidas manualmente por el usuario (tags custom en el multiselect) |
| `_skills_multiselect` | `list` | Valor actual del multiselect de habilidades (widget key) |
| `_locations_multiselect` | `list` | Valor actual del multiselect de ubicaciones (widget key) |

---

## Notas de diseño importantes

### Estado de búsqueda determinístico

El indicador de carga (`st.status`) se activa si y solo si `_searching=True` al renderizar la página de Resultados. `_searching` lo establece el botón Buscar antes del `st.rerun()`. No hay dependencia de cache-miss para mostrar el spinner — el trigger es único y determinístico.

### Procesamiento de CVs en ACA

El ingest-service llama al processing-service de forma síncrona (timeout 150s). Azure Container Apps mantiene la réplica viva mientras hay una petición HTTP activa, lo que evita que los CVs queden "en proceso" indefinidamente. El processing-service serializa el trabajo pesado internamente con un `asyncio.Semaphore(1)`.

### Filtro de ubicación flexible

El filtro de ubicación en el rag-service usa substring matching case-insensitive en Python (post-retrieval), no filtros exactos en Qdrant. `"Madrid"` hace match con `"Madrid, Spain"`, `"Madrid (España)"`, etc.
