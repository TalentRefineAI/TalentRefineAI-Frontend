# 🎯 RAG HR Frontend - Selección de Personal Inteligente

Frontend moderno basado en **Streamlit** para una aplicación de Retrieval-Augmented Generation (RAG) orientada a la selección de personal. 

## 📋 Descripción General

Esta aplicación implementa una interfaz intuitiva para:
- **Subida de CVs**: Carga múltiples documentos PDF con Drag & Drop
- **Búsqueda Semántica**: Consulta natural con filtros avanzados
- **Ranking de Candidatos**: Resultados ordenados por relevancia con justificaciones del LLM
- **Gestión de Candidatos**: Marcar favoritos, contactar, generar reportes

## 🎯 Objetivos del Hito Intermedio

✅ Interface navegable con todas las vistas implementadas  
✅ Datos simulados (mocks) funcionales para UI/UX fluida  
✅ Modularidad y separación de responsabilidades  
✅ Preparado para integración de API real en Fase 2  
✅ Código comentado y estructurado  
✅ Dockerfile listo para despliegue  

## 📁 Estructura del Proyecto

```
RAG-HR-Frontend/
├── app.py                          # Aplicación principal de Streamlit
├── requirements.txt                # Dependencias Python
├── Dockerfile                      # Dockerfile para containerización
├── docker-compose.yml              # Composición de servicios (opcional)
│
├── components/                     # Componentes de UI reutilizables
│   ├── __init__.py
│   ├── upload_view.py             # FE-02: Vista de subida de CVs
│   ├── query_view.py              # FE-03: Vista de consulta
│   └── results_view.py            # FE-04: Vista de resultados
│
└── utils/                          # Utilidades y funciones auxiliares
    ├── __init__.py
    ├── api_client.py              # FE-05: Cliente HTTP con mocks
    └── mock_data.py               # Datos simulados para desarrollo
```

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Python 3.10+
- pip o conda
- Git

### Paso 1: Clonar o Descargar el Proyecto

```bash
cd /home/juakijs
# El proyecto está en RAG-HR-Frontend/
```

### Paso 2: Crear Entorno Virtual

```bash
cd RAG-HR-Frontend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501` automáticamente.

## 🐳 Dockerización

### Opción 1: Usar Docker Directamente

```bash
# Construir imagen
docker build -t rag-hr-frontend:latest .

# Ejecutar contenedor
docker run -p 8501:8501 rag-hr-frontend:latest

# Acceder en http://localhost:8501
```

### Opción 2: Usar Docker Compose

```bash
docker-compose up

# Acceder en http://localhost:8501
```

## 📚 Funcionalidades Implementadas

### FE-01: Configuración Base ✅
- ✓ Inicialización de Streamlit con tema personalizado
- ✓ Navegación en sidebar con 3 secciones principales
- ✓ Session state management
- ✓ Responsivo en dispositivos móviles

### FE-02: Vista de Subida de CVs ✅
- ✓ Drag & Drop para múltiples archivos PDF
- ✓ Barra de progreso simulada por documento
- ✓ Estados: Pendiente → Procesando → Completado
- ✓ Estadísticas de carga en tiempo real
- ✓ Manejo de errores

### FE-03: Vista de Consulta ✅
- ✓ Slider para seleccionar años de experiencia (min/max)
- ✓ Multiselect para ubicaciones preferidas
- ✓ Multiselect para habilidades técnicas requeridas
- ✓ Área de texto libre para consulta semántica
- ✓ Ejemplos de consultas útiles
- ✓ Validación de formulario

### FE-04: Vista de Resultados ✅
- ✓ Tarjetas dinámicas de candidatos
- ✓ Ranking con score de relevancia (0-100%)
- ✓ Habilidades técnicas como badges
- ✓ Justificación generada por el LLM (expandible)
- ✓ Botones de acción: Ver CV, Contactar, Favorito, Más Info
- ✓ Información de metadatos de la búsqueda

### FE-05: Cliente API ✅
- ✓ Clase `RAGAPIClient` preparada para FastAPI
- ✓ Métodos implementados: `upload_cv_documents()`, `query_rag()`, `get_candidate_details()`
- ✓ Modo mock/real intercambiable
- ✓ Manejo de errores y fallbacks
- ✓ Session HTTP con reintentos

