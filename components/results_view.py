"""
Componente de resultados (FE-04).
Renderiza tarjetas dinamicas con candidatos clasificados por relevancia.
"""

import json
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from typing import Dict, List, Any
from utils.api_client import get_api_client


_SCROLL_JS = """
    <script>
      (function() {
        var selectors = [
          '[data-testid="stAppViewContainer"]',
          'section.main', '.main'
        ];
        for (var s of selectors) {
          var el = window.parent.document.querySelector(s);
          if (el) { el.scrollTo({top: 0, behavior: 'smooth'}); break; }
        }
        window.parent.scrollTo({top: 0, behavior: 'smooth'});
      })();
    </script>
    """


def render_results_view():
    st.header("Resultados de Búsqueda")

    last_search = st.session_state.get("last_search")
    if not isinstance(last_search, dict) or not last_search.get("should_search"):
        st.session_state["_searching"] = False
        return

    query = last_search.get("query", "")
    experience_min = last_search.get("experience_min", 0)
    experience_max = last_search.get("experience_max", 20)
    locations = last_search.get("locations")
    skills = last_search.get("skills")

    cache_key = f"{query}|{experience_min}|{experience_max}|{str(locations)}|{str(skills)}"

    # ── BÚSQUEDA ─────────────────────────────────────────────────────────────
    # _searching=True es el único trigger determinístico para ejecutar búsqueda.
    # Lo activa el botón Buscar (query_view.py) ANTES del st.rerun(), garantizando
    # que la búsqueda SIEMPRE se ejecuta exactamente una vez en este render.
    if st.session_state.get("_searching", False):
        st.markdown(f"**Consulta:** _{query}_")
        with st.status("🔍 Buscando candidatos...", expanded=True) as status_container:
            st.write("Generando embeddings y analizando CVs con IA (puede tardar 30-60s en primer acceso)...")
            api_client = get_api_client()
            results = api_client.query_rag(
                query=query,
                experience_min=experience_min,
                experience_max=experience_max,
                locations=locations,
            )
            if not results.get("candidates") and results.get("status") != "error":
                st.write("Qdrant en arranque en frío, reintentando...")
                results = api_client.query_rag(
                    query=query,
                    experience_min=experience_min,
                    experience_max=experience_max,
                    locations=locations,
                )
            if results.get("status") == "error":
                status_container.update(label="Error en la búsqueda", state="error")
            else:
                status_container.update(label="✅ Búsqueda completada", state="complete")

        # Scroll to top right after the search completes (not on every subsequent rerun)
        components.html(_SCROLL_JS, height=0)

        # Cache the results and mark search as complete
        st.session_state["_results_cache"] = results
        st.session_state["_results_cache_key"] = cache_key
        st.session_state["_searching"] = False

        # NO st.rerun() — results render directly below the completed st.status

    # ── RESULTADOS (mostrar resultados en cache) ──────────────────────────────
    results = st.session_state.get("_results_cache")
    if not results:
        st.session_state["_searching"] = False
        return

    st.markdown(f"**Consulta:** _{query}_")
    _elapsed = results.get("metadata", {}).get("processing_time_ms", 0)
    if _elapsed:
        st.caption(f"⏱ Búsqueda completada en {_elapsed} ms")

    if results.get("status") == "error":
        st.error(f"Error al conectar con el servicio RAG: {results.get('message', 'Error desconocido')}")
        st.info("Comprueba que los servicios backend estan activos.")
        st.session_state["_searching"] = False
        return
    if results.get("candidates"):
        st.success(f"Se encontraron {len(results['candidates'])} candidatos relevantes")
    else:
        st.warning("No se encontraron candidatos con los criterios especificados. Intenta una consulta diferente o sube mas CVs.")
        st.session_state["_searching"] = False
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
        report_json = _generate_report_json(
            query, candidates, results.get("metadata", {}),
            experience_min, experience_max, locations, skills,
        )
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="Generar Reporte (JSON)",
            data=report_json.encode("utf-8"),
            file_name=f"reporte_candidatos_{ts}.json",
            mime="application/json",
            use_container_width=True,
        )

    action = st.session_state.pop("_action_msg", None)
    if action:
        kind, msg = action
        st.success(msg) if kind == "success" else st.info(msg)

    # Final safeguard: ensure _searching is False when exiting normally
    st.session_state["_searching"] = False


def _generate_report_json(
    query: str,
    candidates: List[Dict[str, Any]],
    metadata: dict,
    experience_min: int,
    experience_max: int,
    locations: Any,
    skills: Any,
) -> str:
    """Genera un reporte JSON estructurado de la búsqueda, pensado para reutilizarse
    como dataset de entrenamiento (query + filtros + candidatos con score y análisis LLM).
    """
    report = {
        "schema_version": "1.0",
        "report_type": "candidate_search_result",
        "generated_at": datetime.now().isoformat(),
        "query": {
            "job_description": query,
            "filters": {
                "experience_min": experience_min,
                "experience_max": experience_max,
                "locations": list(locations) if locations else None,
                "skills": list(skills) if skills else None,
            },
        },
        "search_metadata": {
            "total_results": len(candidates),
            "processing_time_ms": metadata.get("processing_time_ms", 0),
        },
        "candidates": [
            {
                "rank": i,
                "candidate_id": c.get("id", ""),
                "document_name": c.get("document_name", ""),
                "match_score": c.get("match_score", 0),
                "profile": {
                    "name": c.get("name", ""),
                    "email": c.get("email", ""),
                    "phone": c.get("phone", ""),
                    "location": c.get("location", ""),
                    "experience_years": c.get("experience_years", 0),
                    "skills": c.get("skills", []),
                },
                "llm_analysis": {
                    "expertise_summary": c.get("expertise_summary", ""),
                    "justification": c.get("llm_justification", ""),
                },
            }
            for i, c in enumerate(candidates, 1)
        ],
    }
    return json.dumps(report, ensure_ascii=False, indent=2)


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
