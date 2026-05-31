"""
Componente de subida de CVs (FE-02).
Implementa un área Drag & Drop para subir múltiples archivos PDF
y una barra de progreso que gestiona los estados de los documentos.
"""

import datetime
import streamlit as st
from typing import List
import time

from utils.api_client import get_api_client


def _render_candidates_modal() -> None:
    """Muestra un botón que abre/cierra el panel con candidatos indexados."""
    col1, _ = st.columns([1, 3])
    with col1:
        if st.button("👥 Ver candidatos disponibles", use_container_width=True):
            current = st.session_state.get("_show_candidates_panel", False)
            st.session_state["_show_candidates_panel"] = not current

    if st.session_state.get("_show_candidates_panel", False):
        with st.container(border=True):
            header_col, close_col = st.columns([5, 1])
            with header_col:
                st.markdown("### 📋 Candidatos indexados")
            with close_col:
                if st.button("✕ Cerrar", key="_close_candidates"):
                    st.session_state["_show_candidates_panel"] = False
                    st.rerun()

            # Invalidar cache si hubo un upload exitoso reciente
            if st.session_state.pop("_candidates_needs_refresh", False):
                st.session_state.pop("_candidates_cache", None)

            # El botón se evalúa ANTES de la carga para que el click
            # invalide la cache en la misma ejecución del script.
            refresh_col, ts_col = st.columns([1, 3])
            with refresh_col:
                do_refresh = st.button("🔄 Actualizar", key="_refresh_candidates", use_container_width=True)
            if do_refresh:
                st.session_state.pop("_candidates_cache", None)

            if "_candidates_cache" not in st.session_state:
                with st.spinner("Cargando candidatos..."):
                    api = get_api_client()
                    data = api.list_candidates()
                st.session_state["_candidates_cache"] = data
                st.session_state["_candidates_ts"] = datetime.datetime.now().strftime("%H:%M:%S")

            with ts_col:
                if "_candidates_ts" in st.session_state:
                    st.caption(f"Actualizado: {st.session_state['_candidates_ts']}")

            candidates = st.session_state["_candidates_cache"]

            if not candidates:
                st.info("No hay candidatos indexados todavía.")
            else:
                st.markdown(f"**Total: {len(candidates)} candidato(s)**")
                st.markdown("---")
                for c in candidates:
                    c1, c2, c3 = st.columns([3, 3, 4])
                    with c1:
                        st.markdown(f"**{c.get('name', 'N/A')}**")
                    with c2:
                        email = c.get("email") or "—"
                        st.markdown(email)
                    with c3:
                        st.caption(c.get("file_name", ""))




def _render_delete_all_section() -> None:
    """Zona de peligro: elimina todos los candidatos de Qdrant y Blob Storage."""
    with st.expander("⚠️ Zona de peligro", expanded=False):
        st.warning(
            "Esta acción **eliminará permanentemente** todos los candidatos indexados "
            "y sus archivos PDF del almacenamiento. No se puede deshacer."
        )
        confirmed = st.checkbox(
            "Confirmo que quiero eliminar TODOS los candidatos y archivos",
            key="_delete_all_confirm",
        )
        if st.button(
            "🗑️ Eliminar todo",
            disabled=not confirmed,
            type="primary",
            key="_delete_all_btn",
        ):
            api = get_api_client()
            idx_result = api.delete_all_index()
            blob_result = api.delete_all_uploads()

            if idx_result.get("deleted") and blob_result.get("deleted"):
                # Limpiar estado local
                st.session_state["processing_files"] = {}
                st.session_state.pop("_candidates_cache", None)
                st.session_state["_show_candidates_panel"] = False
                st.session_state["_process_result"] = {
                    "type": "success",
                    "msg": "✅ Todos los candidatos han sido eliminados del índice y del almacenamiento.",
                }
            else:
                errors = []
                if not idx_result.get("deleted"):
                    errors.append(f"Qdrant: {idx_result.get('error', 'error desconocido')}")
                if not blob_result.get("deleted"):
                    errors.append(f"Blob: {blob_result.get('error', 'error desconocido')}")
                st.session_state["_process_result"] = {
                    "type": "error",
                    "msg": "Error al eliminar: " + "; ".join(errors),
                }
            st.rerun()
