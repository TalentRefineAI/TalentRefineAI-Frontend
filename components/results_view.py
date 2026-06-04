"""
Componente de resultados (FE-04).
Renderiza tarjetas dinamicas con candidatos clasificados por relevancia.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
from utils.api_client import get_api_client


def render_results_view():
    st.header("Resultados de Búsqueda")

    last_search = st.session_state.get("last_search")
    if not isinstance(last_search, dict) or not last_search.get("should_search"):
        return

    query = last_search.get("query", "")
    experience_min = last_search.get("experience_min", 0)
    experience_max = last_search.get("experience_max", 20)
    locations = last_search.get("locations")
    skills = last_search.get("skills")

    cache_key = f"{query}|{experience_min}|{experience_max}|{str(locations)}|{str(skills)}"

    # Indicador inmediato de "running": se muestra en el primer render de esta página,
    # antes de que el spinner arranque, llenando el hueco visual tras pulsar "Buscar".
    if st.session_state.get("_searching", False):
        st.info("🔍 Buscando candidatos — por favor espera...")

    # ── BÚSQUEDA ─────────────────────────────────────────────────────────────
    # Si no hay cache para esta consulta, ejecutar la búsqueda con spinner visible.
    # st.spinner() es el indicador de carga más fiable de Streamlit (desde v0.6):
    # muestra el spinner ANTES de ejecutar el bloque y lo oculta al terminar.
    if st.session_state.get("_results_cache_key") != cache_key:
        st.markdown(f"**Consulta:** _{query}_")
        with st.spinner("🔍 Buscando candidatos — generando embeddings y analizando CVs con IA..."):
            api_client = get_api_client()
            results = api_client.query_rag(
                query=query,
                experience_min=experience_min,
                experience_max=experience_max,
                locations=locations,
            )
            # Reintento silencioso ante arranque en frío de Qdrant
            if not results.get("candidates") and results.get("status") != "error":
                results = api_client.query_rag(
                    query=query,
                    experience_min=experience_min,
                    experience_max=experience_max,
                    locations=locations,
                )
        st.session_state["_results_cache"] = results
        st.session_state["_results_cache_key"] = cache_key
        # Liberar el botón "Buscar": la búsqueda ha terminado
        st.session_state["_searching"] = False
        st.rerun()
        return

    # ── RESULTADOS (cache hit) ────────────────────────────────────────────────
    results = st.session_state["_results_cache"]

    st.markdown(f"**Consulta:** _{query}_")
    _elapsed = results.get("metadata", {}).get("processing_time_ms", 0)
    if _elapsed:
        st.caption(f"⏱ Búsqueda completada en {_elapsed} ms")

    if results.get("status") == "error":
        st.error(f"Error al conectar con el servicio RAG: {results.get('message', 'Error desconocido')}")
        st.info("Comprueba que los servicios backend estan activos.")
        return
    if results.get("candidates"):
        st.success(f"Se encontraron {len(results['candidates'])} candidatos relevantes")
    else:
        st.warning("No se encontraron candidatos con los criterios especificados. Intenta una consulta diferente o sube mas CVs.")
        return

    st.divider()

    with st.expander("Parametros de la Busqueda"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Experiencia (anos)", f"{experience_min}-{experience_max}")
        with col2:
            locations_text = ", ".join(locations) if locations and isinstance(locations, (list, tuple)) else "Todas"
            st.write(f"**Ubicaciones:** {locations_text}")
        with col3:
            skills_count = len(skills) if skills and isinstance(skills, (list, tuple)) else 0
            st.write(f"**Habilidades filtradas:** {skills_count}")
        with col4:
            st.write(f"**Tiempo de busqueda:** {_elapsed}ms")

    st.divider()
    st.subheader("Candidatos Recomendados")
    candidates = results.get("candidates", [])
    for idx, candidate in enumerate(candidates, 1):
        _render_candidate_card(candidate, idx)

    st.divider()
    st.subheader("Acciones")
    col1, col2 = st.columns(2)
    with col1:
        report_text = _generate_report(query, candidates, results.get("metadata", {}))
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="Generar Reporte",
            data=report_text.encode("utf-8"),
            file_name=f"reporte_candidatos_{ts}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    action = st.session_state.pop("_action_msg", None)
    if action:
        kind, msg = action
        st.success(msg) if kind == "success" else st.info(msg)


def _generate_report(query: str, candidates: List[Dict[str, Any]], metadata: dict) -> str:
    """Genera un informe de texto con los candidatos encontrados."""
    lines = [
        "=" * 60,
        "REPORTE DE BUSQUEDA DE CANDIDATOS",
        "=" * 60,
        f"Fecha:    {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Consulta: {query}",
        f"Total candidatos encontrados: {len(candidates)}",
        "",
    ]
    for i, c in enumerate(candidates, 1):
        lines += [
            f"{'=' * 60}",
            f"#{i}  {c.get('name', 'N/A')}  —  Relevancia: {c.get('match_score', 0)}%",
            f"{'=' * 60}",
            f"  Email:        {c.get('email', 'N/A')}",
            f"  Telefono:     {c.get('phone', 'N/A')}",
            f"  Ubicacion:    {c.get('location', 'N/A')}",
            f"  Experiencia:  {c.get('experience_years', 0)} anos",
        ]
        skills = c.get("skills", [])
        if skills:
            lines.append(f"  Habilidades:  {', '.join(skills)}")
        summary = c.get("expertise_summary", "")
        if summary:
            lines.append(f"  Resumen:      {summary}")
        just = c.get("llm_justification", "")
        if just:
            lines += [
                "  Justificacion RAG:",
                f"    {just}",
            ]
        lines.append("")
    lines += [
        "=" * 60,
        "Generado por TalentRefineAI",
        "=" * 60,
    ]
    return "\n".join(lines)


def _render_candidate_card(candidate: Dict[str, Any], position: int):
    cid = candidate.get("id") or ""

    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"### #{position} {candidate.get('name', 'Sin nombre')}")
        with col2:
            match_score = candidate.get("match_score", 0)
            score_color = _get_score_color(match_score)
            st.markdown(
                f"<div style='text-align:right;font-weight:bold;color:{score_color};'>{match_score}%</div>",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(candidate.get("location", "N/A"))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Email:** `{candidate.get('email', 'N/A')}`")
            st.markdown(f"**Telefono:** {candidate.get('phone', 'N/A')}")
        with col2:
            st.markdown(f"**Experiencia:** {candidate.get('experience_years', 0)} anos")
            st.markdown(f"**Especializacion:** {candidate.get('expertise_summary', 'N/A')}")

        st.divider()
        st.markdown("**Habilidades Tecnicas:**")
        skills = candidate.get("skills", [])
        if skills:
            st.markdown(" ".join(f"`{s}`" for s in skills))

        st.divider()
        with st.expander("Justificacion del Analisis RAG"):
            st.markdown(candidate.get("llm_justification", "No disponible"))

        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            filename = candidate.get("document_name", "")
            if cid and filename:
                state_key = f"_cv_state_{cid}"
                bytes_key = f"_cv_bytes_{cid}"
                state = st.session_state.get(state_key, "idle")

                if state == "loading":
                    with st.spinner("Preparando el enlace de descarga..."):
                        pdf_bytes = get_api_client().download_cv(cid, filename)
                    st.session_state[bytes_key] = pdf_bytes
                    st.session_state[state_key] = "ready" if pdf_bytes else "error"
                    st.rerun()
                elif state == "ready":
                    st.download_button(
                        label="📥 Haz clic para descargar el PDF",
                        data=st.session_state[bytes_key],
                        file_name=filename,
                        mime="application/pdf",
                        key=f"dl_pdf_{cid}",
                        use_container_width=True,
                    )
                elif state == "error":
                    st.error("No se pudo cargar el PDF")
                    if st.button("Reintentar", key=f"retry_cv_{cid}", use_container_width=True):
                        del st.session_state[state_key]
                        st.rerun()
                else:  # idle
                    if st.button("Descargar PDF", key=f"dl_btn_{cid}", use_container_width=True):
                        st.session_state[state_key] = "loading"
                        st.rerun()
            else:
                st.caption("CV no disponible")

        with col2:
            if st.button("Contactar", key=f"contact_{cid}", use_container_width=True):
                st.session_state[f"_contact_{cid}"] = True
            if st.session_state.get(f"_contact_{cid}"):
                st.success(f"Email: {candidate.get('email', 'N/A')}")

        with col3:
            if st.button("Mas Info", key=f"more_info_{cid}", use_container_width=True):
                st.session_state[f"_show_more_{cid}"] = not st.session_state.get(f"_show_more_{cid}", False)
            if st.session_state.get(f"_show_more_{cid}"):
                st.info("\n".join([
                    "**Informacion Completa:**",
                    "- **ID:** " + cid,
                    "- **Documento:** " + str(candidate.get("document_name", "N/A")),
                    "- **Score:** " + str(candidate.get("match_score")) + "%",
                    "- **Email:** " + str(candidate.get("email", "N/A")),
                    "- **Telefono:** " + str(candidate.get("phone", "N/A")),
                    "- **Ubicacion:** " + str(candidate.get("location", "N/A")),
                    "- **Experiencia:** " + str(candidate.get("experience_years", 0)) + " anos",
                ]))

        st.divider()


def _get_score_color(score: int) -> str:
    if score >= 90:
        return "#00d084"
    elif score >= 80:
        return "#00c9b7"
    elif score >= 70:
        return "#fcb900"
    elif score >= 60:
        return "#ff6900"
    else:
        return "#cf2e2e"
