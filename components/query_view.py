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
    - Filtros por años de experiencia mínima (slider)
    - Filtros por ubicación (multiselect)
    - Filtros por habilidades técnicas con entrada personalizada
    - Ejemplos de consultas útiles
    - Área de texto para consulta semántica
    - Botón de búsqueda
    """
    st.header("Búsqueda de Candidatos")
    st.markdown(
        "Utiliza el formulario a continuación para buscar candidatos ideales "
        "usando consultas semánticas y filtros específicos."
    )
    
    st.divider()
    
    st.subheader("Criterios de Búsqueda")

    # Fila 1: Años de experiencia mínima
    experience_min = st.slider(
        "Experiencia Mínima (años)",
        min_value=0,
        max_value=20,
        value=0,
        step=1,
        help="Especifica el mínimo de años de experiencia requeridos."
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

    # Fila 3: Habilidades técnicas con opción de entrada personalizada
    available_skills = api_client.get_available_skills()

    # Crear lista mutable para añadir habilidades personalizadas
    skills_list = list(available_skills) if available_skills else []

    # Sublínea para entrada de habilidad personalizada
    st.markdown("**Habilidades Requeridas:**")
    custom_skill = st.text_input(
        "Escriba una habilidad personalizada (opcional):",
        placeholder="Ej: Scala, Go, Rust, Kubernetes, etc.",
        key="custom_skill_input",
        help="Ingresa una habilidad que no esté en la lista predefinida para añadirla."
    )

    # Añadir la habilidad personalizada a la lista si se proporcionó
    if custom_skill and custom_skill.strip():
        if custom_skill.strip() not in skills_list:
            skills_list.append(custom_skill.strip())

    # Multiselect para seleccionar habilidades (predefinidas + personalizadas)
    selected_skills = st.multiselect(
        "Selecciona de la lista:",
        options=skills_list,
        default=[],
        help="Elige las habilidades técnicas que buscas. La habilidad personalizada que ingresaste estará disponible arriba."
    )

    # Fila 4: Ejemplos de consultas útiles
    st.divider()
    with st.expander("Ver ejemplos de consultas"):
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

    # Fila 5: Consulta semántica
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
        search_button = st.button(
            "Buscar",
            use_container_width=True,
            type="primary"
        )

    with col2:
        clear_button = st.button(
            "Limpiar",
            use_container_width=True
        )
    
    # Validar y ejecutar búsqueda
    if search_button:
        if not semantic_query.strip():
            st.error("Por favor, ingresa una consulta semántica.")
            return
        
        # Guardar en session state para que results_view pueda acceder
        st.session_state.last_search = {
            "query": semantic_query,
            "experience_min": experience_min,
            "experience_max": 20,
            "locations": selected_locations if selected_locations else None,
            "skills": selected_skills if selected_skills else None,
            "should_search": True
        }
        # Invalidar caché y estado de busqueda para forzar llamada fresca
        st.session_state.pop("_results_cache_key", None)
        st.session_state.pop("_results_cache", None)
        st.session_state["_searching"] = False  # reiniciar maquina de estados
        # Navegar automaticamente a la vista de Resultados
        st.session_state._nav_page_request = "Resultados"
        st.rerun()
    
    if clear_button:
        if "last_search" in st.session_state:
            del st.session_state.last_search
        st.rerun()
