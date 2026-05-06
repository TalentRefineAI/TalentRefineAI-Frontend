"""
Frontend RAG para Selección de Personal - Aplicación Principal
===============================================================

Aplicación de Streamlit para gestión inteligente de candidatos usando
Retrieval-Augmented Generation (RAG).

Autor: DevOps Team
Versión: 1.0.0
Fase: Hito Intermedio (datos simulados - mocks)

Características:
- FE-01: Configuración base con tema y navegación en sidebar
- FE-02: Vista de subida de CVs con Drag & Drop y progreso
- FE-03: Vista de consulta con filtros y búsqueda semántica
- FE-04: Vista de resultados con tarjetas de candidatos
- FE-05: Cliente API preparado para integración en Fase 2
"""

import streamlit as st
from components.upload_view import render_upload_view
from components.query_view import render_query_view
from components.results_view import render_results_view


# ============================================================================
# FE-01: CONFIGURACIÓN BASE DE STREAMLIT
# ============================================================================

def _configure_page():
    """Configura la página de Streamlit con tema y metadata."""
    st.set_page_config(
        page_title="RAG HR - Selección de Personal",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/your-org/rag-hr-frontend",
            "Report a bug": "https://github.com/your-org/rag-hr-frontend/issues",
            "About": "RAG HR Frontend v1.0.0 - Hito Intermedio"
        }
    )
    
    # Configurar tema visual con CSS
    st.markdown("""
    <style>
    /* Variables de color */
    :root {
        --primary-color: #0d47a1;
        --secondary-color: #1976d2;
        --success-color: #00c9b7;
        --danger-color: #ff6b6b;
        --warning-color: #ffa500;
    }
    
    /* Estilos generales */
    .main {
        padding-top: 2rem;
    }
    
    /* Estilos para headers */
    h1, h2, h3 {
        color: #0d47a1;
        font-weight: 600;
    }
    
    /* Estilos para containers */
    .stContainer {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Estilos para botones */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Estilos para expanders */
    .streamlit-expander {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
    }
    
    /* Estilos para métricos */
    [data-testid="stMetricValue"] {
        color: #0d47a1;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)


def _initialize_session_state():
    """Inicializa las variables de sesión necesarias."""
    if "last_search" not in st.session_state:
        st.session_state.last_search = None
    
    if "processing_files" not in st.session_state:
        st.session_state.processing_files = {}
    
    if "favorite_candidates" not in st.session_state:
        st.session_state.favorite_candidates = []


def _render_sidebar():
    """Crea la navegación en la barra lateral."""
    with st.sidebar:
        # Logo y branding
        st.markdown("# 🎯 RAG HR")
        st.markdown("**Selección de Personal Inteligente**")
        st.markdown("---")
        
        # Navegación principal
        st.markdown("### 📍 Navegación")
        current_page = st.radio(
            label="Selecciona una sección:",
            options=["📄 Subida de CVs", "🔍 Búsqueda", "🏆 Resultados"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Información de la sesión
        st.markdown("### 📊 Estadísticas de Sesión")
        
        col1, col2 = st.columns(2)
        with col1:
            num_files = len(st.session_state.processing_files)
            st.metric("CVs Cargados", num_files)
        
        with col2:
            num_favorites = len(st.session_state.favorite_candidates)
            st.metric("Favoritos", num_favorites)
        
        st.markdown("---")
        
        # Información sobre la API
        st.markdown("### ⚙️ Configuración")
        
        with st.expander("🔧 Configuración Avanzada"):
            api_mode = st.selectbox(
                "Modo de API:",
                options=["Mocks (Desarrollo)", "API Real (Producción)"],
                help="En desarrollo se usan datos simulados. En producción se conecta a FastAPI."
            )
            
            if api_mode == "API Real (Producción)":
                api_url = st.text_input(
                    "URL de la API:",
                    value="http://localhost:8000",
                    help="URL base del servidor FastAPI"
                )
                st.caption(f"Conectando a: {api_url}")
        
        st.markdown("---")
        
        # Pie de página
        st.markdown("### 📝 Información")
        st.markdown(
            """
            **RAG HR Frontend v1.0.0**
            
            Hito Intermedio - Fase 1
            
            📧 [Contacto](mailto:support@example.com)
            🐛 [Reportar Bug](https://github.com/your-org/issues)
            📖 [Documentación](https://docs.example.com)
            """
        )
        
        st.markdown("---")
        st.caption("© 2024 DevOps Team - Todos los derechos reservados")
    
    return current_page


def _render_main_content(page: str):
    """Renderiza el contenido principal según la página seleccionada."""
    
    if page == "📄 Subida de CVs":
        render_upload_view()
    
    elif page == "🔍 Búsqueda":
        render_query_view()
    
    elif page == "🏆 Resultados":
        render_results_view()


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

def main():
    """Función principal de la aplicación."""
    
    # Ejecutar configuraciones iniciales
    _configure_page()
    _initialize_session_state()
    
    # Renderizar header principal
    st.markdown(
        """
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); 
        border-radius: 10px; color: white; margin-bottom: 30px;'>
            <h1 style='margin: 0; color: white;'>🎯 RAG HR - Selección de Personal</h1>
            <p style='margin: 10px 0 0 0;'>Búsqueda Inteligente de Candidatos con Inteligencia Artificial</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Renderizar sidebar y obtener página actual
    current_page = _render_sidebar()
    
    # Renderizar contenido principal
    _render_main_content(current_page)
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🚀 Tecnología: Streamlit + FastAPI + LLM")
    with col2:
        st.caption("📦 Versión: 1.0.0 (Hito Intermedio)")
    with col3:
        st.caption("🔐 Modo: Desarrollo (Mocks)")


if __name__ == "__main__":
    main()
