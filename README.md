# TalentRefineAI-Frontend

Frontend de **TalentRefine AI**, plataforma de reclutamiento inteligente que permite subir CVs en PDF y buscar candidatos mediante lenguaje natural, con resultados clasificados por un score híbrido (semántico + LLM).

Construido con **Streamlit 1.30** y desplegado en Azure Container Apps.

---

## Demo en producción

**URL:** `https://ca-frontend-talentrefine-dev-spc.greenwave-4d796cb5.spaincentral.azurecontainerapps.io`

---

## Funcionalidades

| Vista | Descripción |
|-------|-------------|
| **Subida de CVs** | Carga múltiples PDFs con Drag & Drop, barra de progreso por documento, estadísticas en tiempo real |
| **Búsqueda** | Consulta semántica libre + filtros (experiencia mínima, ubicación, habilidades) |
| **Resultados** | Candidatos ordenados por score híbrido con resumen y justificación del LLM |

---

## Estructura del proyecto

```
TalentRefineAI-Frontend/
├── app.py                    # Punto de entrada Streamlit (navegación + session state)
├── Dockerfile
├── requirements.txt
├── components/
│   ├── upload_view.py        # Vista de subida de CVs
│   ├── query_view.py         # Vista de búsqueda con filtros
│   └── results_view.py       # Vista de resultados y candidatos
└── utils/
    ├── api_client.py         # Cliente HTTP hacia los servicios backend
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
docker run -p 8501:8501   -e BACKEND_BASE_URL=http://host.docker.internal:8000   -e RAG_SERVICE_URL=http://host.docker.internal:8001   rag-hr-frontend:local
```

---

## Despliegue en producción

Ver `OPERATIONS.md` en el repositorio backend para el flujo completo de build y deploy.

```bash
ACR=crtalentrefinedevspc
RG=rg-talentrefine-dev-spc

az acr build --registry $ACR   --image rag-hr-frontend:latest   --file Dockerfile .   --resource-group $RG

az containerapp update   --name ca-frontend-talentrefine-dev-spc   --resource-group $RG   --image $ACR.azurecr.io/rag-hr-frontend:latest   --revision-suffix v$(date +%Y%m%d)
```

---

## Session state keys principales

| Key | Tipo | Descripción |
|-----|------|-------------|
| `processing_files` | `dict[str, dict]` | Estado por nombre de archivo (`pending`/`processing`/`completed`/`error`) |
| `last_search` | `dict` | Parámetros de la última búsqueda + flag `should_search` |
| `_nav_page_request` | `str` | Navegación programática entre páginas |
| `search_results` | `list` | Resultados de la última búsqueda RAG |

---

## Guía de desarrollo

Ver [DEVELOPMENT.md](DEVELOPMENT.md) para convenciones de código, estructura de componentes
y patrones de integración con la API.

---

## Changelog

Ver [CHANGELOG.md](CHANGELOG.md).
