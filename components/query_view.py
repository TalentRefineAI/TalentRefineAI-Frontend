"""
Componente de consulta (FE-03).
Diseña un formulario con inputs para filtrar candidatos.
Incluye desplegables, sliders y área de texto para consultas semánticas.
"""

import streamlit as st
from typing import Dict, List, Any
from utils.api_client import get_api_client


def render_query_view():
    """
    Renderiza la vista de consulta RAG con:
    - Filtros por años de experiencia (slider)
    - Filtros por ubicación (multiselect)
    - Área de texto para consulta semántica
    - Botón de búsqueda
    """
    st.header("🔍 Búsqueda de Candidatos")
    st.markdown(
        "Utiliza el formulario a continuación para buscar candidatos ideales "
        "usando consultas semánticas y filtros específicos."
    )
    
    st.divider()
    
    # Crear formulario con los filtros
    with st.form(key="search_form"):
        st.subheader("Criterios de Búsqueda")
        
        # Fila 1: Años de experiencia
        col1, col2 = st.columns(2)
        with col1:
            experience_min = st.slider(
                "Experiencia Mínima (años)",
                min_value=0,
                max_value=20,
                value=0,
                step=1
            )
        
        with col2:
            experience_max = st.slider(
                "Experiencia Máxima (años)",
                min_value=0,
                max_value=30,
                value=20,
                step=1
            )
        
        # Fila 2: Ubicación
        api_client = get_api_client()
        available_locations = api_client.get_available_locations()
        
        selected_locations = st.multiselect(
            "Ubicación Preferida",
            options=available_locations,
            default=[],
            help="Selecciona una o más ubicaciones. Dejar vacío para todas."
        )
        
        # Fila 3: Habilidades técnicas
        available_skills = api_client.get_available_skills()
        selected_skills = st.multiselect(
            "Habilidades Requeridas",
            options=available_skills,
            default=[],
            help="Selecciona las habilidades técnicas que buscas."
        )
        
        # Fila 4: Consulta semántica
        st.divider()
        semantic_query = st.text_area(
            "Consulta Semántica",
            placeholder="Ej: Buscamos un desarrollador senior con experiencia en arquitectura de microservicios y cloud native para liderar nuestro equipo de backend...",
            height=120,
            help="Describe con detalle el perfil que buscas. El LLM analizará tus CVs y encontrará los mejores candidatos."
        )
        
        st.divider()
        
        # Botón de búsqueda
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            search_button = st.form_submit_button(
                "🔍 Buscar",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            clear_button = st.form_submit_button(
                "🔄 Limpiar",
                use_container_width=True
            )
    
    # Validar y ejecutar búsqueda
    if search_button:
        if not semantic_query.strip():
            st.error("⚠️ Por favor, ingresa una consulta semántica.")
            return
        
        if experience_min > experience_max:
            st.error("⚠️ La experiencia mínima no puede ser mayor que la máxima.")
            return
        
        # Guardar en session state para que results_view pueda acceder
        st.session_state.last_search = {
            "query": semantic_query,
            "experience_min": experience_min,
            "experience_max": experience_max,
            "locations": selected_locations if selected_locations else None,
            "skills": selected_skills if selected_skills else None,
            "should_search": True
        }
        
        st.success("✅ Búsqueda ejecutada. Ve a la sección de Resultados para ver los candidatos.")
    
    if clear_button:
        if "last_search" in st.session_state:
            del st.session_state.last_search
        st.rerun()
    
    # Mostrar ejemplos de búsquedas útiles
    with st.expander("💡 Ejemplos de Consultas"):
        st.markdown("""
        **Desarrollador Backend:**
        > "Necesitamos un desarrollador backend con experiencia en Python, FastAPI y bases de datos PostgreSQL. 
        > Debe tener al menos 5 años de experiencia y preferiblemente conocimiento en AWS."
        
        **Ingeniero DevOps:**
        > "Buscamos un especialista DevOps con experiencia en Kubernetes, Terraform e infraestructura cloud. 
        > Debe estar familiarizado con CI/CD pipelines usando Jenkins o GitLab CI."
        
        **Data Scientist:**
        > "Necesitamos un data scientist con experiencia en machine learning, Python y análisis estadístico. 
        > Preferiblemente con experiencia en proyectos de NLP o Computer Vision."
        """)
