#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Script para construir y subir imagen al ACR existente en rg-talentrefine-dev-spc
# ============================================================================
# Valores por defecto para esta suscripción y el ACR existente en España Central.
# Ejecuta: ./deploy-azure-containerapp.sh
#============================================================================

ACR_NAME="${ACR_NAME:-crtalentrefinedevspc}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-talentrefine-dev-spc}"
LOCATION="${LOCATION:-spaincentral}"
SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-0aa15e59-d4de-4ba4-b34a-e238fdaae696}"
IMAGE_NAME="${IMAGE_NAME:-rag-hr-frontend}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ACR_LOGIN_SERVER="${ACR_LOGIN_SERVER:-${ACR_NAME}.azurecr.io}"
FULL_IMAGE_NAME="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

info() {
  printf "[INFO] %s\n" "$1"
}

error_exit() {
  printf "[ERROR] %s\n" "$1" >&2
  exit 1
}

require_cli() {
  command -v "$1" >/dev/null 2>&1 || error_exit "Necesito '$1' instalado y accesible en PATH."
}

build_image() {
  info "Construyendo imagen Docker local..."
  docker build -t "$IMAGE_NAME:$IMAGE_TAG" .
}

login_acr() {
  info "Haciendo login en Azure Container Registry ($ACR_NAME)..."
  az acr login --name "$ACR_NAME"
}

verify_acr_exists() {
  info "Verificando que el ACR exista: $ACR_NAME"
  if ! az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    error_exit "El ACR '$ACR_NAME' no existe en el grupo de recursos '$RESOURCE_GROUP'."
  fi
}

push_image() {
  info "Taggeando la imagen para ACR..."
  docker tag "$IMAGE_NAME:$IMAGE_TAG" "$FULL_IMAGE_NAME"
  info "Subiendo imagen a ACR: $FULL_IMAGE_NAME"
  docker push "$FULL_IMAGE_NAME"
}

print_guidance() {
  cat <<EOF

Guía breve de despliegue de imagen a Azure Container Registry:

1) Local (.env)
   - Para desarrollo local puedes usar un archivo .env con variables como:
       STREAMLIT_SERVER_PORT=8501
       API_BASE_URL=https://api.tu-dominio.com
   - No subas .env a Git ni lo incluyas en la imagen de producción.

2) Azure Container Registry
   - La imagen se sube a: $FULL_IMAGE_NAME
   - Verifica el repositorio en Azure Portal o con:
       az acr repository list --name "$ACR_NAME" -o table

3) Para desplegar la imagen en cualquier servicio
   - Usa el nombre completo de la imagen:
       $FULL_IMAGE_NAME
   - Aplica esa imagen en tu servicio de Azure o Kubernetes según tu arquitectura.

EOF
}

require_cli az
require_cli docker

build_image
login_acr
verify_acr_exists
push_image
print_guidance

info "Imagen subida correctamente a: $FULL_IMAGE_NAME"