def render_upload_view():
    """
    Renderiza la vista de subida de CVs con:
    - Componente Drag & Drop
    - Barra de progreso por documento
    - Estados: pendiente, procesando, completado
    """
    st.header("Gestión de CVs")
    st.markdown(
        "Sube uno o múltiples CVs en formato PDF. El sistema los procesará "
        "automáticamente para indexarlos en el motor RAG."
    )
    
    # Divider visual
    st.divider()

    # ---- Botón "Ver candidatos disponibles" ----
    _render_candidates_modal()

    st.divider()

    # ---- Zona de peligro: Eliminar todo ----
    _render_delete_all_section()

    st.divider()

    # Sección de subida de archivos
    st.subheader("Subir Documentos")
    
    # Crear dos columnas: upload area y sidebar con info
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Área de subida de archivos (Streamlit maneja Drag & Drop automáticamente)
        uploaded_files = st.file_uploader(
            label="Arrastra y suelta archivos PDF aquí o haz clic para seleccionar",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
    
    with col2:
        st.info(
            "**Formatos aceptados:**\n"
            "- PDF\n\n"
            "**Tamaño máximo:**\n"
            "- 25 MB"
        )
    
    st.divider()
    
    # Procesar archivos subidos
    if uploaded_files:
        st.subheader("Estado de Procesamiento")
        
        # Inicializar o recuperar el estado de sesión
        if "processing_files" not in st.session_state:
            st.session_state.processing_files = {}
        
        # Procesar cada archivo subido
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            
            # Inicializar el estado del archivo si no existe
            if file_name not in st.session_state.processing_files:
                st.session_state.processing_files[file_name] = {
                    "status": "pending",
                    "progress": 0,
                    "error": None
                }
            
            # Crear contenedor para cada archivo
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{file_name}**")
                    st.markdown(f"*Tamaño: {uploaded_file.size / 1024 / 1024:.2f} MB*")
                with col2:
                    file_status = st.session_state.processing_files[file_name]["status"]
                    if file_status == "pending":
                        status_badge = "[Pendiente]"
                    elif file_status == "processing":
                        status_badge = "[Procesando]"
                    else:  # completed
                        status_badge = "[Completado]"
                    
                    st.markdown(f"**{status_badge}**")
                
                # Barra de progreso
                progress_value = st.session_state.processing_files[file_name]["progress"]
                st.progress(progress_value / 100, text=f"{progress_value}%")
                
                # Error message si existe
                error = st.session_state.processing_files[file_name].get("error")
                if error:
                    st.error(f"Error: {error}")
        
        # Botón para iniciar el procesamiento
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("Procesar CVs", use_container_width=True):
                _process_files(uploaded_files)
        
        with col2:
            if st.button("Limpiar", use_container_width=True):
                st.session_state.processing_files = {}
                st.rerun()
        
        # Mostrar resumen de estadísticas
        st.divider()
        _render_upload_statistics()
        # Mostrar resultado del procesamiento si existe
        if "_process_result" in st.session_state:
            result = st.session_state["_process_result"]
            del st.session_state["_process_result"]
            if result["type"] == "success":
                st.success(result["msg"])
            else:
                st.error(result["msg"])
    
    else:
        # Mostrar mensaje cuando no hay archivos
        st.info(
            "**No hay archivos cargados**\n\n"
            "Sube tus CVs en formato PDF para comenzar el análisis. "
            "El sistema extraerá información relevante y la indexará automáticamente."
        )


def _process_files(uploaded_files: List):
    """
    Procesa los archivos subidos y envía la información al servicio de ingesta.
    
    Args:
        uploaded_files: Lista de archivos subidos
    """
    progress_placeholder = st.empty()
    total_files = len(uploaded_files)

    api_client = get_api_client()
    file_contents = [uploaded_file.read() for uploaded_file in uploaded_files]
    file_names = [uploaded_file.name for uploaded_file in uploaded_files]

    response = api_client.upload_cv_documents(file_contents, file_names)
    document_ids = response.get("document_ids", [])
    upload_message = response.get("message", "Carga completada.")

    if not document_ids:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            st.session_state.processing_files[file_name]["status"] = "error"
            st.session_state.processing_files[file_name]["progress"] = 0
            st.session_state.processing_files[file_name]["error"] = upload_message

        st.session_state["_process_result"] = {"type": "error", "msg": upload_message}
        st.rerun()

    for idx, (uploaded_file, doc_id) in enumerate(zip(uploaded_files, document_ids)):
        file_name = uploaded_file.name
        st.session_state.processing_files[file_name]["status"] = "processing"
        st.session_state.processing_files[file_name]["progress"] = 10

        progress_placeholder.progress(
            ((idx + 0.1) / total_files),
            text=f"Iniciando procesamiento de {file_name}..."
        )
        time.sleep(0.2)

        process_result = api_client.process_document(doc_id)
        process_success = process_result.get("status") == "success"
        process_message = process_result.get("message", "Procesamiento completado.")

        if process_success:
            st.session_state.processing_files[file_name]["status"] = "completed"
            st.session_state.processing_files[file_name]["progress"] = 100
        else:
            st.session_state.processing_files[file_name]["status"] = "error"
            st.session_state.processing_files[file_name]["progress"] = 0
            st.session_state.processing_files[file_name]["error"] = process_message

        progress_placeholder.progress(
            ((idx + 1) / total_files),
            text=f"Procesando archivo {idx + 1} de {total_files}..."
        )
        time.sleep(0.2)

    progress_placeholder.empty()
    # Marca el panel de candidatos para refrescar en el próximo render
    st.session_state["_candidates_needs_refresh"] = True
    st.session_state["_process_result"] = {"type": "success", "msg": "Procesamiento completado para todos los documentos."}
    st.rerun()


def _render_upload_statistics():
    """
    Renderiza las estadísticas de carga de archivos.
    """
    if not st.session_state.processing_files:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    files_status = st.session_state.processing_files
    total = len(files_status)
    completed = len([f for f in files_status.values() if f["status"] == "completed"])
    processing = len([f for f in files_status.values() if f["status"] == "processing"])
    pending = len([f for f in files_status.values() if f["status"] == "pending"])
    
    with col1:
        st.metric("Total", total)
    
    with col2:
        st.metric("Completados", completed)
    
    with col3:
        st.metric("Procesando", processing)
    
    with col4:
        st.metric("Pendientes", pending)
