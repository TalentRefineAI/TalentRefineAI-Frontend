"""
Componente de consulta (FE-03).
Diseña un formulario con inputs para filtrar candidatos.
Incluye desplegables, sliders y área de texto para consultas semánticas.
"""

import streamlit as st
from typing import Dict, List, Any
from utils.api_client import get_api_client


def _on_add_skill():
    """Callback: añadir skill personalizada desde el text_input."""
    counter = st.session_state.get("_skill_input_counter", 0)
    val = st.session_state.get(f"_skill_input_{counter}", "").strip()
    if val and val not in st.session_state.get("_custom_skills", []):
        st.session_state["_custom_skills"].append(val)
        current = list(st.session_state.get("_skills_multiselect", []))
        if val not in current:
            current.append(val)
        st.session_state["_skills_multiselect"] = current
    st.session_state["_skill_input_counter"] += 1


def _on_add_location():
    """Callback: añadir ubicación personalizada desde el text_input."""
    counter = st.session_state.get("_loc_input_counter", 0)
    val = st.session_state.get(f"_loc_input_{counter}", "").strip()
    if val and val not in st.session_state.get("_custom_locations", []):
        st.session_state["_custom_locations"].append(val)
        current = list(st.session_state.get("_locations_multiselect", []))
        if val not in current:
            current.append(val)
        st.session_state["_locations_multiselect"] = current
    st.session_state["_loc_input_counter"] += 1


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

    st.markdown("**Ubicación:**")
    st.text_input(
        "Añadir ubicación:",
        key=f"_loc_input_{st.session_state.get('_loc_input_counter', 0)}",
        placeholder="Escribe una ubicación y pulsa Enter...",
        on_change=_on_add_location,
        label_visibility="collapsed",
    )

    custom_locs = st.session_state.get("_custom_locations", [])
    all_locs_opts = list(available_locations) + [l for l in custom_locs if l not in available_locations]

    if "_locations_multiselect" not in st.session_state:
        st.session_state["_locations_multiselect"] = []

    selected_locations = st.multiselect(
        "Selecciona ubicaciones:",
        options=all_locs_opts,
        key="_locations_multiselect",
        placeholder="Selecciona de la lista o escribe arriba...",
        label_visibility="collapsed",
    )

    # Fila 3: Habilidades técnicas unificadas
    available_skills = api_client.get_available_skills()

    st.markdown("**Habilidades Requeridas:**")
    st.text_input(
        "Añadir habilidad:",
        key=f"_skill_input_{st.session_state.get('_skill_input_counter', 0)}",
        placeholder="Escribe y pulsa Enter para añadir un tag...",
        on_change=_on_add_skill,
        label_visibility="collapsed",
    )

    custom_skills = st.session_state.get("_custom_skills", [])
    all_skills_opts = list(available_skills) + [s for s in custom_skills if s not in available_skills]

    if "_skills_multiselect" not in st.session_state:
        st.session_state["_skills_multiselect"] = []

    selected_skills = st.multiselect(
        "Selecciona habilidades:",
        options=all_skills_opts,
        key="_skills_multiselect",
        placeholder="Selecciona de la lista o escribe arriba...",
        label_visibility="collapsed",
    )

    # Fila 4: Ejemplos de consultas útiles
    st.divider()
    with st.expander("Ver ejemplos de consultas"):
        st.markdown("""
**Senior Backend Python:**
> "Desarrollador Python senior con +5 años en microservicios y FastAPI. Experiencia sólida en PostgreSQL, Redis y despliegue en cloud (AWS o Azure). Se valorará conocimiento de arquitectura hexagonal y haber liderado equipos pequeños."

**Data Engineer / MLOps:**
> "Buscamos un Data Engineer con experiencia en pipelines de datos (Spark, Airflow) y familiaridad con plataformas MLOps (MLflow, Kubeflow). Conocimiento de SQL avanzado y al menos un cloud provider. Python es imprescindible."

**Frontend React / TypeScript:**
> "Desarrollador frontend mid-senior con dominio de React y TypeScript. Experiencia con testing (Jest, Cypress), design systems y colaboración estrecha con equipos de diseño. Se valorará experiencia con Next.js y accesibilidad web."

**DevOps / Platform Engineer:**
> "Ingeniero de plataforma con experiencia en Kubernetes, Terraform e infraestructura como código. Dominio de CI/CD con GitHub Actions o GitLab CI. Deseable experiencia en observabilidad (Prometheus, Grafana) y seguridad en cloud."

**Fullstack Junior:**
> "Desarrollador júnior fullstack con conocimientos de JavaScript/TypeScript, React básico y algún framework backend (Node.js, Django o FastAPI). Ganas de aprender y capacidad para trabajar en equipo. Formación reciente valorada."
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
            type="primary",
            disabled=st.session_state.get("_searching", False),
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

        st.session_state["last_search"] = {
            "query": semantic_query,
            "experience_min": experience_min,
            "experience_max": 20,
            "locations": list(st.session_state.get("_locations_multiselect", [])) or None,
            "skills": list(st.session_state.get("_skills_multiselect", [])) or None,
            "should_search": True,
        }
        st.session_state.pop("_results_cache_key", None)
        st.session_state.pop("_results_cache", None)
        st.session_state["_searching"] = True
        st.session_state["_page"] = "Resultados"
        st.rerun()

    if clear_button:
        st.session_state["last_search"] = {
            "query": "",
            "experience_min": 0,
            "experience_max": 20,
            "locations": None,
            "skills": None,
            "should_search": False,
        }
        st.session_state.pop("_results_cache_key", None)
        st.session_state.pop("_results_cache", None)
        st.session_state["_searching"] = False
        st.session_state["_custom_skills"] = []
        st.session_state["_skills_multiselect"] = []
        st.session_state["_skill_input_counter"] = 0
        st.session_state["_custom_locations"] = []
        st.session_state["_locations_multiselect"] = []
        st.session_state["_loc_input_counter"] = 0
        st.session_state["_page"] = "Búsqueda"
        st.rerun()
