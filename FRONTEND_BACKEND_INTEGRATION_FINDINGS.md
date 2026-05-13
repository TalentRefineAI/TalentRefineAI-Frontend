# Frontend Backend Integration Findings

Este documento recoge los cambios funcionales detectados en el frontend que conviene realizar para completar la integracion con el backend FastAPI actual. No se han aplicado cambios de codigo en esta fase.

## 1. El cliente API usa una URL unica hardcodeada

**Problema detectado**

`utils/api_client.py` inicializa `RAGAPIClient` con `base_url="http://localhost:8000"` y construye todas las llamadas contra esa unica URL.

El backend actual no expone una unica API en `8000`. En local, los servicios publicados son:

- `ingest-service`: `http://localhost:8001`
- `processing-service`: `http://localhost:8002`
- `rag-service`: `http://localhost:8003`

En Docker Compose, ademas, el frontend debe comunicarse por DNS interno:

- `http://ingest-service:8000`
- `http://rag-service:8000`

**Impacto**

Si se activa el modo de API real, Streamlit intentara llamar a un endpoint inexistente en `http://localhost:8000`. Dentro del contenedor, `localhost` apunta al propio contenedor de Streamlit, no al backend, por lo que la integracion real fallaria aunque los servicios FastAPI esten arrancados correctamente.

**Cambio justificado**

El cliente debe leer URLs separadas desde variables de entorno:

- `INGEST_API_URL`
- `RAG_API_URL`

Esto hace que el mismo codigo sea reproducible en local Docker y en Azure, donde cada servicio tendra un FQDN o endpoint interno diferente.

## 2. Las rutas usadas por el frontend no coinciden con el backend actual

**Problema detectado**

`utils/api_client.py` usa rutas de una API prevista para una fase anterior:

- `POST /api/v1/documents/upload`
- `POST /api/v1/rag/query`
- `GET /api/v1/documents/status`

El backend actual expone:

- `POST /upload` en `ingest-service`
- `GET /upload/{doc_id}/status` en `ingest-service`
- `POST /search` en `rag-service`

**Impacto**

Aunque las URLs base se corrigieran, las llamadas reales seguirian devolviendo `404 Not Found`. Esto bloquearia tanto la subida real de CVs como la busqueda RAG desde Streamlit.

**Cambio justificado**

Actualizar las rutas del cliente al contrato real evita introducir un API gateway ficticio y mantiene la arquitectura definida: Streamlit habla directamente con `ingest-service` y `rag-service`.

## 3. El payload de busqueda no coincide con `SearchRequest`

**Problema detectado**

El frontend construye actualmente un payload de busqueda con campos como:

- `query`
- `experience_min`
- `experience_max`
- `locations`
- `top_k`

El backend espera el modelo `SearchRequest`:

- `job_description`
- `filters.min_exp_years`
- `filters.location`
- `top_k`

**Impacto**

El backend rechazara la peticion real con error de validacion `422 Unprocessable Entity`, porque `job_description` es obligatorio y el esquema de filtros no coincide.

**Cambio justificado**

Mapear el formulario de Streamlit al contrato real permite que la UI siga usando sus controles actuales mientras envia un payload compatible con FastAPI. Para la primera integracion basta con usar la primera ubicacion seleccionada como `filters.location`, ya que el backend actual solo acepta una ubicacion.

## 4. La vista de resultados fuerza siempre mocks

**Problema detectado**

`components/results_view.py` instancia el cliente con `get_api_client(use_mock=True)`, por lo que nunca llama al backend real aunque el usuario seleccione API real en la sidebar.

**Impacto**

La aplicacion puede aparentar estar integrada con FastAPI, pero siempre mostrara datos simulados. Esto oculta fallos reales de conectividad, contrato y configuracion.

**Cambio justificado**

El modo mock/API real debe depender de una configuracion central, preferiblemente `USE_MOCK_DATA` y/o estado de sesion de Streamlit. Asi se preserva el modo demo y se habilita una ruta real de validacion end-to-end.

## 5. La configuracion avanzada de la sidebar no gobierna el cliente

**Problema detectado**

`app.py` muestra un selector entre mocks y API real, y un campo de URL, pero esos valores no se propagan al cliente API usado por `query_view` ni `results_view`.

**Impacto**

La UI ofrece controles que no tienen efecto funcional. Esto puede confundir en pruebas locales, demos y validaciones DevOps, porque el operador cree estar probando una configuracion que realmente no se utiliza.

**Cambio justificado**

La sidebar debe escribir la configuracion en `st.session_state`, y los componentes deben crear el cliente usando esos valores. En contenedor y Azure, los defaults deben venir de variables de entorno para evitar valores hardcodeados.

## 6. La respuesta RAG real necesita adaptacion para la UI actual

**Problema detectado**

La UI de resultados espera candidatos con campos como:

- `name`
- `match_score`
- `experience_years`
- `expertise_summary`
- `llm_justification`
- `document_name`

El backend devuelve `CandidateResult` con campos como:

- `candidate_id`
- `file_name`
- `score`
- `summary`
- `reason`
- `contact_info`
- `exp_years`
- `location`

**Impacto**

Aunque la busqueda real respondiera correctamente, la UI podria mostrar valores vacios o incorrectos si no se normaliza la respuesta.

**Cambio justificado**

El cliente frontend debe transformar la respuesta real al formato que ya consume la UI. Esto reduce el alcance del cambio: no obliga a reescribir las tarjetas visuales y mantiene separada la adaptacion de contrato en una capa de cliente.

## 7. El healthcheck del Dockerfile usa `curl`, pero la imagen final no lo instala

**Problema detectado**

El `Dockerfile` instala `curl` en la etapa `builder`, pero la etapa final `production` parte de `base` y solo copia el virtualenv desde `builder`. Por tanto, `curl` no queda garantizado en la imagen runtime.

El propio `Dockerfile` declara:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1
```

**Impacto**

Cuando la imagen se ejecute fuera de un Compose que sobrescriba el healthcheck, Docker o Azure podrian marcar el contenedor como unhealthy aunque Streamlit este funcionando correctamente, simplemente porque el binario `curl` no existe en runtime.

**Cambio justificado**

El healthcheck del Dockerfile debe usar una herramienta disponible en la imagen final, por ejemplo `python -c` con `urllib.request`, o instalar `curl` tambien en la etapa `production`. Usar Python reduce paquetes del sistema y mantiene la imagen mas pequena.

## Recomendacion de implementacion futura

Implementar estos cambios en un commit separado del backend, con el siguiente alcance:

- Actualizar `utils/api_client.py` para usar `INGEST_API_URL`, `RAG_API_URL`, rutas reales y normalizacion de respuesta.
- Actualizar `app.py` para que la sidebar guarde modo y URLs en `st.session_state`.
- Actualizar `components/query_view.py` y `components/results_view.py` para instanciar el cliente con la configuracion activa.
- Mantener `USE_MOCK_DATA=true` por defecto para no romper demos locales.

Mensaje sugerido:

```text
feat(frontend): document backend API integration gaps
```
