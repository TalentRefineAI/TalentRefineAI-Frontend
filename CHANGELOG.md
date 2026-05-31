# Changelog

Todos los cambios notables se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.3.0] — 2025-06

### Fixed
- **Stats bar** (`upload_view.py`): `_render_upload_statistics()` ahora acepta `uploaded_files`
  y filtra `st.session_state.processing_files` para mostrar solo los archivos actualmente
  visibles en el uploader — evita el bug donde un CV completado inflaba el total incluso
  cuando el usuario ya había seleccionado otros archivos.
- **Search button** (`query_view.py`): eliminado `st.form` / `st.form_submit_button` que
  fallaba silenciosamente en Streamlit 1.30 al combinarse con `st.rerun()`. Reemplazado por
  `st.button` directo; la búsqueda ahora se ejecuta de forma fiable al pulsar "Buscar".
- Renombrada métrica "Completados" a **"Indexados"** con help text explicativo.

---

## [1.2.0] — 2025-05

### Added
- Integración con backend real: `api_client.py` conecta a ingest-service y rag-service en producción.
- Botón "Eliminar todos los CVs" que llama a `DELETE /upload/all` en el ingest-service.
- Botón "Vaciar índice" que llama a `DELETE /search/candidates` en el rag-service.
- Vista de resultados muestra score híbrido (0-100%), resumen y justificación del LLM por candidato.
- Navegación programática: `st.session_state._nav_page_request` redirige a "Resultados" tras buscar.
- Manejo de errores HTTP en `api_client.py` con mensajes de usuario.
- Botón "Refresh" en barra lateral para limpiar session state y actualizar estado de procesamiento.

### Fixed
- Múltiples correcciones de producción (production audit): manejo de respuestas malformadas,
  timeouts, estados de carga inconsistentes.

---

## [1.1.0] — 2025-04

### Added
- Vista de consulta (`query_view.py`) con slider de experiencia, multiselect de ubicación y
  habilidades, texto libre para consulta semántica.
- Input de habilidad personalizada en la vista de búsqueda.
- Ejemplos de consultas expandibles.

---

## [1.0.0] — 2025-03

### Added
- **[FE-01]** Configuración base: Streamlit, navegación en sidebar, session state.
- **[FE-02]** Vista de subida de CVs: Drag & Drop, progreso por documento, estados.
- **[FE-03]** Vista de consulta con filtros y área semántica.
- **[FE-04]** Vista de resultados con tarjetas de candidatos, score con colores, habilidades como badges.
- **[FE-05]** Cliente API (`RAGAPIClient`) con modo mock intercambiable.
- Dockerfile y docker-compose para despliegue.
