# DEVELOPMENT.md — Guía de desarrollo (Frontend)

---

## Arquitectura de componentes

```
app.py                      # Punto de entrada: inicializa session state, renderiza sidebar, enruta entre páginas
│
├── components/upload_view.py    # render_upload_view()  — Vista de subida de CVs
├── components/query_view.py     # render_query_view()   — Vista de búsqueda
└── components/results_view.py   # render_results_view() — Vista de resultados
```

Cada componente expone una única función pública `render_*_view()` sin parámetros.
El estado compartido se gestiona exclusivamente a través de `st.session_state`.

---

## Session state

| Key | Tipo | Establecido por | Consumido por |
|-----|------|----------------|---------------|
| `processing_files` | `dict[filename: str, {status, doc_id, ...}]` | `upload_view` | `upload_view` (estadísticas + progreso) |
| `last_search` | `dict` con `query`, `experience_min`, `experience_max`, `locations`, `skills`, `should_search` | `query_view` | `results_view` |
| `_nav_page_request` | `str` (nombre de página) | `query_view` / `results_view` | `app.py` |
| `search_results` | `list[dict]` | `results_view` | `results_view` (display) |
| `current_page` | `str` | `app.py` | `app.py` (routing) |

### Flujo de búsqueda

1. Usuario rellena `query_view` y pulsa "Buscar".
2. `query_view` guarda los parámetros en `st.session_state.last_search` con `should_search=True`.
3. `query_view` setea `st.session_state._nav_page_request = "Resultados"` y llama `st.rerun()`.
4. `app.py` detecta `_nav_page_request`, cambia `current_page` y limpia el flag.
5. `results_view` detecta `should_search=True`, llama al API, guarda resultados y limpia el flag.

---

## api_client.py

```python
from utils.api_client import get_api_client

client = get_api_client()          # Singleton cacheado con @st.cache_resource

# Subir CVs
result = client.upload_documents(files, filenames)

# Buscar candidatos
results = client.search_candidates(
    job_description="...",
    min_exp_years=3,
    required_location=None,  # o "Madrid"
    top_k=5,
)

# Listar ubicaciones y habilidades disponibles (para dropdowns)
locations = client.get_available_locations()
skills    = client.get_available_skills()

# Estado de un documento
status = client.get_document_status(doc_id)

# Eliminar todos los CVs / índice
client.delete_all_documents()
client.delete_candidates_index()
```

Si `USE_MOCK_DATA=true` el cliente devuelve datos de `mock_data.py` sin llamar al backend.

---

## Convenciones de código

- **PEP 8** con max 100 chars/línea.
- Funciones públicas de componentes: `render_*_view()`.
- Funciones helper privadas: `_nombre_descriptivo()`.
- Tipado con `typing` donde añada claridad.
- Logging con `st.error` / `st.warning` para errores de usuario; `print` / structlog para debug.

---

## Notas sobre Streamlit 1.30

- **No usar `st.form` + `st.form_submit_button` + `st.rerun()` juntos** — la combinación
  es frágil en esta versión: el submit puede no propagarse correctamente. Usar `st.button` directo.
- `st.cache_resource` para el singleton del API client.
- `st.cache_data` para datos de baja frecuencia (listas de ubicaciones/habilidades).
- `st.rerun()` es la forma actual de forzar re-renderizado (antes `st.experimental_rerun()`).

---

## Añadir un nuevo filtro de búsqueda

1. Añadir el widget en `query_view.py` (fuera de cualquier `st.form`).
2. Incluir el valor en `st.session_state.last_search`.
3. Actualizar `SearchRequest` en el backend (`app/rag_service/routers/search.py`).
4. Actualizar `api_client.search_candidates()` para pasar el nuevo parámetro.
5. Actualizar `results_view.py` si el filtro afecta la visualización.

---

## Añadir una nueva vista

1. Crear `components/nueva_view.py` con función `render_nueva_view()`.
2. Importar y registrar en `app.py` en el dict de páginas.
3. Añadir entrada en el sidebar.

---

## Testing local rápido

```bash
# Modo mock (sin backend)
USE_MOCK_DATA=true streamlit run app.py

# Con backend local (requiere docker-compose.local-fake.yml activo en el backend)
BACKEND_BASE_URL=http://localhost:8000 RAG_SERVICE_URL=http://localhost:8001 streamlit run app.py
```
