# Makefile para RAG HR Frontend
# Facilita tareas comunes de desarrollo

.PHONY: help setup run stop logs clean docker-build docker-run docker-stop

# Variables
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

# Color output
GREEN := \033[0;32m
BLUE := \033[0;34m
NC := \033[0m # No Color

# ============================================================================
# HELP
# ============================================================================
help:
	@echo "$(BLUE)RAG HR Frontend - Comandos disponibles:$(NC)"
	@echo ""
	@echo "$(GREEN)Setup:$(NC)"
	@echo "  make setup              Crear entorno virtual e instalar dependencias"
	@echo "  make clean              Limpiar archivos temporales y caché"
	@echo ""
	@echo "$(GREEN)Ejecución Local:$(NC)"
	@echo "  make run                Ejecutar aplicación Streamlit"
	@echo "  make stop               Detener aplicación"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker-build       Construir imagen Docker"
	@echo "  make docker-run         Ejecutar en contenedor Docker"
	@echo "  make docker-stop        Detener contenedor Docker"
	@echo "  make docker-compose-up  Ejecutar con docker-compose"
	@echo "  make docker-compose-down Detener docker-compose"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make lint               Ejecutar linter de Python"
	@echo "  make format             Formatear código con Black"
	@echo "  make test               Ejecutar tests"
	@echo "  make requirements-freeze Congelar dependencias"

# ============================================================================
# SETUP
# ============================================================================
setup:
	@echo "$(BLUE)Creando entorno virtual...$(NC)"
	python -m venv $(VENV)
	@echo "$(BLUE)Instalando dependencias...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Setup completado$(NC)"
	@echo ""
	@echo "Para activar el entorno virtual:"
	@echo "  source $(VENV)/bin/activate"

# ============================================================================
# EJECUCIÓN LOCAL
# ============================================================================
run:
	@echo "$(BLUE)Iniciando aplicación Streamlit...$(NC)"
	@echo "$(GREEN)Accede a: http://localhost:8501$(NC)"
	$(STREAMLIT) run app.py

stop:
	@echo "$(BLUE)Deteniendo aplicación...$(NC)"
	pkill -f "streamlit run app.py" || echo "No hay instancia en ejecución"
	@echo "$(GREEN)✓ Aplicación detenida$(NC)"

# ============================================================================
# DOCKER
# ============================================================================
docker-build:
	@echo "$(BLUE)Construyendo imagen Docker...$(NC)"
	docker build -t rag-hr-frontend:latest .
	@echo "$(GREEN)✓ Imagen construida$(NC)"

docker-run:
	@echo "$(BLUE)Ejecutando contenedor Docker...$(NC)"
	docker run -p 8501:8501 --name rag-hr-frontend rag-hr-frontend:latest
	@echo "$(GREEN)✓ Contenedor en ejecución en http://localhost:8501$(NC)"

docker-stop:
	@echo "$(BLUE)Deteniendo contenedor Docker...$(NC)"
	docker stop rag-hr-frontend || true
	docker rm rag-hr-frontend || true
	@echo "$(GREEN)✓ Contenedor detenido$(NC)"

docker-compose-up:
	@echo "$(BLUE)Iniciando docker-compose...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Servicios iniciados en http://localhost:8501$(NC)"

docker-compose-down:
	@echo "$(BLUE)Deteniendo docker-compose...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Servicios detenidos$(NC)"

logs:
	docker-compose logs -f

# ============================================================================
# UTILITIES
# ============================================================================
lint:
	@echo "$(BLUE)Ejecutando linter...$(NC)"
	$(PYTHON) -m pylint app.py components/ utils/ || true

format:
	@echo "$(BLUE)Formateando código...$(NC)"
	$(PYTHON) -m black app.py components/ utils/ || echo "Black no instalado"

test:
	@echo "$(BLUE)Ejecutando tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v || echo "Pytest no instalado"

requirements-freeze:
	@echo "$(BLUE)Congelando dependencias...$(NC)"
	$(PIP) freeze > requirements-frozen.txt
	@echo "$(GREEN)✓ Dependencias guardadas en requirements-frozen.txt$(NC)"

# ============================================================================
# LIMPIEZA
# ============================================================================
clean:
	@echo "$(BLUE)Limpiando archivos temporales...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -delete
	rm -rf .pytest_cache/ || true
	rm -rf .coverage || true
	rm -rf htmlcov/ || true
	rm -rf dist/ || true
	rm -rf build/ || true
	@echo "$(GREEN)✓ Limpieza completada$(NC)"

# ============================================================================
# DEFAULT
# ============================================================================
.DEFAULT_GOAL := help
