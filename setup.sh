#!/bin/bash

# Script de Setup para RAG HR Frontend
# Uso: bash setup.sh

set -e  # Salir si hay error

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Main
print_header "RAG HR Frontend - Setup"

# Verificar Python
print_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION encontrado"

# Crear virtualenv
print_info "Creando entorno virtual..."
if [ -d "venv" ]; then
    print_info "El directorio venv ya existe"
    read -p "¿Deseas eliminarlo y crear uno nuevo? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Entorno virtual creado"
    fi
else
    python3 -m venv venv
    print_success "Entorno virtual creado"
fi

# Activar virtualenv
print_info "Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"

# Actualizar pip
print_info "Actualizando pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
print_success "pip actualizado"

# Instalar dependencias
print_info "Instalando dependencias..."
pip install -r requirements.txt > /dev/null 2>&1
print_success "Dependencias instaladas"

# Crear .env si no existe
if [ ! -f ".env" ]; then
    print_info "Creando archivo .env..."
    cp .env.example .env
    print_success "Archivo .env creado (edita con tus valores)"
fi

# Crear carpeta uploads si no existe
if [ ! -d "uploads" ]; then
    mkdir -p uploads
    print_success "Carpeta uploads creada"
fi

# Summary
echo ""
print_header "Setup Completado!"
echo ""
echo -e "${GREEN}Para ejecutar la aplicación:${NC}"
echo ""
echo "  1. Activar entorno virtual:"
echo "     ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "  2. Ejecutar aplicación:"
echo "     ${YELLOW}streamlit run app.py${NC}"
echo ""
echo "  La aplicación estará disponible en:"
echo "     ${BLUE}http://localhost:8501${NC}"
echo ""
echo -e "${GREEN}O usa Docker:${NC}"
echo ""
echo "  ${YELLOW}docker build -t rag-hr-frontend:latest .${NC}"
echo "  ${YELLOW}docker run -p 8501:8501 rag-hr-frontend:latest${NC}"
echo ""
print_info "Para más información, ver README.md"
