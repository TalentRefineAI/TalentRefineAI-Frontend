"""
Componente de resultados (FE-04).
Renderiza tarjetas dinámicas con candidatos clasificados por relevancia.
Cada tarjeta muestra nombre, habilidades y justificación del LLM.
"""

import streamlit as st
from typing import Dict, List, Any
from utils.api_client import get_api_client


def render_results_view():
    """
    Renderiza la vista de resultados RAG con:
    - Tarjetas dinámicas de candidatos
    - Ranking por score de relevancia
    - Justificación del LLM
    - Detalles expandibles
    """
    st.header("Resultados de Búsqueda")
    
    # Verificar si hay una búsqueda ejecutada y si el estado es un diccionario válido
    last_search = st.session_state.get("last_search")
    if not isinstance(last_search, dict) or not last_search.get("should_search"):
        st.info(
            "Por favor, introduce una búsqueda en la sección correspondiente para ver los resultados."
        )
        return
    
    # Obtener parámetros de la búsqueda anterior
    search_params = last_search
    query = search_params.get("query", "")
    experience_min = search_params.get("experience_min", 0)
    experience_max = search_params.get("experience_max", 20)
    locations = search_params.get("locations")
    skills = search_params.get("skills")
    
    # Llamar a la API para obtener resultados
    api_client = get_api_client(use_mock=True)
    results = api_client.query_rag(
        query=query,
        experience_min=experience_min,
        experience_max=experience_max,
        locations=locations
    )
    
    # Mostrar información de la búsqueda
    st.markdown(f"**Consulta:** _{query}_")
    
    if results.get("candidates"):
        st.success(f"Se encontraron {len(results['candidates'])} candidatos relevantes")
    else:
        st.warning("No se encontraron candidatos con los criterios especificados")
        return
    
    st.divider()
    
    # Mostrar metadatos de la búsqueda
    with st.expander("Parámetros de la Búsqueda"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Experiencia (años)", f"{experience_min}-{experience_max}")
        with col2:
            locations_text = ", ".join(locations) if locations else "Todas"
            st.write(f"**Ubicaciones:** {locations_text}")
        with col3:
            skills_text = len(skills) if skills else 0
            st.write(f"**Habilidades filtradas:** {skills_text}")
        with col4:
            processing_time = results.get("metadata", {}).get("processing_time_ms", 0)
            st.write(f"**Tiempo de búsqueda:** {processing_time}ms")
    
    st.divider()
    
    # Renderizar tarjetas de candidatos
    st.subheader("Candidatos Recomendados")
    
    candidates = results.get("candidates", [])
    
    for idx, candidate in enumerate(candidates, 1):
        _render_candidate_card(candidate, idx)
    
    # Mostrar opciones de exportación
    st.divider()
    st.subheader("Acciones")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Enviar Invitaciones", use_container_width=True):
            st.success("Se han enviado invitaciones a los candidatos seleccionados.")
    
    with col2:
        if st.button("Guardar Resultados", use_container_width=True):
            st.success("Resultados guardados en tu biblioteca de búsquedas.")
    
    with col3:
        if st.button("Generar Reporte", use_container_width=True):
            st.success("Reporte generado. Descárgalo en tu escritorio.")


def _render_candidate_card(candidate: Dict[str, Any], position: int):
    """
    Renderiza una tarjeta individual de candidato.
    
    Args:
        candidate (Dict[str, Any]): Datos del candidato
        position (int): Posición en el ranking
    """
    with st.container(border=True):
        # Encabezado con ranking
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### #{position} {candidate.get('name', 'Sin nombre')}")
        
        with col2:
            match_score = candidate.get("match_score", 0)
            score_color = _get_score_color(match_score)
            st.markdown(f"<div style='text-align: right; font-weight: bold; color: {score_color};'>{match_score}%</div>", 
                       unsafe_allow_html=True)
        
        with col3:
            # Badge de ubicación
            location = candidate.get("location", "N/A")
            st.markdown(f"{location}")
        
        # Información básica en dos columnas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Email:** `{candidate.get('email', 'N/A')}`")
            st.markdown(f"**Teléfono:** {candidate.get('phone', 'N/A')}")
        
        with col2:
            experience = candidate.get("experience_years", 0)
            st.markdown(f"**Experiencia:** {experience} años")
            st.markdown(f"**Especialización:** {candidate.get('expertise_summary', 'N/A')}")
        
        st.divider()
        
        # Habilidades en forma de badges
        st.markdown("**Habilidades Técnicas:**")
        skills = candidate.get("skills", [])
        if skills:
            skill_badges = " ".join([f"`{skill}`" for skill in skills])
            st.markdown(skill_badges)
        
        st.divider()
        
        # Justificación del LLM en un expander
        with st.expander("Justificación del Análisis RAG"):
            justification = candidate.get("llm_justification", "No disponible")
            st.markdown(justification)
        
        st.divider()
        
        # Botones de acción
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Ver CV", key=f"view_cv_{candidate.get('id')}", use_container_width=True):
                st.info(f"CV: {candidate.get('document_name', 'documento.pdf')}")
        
        with col2:
            if st.button("Contactar", key=f"contact_{candidate.get('id')}", use_container_width=True):
                st.success(f"Email enviado a {candidate.get('name')}")
        
        with col3:
            if st.button("Favorito", key=f"favorite_{candidate.get('id')}", use_container_width=True):
                st.success("Añadido a favoritos")
        
        with col4:
            if st.button("Más Info", key=f"more_info_{candidate.get('id')}", use_container_width=True):
                st.info(
                    f"**Información Completa:**\n\n"
                    f"- **ID:** {candidate.get('id')}\n"
                    f"- **Documento:** {candidate.get('document_name')}\n"
                    f"- **Score:** {candidate.get('match_score')}%"
                )


def _get_score_color(score: int) -> str:
    """
    Retorna el color según el score de relevancia.
    
    Args:
        score (int): Score de 0-100
        
    Returns:
        str: Color en hexadecimal
    """
    if score >= 90:
        return "#00d084"  # Verde oscuro
    elif score >= 80:
        return "#00c9b7"  # Verde claro
    elif score >= 70:
        return "#ffd700"  # Oro
    elif score >= 60:
        return "#ffa500"  # Naranja
    else:
        return "#ff6b6b"  # Rojo