## 🔄 Flujo de Uso

1. **Subida de CVs**: El reclutador sube 1 o más CVs en PDF
2. **Búsqueda**: Define criterios (experiencia, ubicación) y escribe consulta semántica
3. **Resultados**: Sistema retorna candidatos rankeados por relevancia
4. **Acciones**: Contactar, guardar favoritos, generar reportes

## 📊 Datos Simulados (Mocks)

La aplicación incluye 6 candidatos simulados con perfiles diversos:

| Candidato               | Experiencia | Ubicación | Habilidades          | Score |
| ----------------------- | ----------- | --------- | -------------------- | ----- |
| María García López      | 7 años      | Madrid    | Python, FastAPI, AWS | 95%   |
| Juan Rodríguez Martínez | 5 años      | Barcelona | React, JavaScript    | 82%   |
| Ana Fernández Pérez     | 8 años      | Valencia  | DevOps, Kubernetes   | 88%   |
| Carlos López Jiménez    | 6 años      | Madrid    | Data Science, ML     | 80%   |
| Sofía González Ruiz     | 4 años      | Bilbao    | QA, Automation       | 75%   |
| Miguel Sánchez Torres   | 9 años      | Madrid    | System Architecture  | 92%   |

## 🔌 Integración con API Real (Fase 2)

Para conectar con la API de FastAPI en la Fase 2:

1. **En `utils/api_client.py`**: Cambiar `use_mock=False`
2. **Configurar URL base**: 
   ```python
   client = RAGAPIClient(base_url="http://api.server:8000", use_mock=False)
   ```
3. **Los endpoints esperados**:
   - `POST /api/v1/documents/upload`
   - `POST /api/v1/rag/query`
   - `GET /api/v1/candidates/{id}`
   - `GET /api/v1/documents/status`
   - `GET /api/v1/filters/locations`
   - `GET /api/v1/filters/skills`

## 🎨 Tema y Personalización

El tema visual se configura en `app.py`. Puedes personalizar:

```python
# Colores
--primary-color: #0d47a1      # Azul marino
--secondary-color: #1976d2    # Azul
--success-color: #00c9b7      # Verde
--danger-color: #ff6b6b       # Rojo
--warning-color: #ffa500      # Naranja
```

## 📦 Dependencias

| Librería      | Versión | Propósito                        |
| ------------- | ------- | -------------------------------- |
| streamlit     | 1.28.1  | Framework web principal          |
| requests      | 2.31.0  | Cliente HTTP para API            |
| python-dotenv | 1.0.0   | Gestión de variables de entorno  |
| pandas        | 2.1.1   | Análisis y manipulación de datos |
| pillow        | 10.0.1  | Procesamiento de imágenes        |

## 🔒 Variables de Entorno (Fase 2)

Crear archivo `.env`:

```env
API_URL=http://localhost:8000
API_TIMEOUT=30
LOG_LEVEL=INFO
DEBUG_MODE=False
USE_MOCK_DATA=True
```

## 📝 Comentarios en el Código

Todos los archivos están ampliamente documentados con:
- Docstrings en módulos, clases y funciones
- Comentarios inline para lógica compleja
- Type hints para claridad
- Ejemplos de uso

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### Error: "Conexión rechazada a localhost:8501"
- Asegúrate de estar en el directorio correcto
- Ejecuta: `streamlit run app.py`

### Los mocks no se cargan correctamente
- Verifica que `utils/mock_data.py` exista
- Importa correctamente: `from utils.mock_data import ...`

## 🚀 Próximos Pasos (Fase 2)

- [ ] Integración con API FastAPI real

## 👨‍💻 Contribuyentes

- DevOps Team

## 📄 Licencia

MIT License - Ver LICENSE.md

## 📧 Contacto y Soporte

- Email: support@example.com
- Issues: https://github.com/your-org/rag-hr-frontend/issues
- Wiki: https://docs.example.com

---

**Última actualización:** 2024  
**Estado:** Hito Intermedio - Fase 1 Completada ✅
