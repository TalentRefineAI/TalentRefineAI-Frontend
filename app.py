"""
Frontend RAG para Selección de Personal - Aplicación Principal
"""

import streamlit as st
from components.upload_view import render_upload_view
from components.query_view import render_query_view
from components.results_view import render_results_view


# ============================================================================
# FE-01: CONFIGURACIÓN BASE
# ============================================================================

def _configure_page():
    st.set_page_config(
        page_title="RAG HR - Selección de Personal",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">""",
        unsafe_allow_html=True,
    )
    st.markdown("""<style>
h1, h2, h3 { color: #0d47a1; font-weight: 600; }
.stButton > button { border-radius: 6px; font-weight: 500; transition: all 0.3s ease; }
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
[data-testid="stMetricValue"] { color: #0d47a1; font-weight: 700; }
.footer { text-align: center; padding: 20px; margin-top: 40px; border-top: 1px solid #e0e0e0; color: #666; }
</style>""", unsafe_allow_html=True)


def _initialize_session_state():
    if "last_search" not in st.session_state:
        st.session_state["last_search"] = {
            "query": "",
            "experience_min": 0,
            "experience_max": 20,
            "locations": None,
            "skills": None,
            "should_search": False,
        }
    if "processing_files" not in st.session_state:
        st.session_state["processing_files"] = {}
    if "favorite_candidates" not in st.session_state:
        st.session_state["favorite_candidates"] = []
    # _page is the authoritative current-page state (NOT a widget key)
    if "_page" not in st.session_state:
        st.session_state["_page"] = "Subida de CVs"


def _on_nav_change():
    """Callback called by the sidebar radio when the user manually changes page."""
    st.session_state["_page"] = st.session_state["_nav_radio"]


def _render_sidebar():
    """Sidebar navigation. Uses on_change + index= to avoid widget-key conflicts."""
    has_results = st.session_state.get("last_search", {}).get("should_search", False)
    pages = ["Subida de CVs", "Búsqueda", "Resultados"] if has_results else ["Subida de CVs", "Búsqueda"]

    # Guard: _page points to Resultados but no search has been done yet
    current = st.session_state.get("_page", "Subida de CVs")
    if current not in pages:
        current = "Subida de CVs"
        st.session_state["_page"] = current

    with st.sidebar:
        st.markdown("# RAG HR")
        st.markdown("**Selección de Personal Inteligente**")
        st.markdown("---")
        st.markdown("### Navegación")
        st.radio(
            label="Selecciona una sección:",
            options=pages,
            index=pages.index(current),
            key="_nav_radio",
            on_change=_on_nav_change,
            label_visibility="collapsed",
        )
        st.markdown("---")

    return st.session_state["_page"]


def _render_main_content(page: str):
    if page == "Subida de CVs":
        render_upload_view()
    elif page == "Búsqueda":
        render_query_view()
    elif page == "Resultados":
        render_results_view()


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

def main():
    _configure_page()
    _initialize_session_state()

    st.markdown(
        """
        <div style='text-align:center;padding:20px;background:linear-gradient(135deg,#0d47a1 0%,#1976d2 100%);
        border-radius:10px;color:white;margin-bottom:30px;'>
            <h1 style='margin:0;color:white;'>RAG HR - Selección de Personal</h1>
            <p style='margin:10px 0 0 0;'>Búsqueda Inteligente de Candidatos con Inteligencia Artificial</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_page = _render_sidebar()
    _render_main_content(current_page)

    st.markdown(
        "<div class='footer'>© 2024 TalentRefineAI — Todos los derechos reservados</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
