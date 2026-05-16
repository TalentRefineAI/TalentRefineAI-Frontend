"""
Componente de subida de CVs (FE-02).
Implementa un área Drag & Drop para subir múltiples archivos PDF
y una barra de progreso que gestiona los estados de los documentos.
"""

import streamlit as st
from typing import List
import time


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
            with st.container(border=True):
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
    
    else:
        # Mostrar mensaje cuando no hay archivos
        st.info(
            "**No hay archivos cargados**\n\n"
            "Sube tus CVs en formato PDF para comenzar el análisis. "
            "El sistema extraerá información relevante y la indexará automáticamente."
        )


def _process_files(uploaded_files: List):
    """
    Simula el procesamiento de archivos con progreso.
    
    Args:
        uploaded_files: Lista de archivos subidos
    """
    # Mostrar un placeholder para la barra de progreso general
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    total_files = len(uploaded_files)
    
    # Procesar cada archivo
    for idx, uploaded_file in enumerate(uploaded_files):
        file_name = uploaded_file.name
        
        # Simular tres fases: 0% -> 50% -> 100%
        for progress in [0, 30, 60, 100]:
            st.session_state.processing_files[file_name]["progress"] = progress
            
            if progress < 100:
                st.session_state.processing_files[file_name]["status"] = "processing"
            else:
                st.session_state.processing_files[file_name]["status"] = "completed"
            
            # Actualizar la UI
            progress_placeholder.progress(
                ((idx + progress / 100) / total_files),
                text=f"Procesando archivo {idx + 1} de {total_files}..."
            )
            
            time.sleep(0.3)  # Simular tiempo de procesamiento
    
    # Mensaje final
    status_placeholder.success(
        f"Procesamiento completado. Se han indexado {total_files} CVs exitosamente."
    )


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
