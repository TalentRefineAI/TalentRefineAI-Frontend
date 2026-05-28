#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Script de despliegue a Azure Container Apps para RAG-HR-Frontend
# ============================================================================
# Uso básico:
#export SUBSCRIPTION_ID="e9cbf006-1116-420a-8134-b19ed08a6302"
#export RESOURCE_GROUP="rg-talentrefine-front-dev-spc"
##export LOCATION="spaincentral"
#export CONTAINERAPP_ENV="cae-talentrefine-front-dev-spc"
#export APP_NAME="ca-frontend-talentrefine-dev-spc"
#export ACR_NAME="crtalentrefinefrontdevspc"
#export IMAGE_TAG="latest"
# ./deploy-azure-containerapp.sh
#
# Con Managed Identity y Key Vault:
#   export MANAGED_IDENTITY_NAME=<NOMBRE_IDENTIDAD>
#   export KEY_VAULT_NAME=<NOMBRE_KEY_VAULT>
#   export VAULT_SECRET_NAME=<NOMBRE_SECRETO_EN_KEYVAULT>
#   export CONTAINER_APP_SECRET_NAME=<NOMBRE_SECRET_CONTAINERAPP>
#
# Hacer esto de forma manual:

# 1. Crear el grupo de recursos en España Central
#az group create --name "rg-talentrefine-front-dev-spc" --location "spaincentral"
#
# 2. Crear tu propio registro de contenedores (ACR) en formato básico
#az acr create --resource-group "rg-talentrefine-front-dev-spc" --name "crtalentrefinefrontdevspc" --sku Basic
#
# 3. Habilitar las credenciales de administrador (Esencial para las líneas 94 y 95 de tu script)
#az acr update --name "crtalentrefinefrontdevspc" --admin-enabled true
#
============================================================================

ACR_NAME="${ACR_NAME:-<NOMBRE_ACR>}"
RESOURCE_GROUP="${RESOURCE_GROUP:-<GRUPO_RECURSOS>}"
LOCATION="${LOCATION:-<REGION>}"
CONTAINERAPP_ENV="${CONTAINERAPP_ENV:-<NOMBRE_ENTORNO_CONTAINERAPPS>}"
APP_NAME="${APP_NAME:-<NOMBRE_CONTAINER_APP>}"
SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-<SUBSCRIPTION_ID>}"
IMAGE_NAME="${IMAGE_NAME:-rag-hr-frontend}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ACR_LOGIN_SERVER="${ACR_LOGIN_SERVER:-${ACR_NAME}.azurecr.io}"
FULL_IMAGE_NAME="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"
MANAGED_IDENTITY_NAME="${MANAGED_IDENTITY_NAME:-<NOMBRE_IDENTIDAD>}"
KEY_VAULT_NAME="${KEY_VAULT_NAME:-<NOMBRE_KEY_VAULT>}"
VAULT_SECRET_NAME="${VAULT_SECRET_NAME:-<NOMBRE_SECRETO_EN_KEYVAULT>}"
CONTAINER_APP_SECRET_NAME="${CONTAINER_APP_SECRET_NAME:-<NOMBRE_SECRET_CONTAINERAPP>}"

function info() {
  printf "[INFO] %s\n" "$1"
}

function error_exit() {
  printf "[ERROR] %s\n" "$1" >&2
  exit 1
}

function require_cli() {
  command -v "$1" >/dev/null 2>&1 || error_exit "Necesito '$1' instalado y accesible en PATH."
}

function build_image() {
  info "Construyendo imagen Docker local..."
  docker build -t "$IMAGE_NAME:$IMAGE_TAG" .
}

function login_azure() {
  info "Iniciando sesión en Azure..."
  az login >/dev/null
  az account set --subscription "$SUBSCRIPTION_ID"
}

function login_acr() {
  info "Haciendo login en Azure Container Registry ($ACR_NAME)..."
  az acr login --name "$ACR_NAME"
}

function push_image() {
  info "Taggeando la imagen para ACR..."
  docker tag "$IMAGE_NAME:$IMAGE_TAG" "$FULL_IMAGE_NAME"
  info "Subiendo imagen a ACR: $FULL_IMAGE_NAME"
  docker push "$FULL_IMAGE_NAME"
}

function create_resource_group() {
  info "Creando o actualizando el resource group: $RESOURCE_GROUP"
  az group create --name "$RESOURCE_GROUP" --location "$LOCATION" >/dev/null
}

function create_containerapps_environment() {
  info "Creando o verificando el entorno de Container Apps: $CONTAINERAPP_ENV"
  az containerapp env create \
    --name "$CONTAINERAPP_ENV" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" >/dev/null
}

function deploy_container_app() {
  if az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    info "Actualizando Container App existente: $APP_NAME"
    az containerapp update \
      --name "$APP_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --image "$FULL_IMAGE_NAME" \
      --env-vars STREAMLIT_SERVER_PORT=8501 \
      --min-replicas 1 \
      --max-replicas 2 >/dev/null
  else
    info "Creando nueva Container App: $APP_NAME"
    az containerapp create \
      --name "$APP_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --environment "$CONTAINERAPP_ENV" \
      --image "$FULL_IMAGE_NAME" \
      --ingress external \
      --target-port 8501 \
      --min-replicas 1 \
      --max-replicas 2 \
      --env-vars STREAMLIT_SERVER_PORT=8501 \
      --registry-server "$ACR_LOGIN_SERVER" \
      --registry-username "$(az acr credential show --name "$ACR_NAME" --query username -o tsv)" \
      --registry-password "$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv)" >/dev/null
  fi
}

function create_managed_identity() {
  if [[ "$MANAGED_IDENTITY_NAME" == "<NOMBRE_IDENTIDAD>" ]]; then
    return
  fi

  info "Creando o usando Managed Identity: $MANAGED_IDENTITY_NAME"
  az identity create --name "$MANAGED_IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" >/dev/null || true
  local identity_id
  identity_id=$(az identity show --name "$MANAGED_IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query id -o tsv)
  echo "$identity_id"
}

function assign_keyvault_policy() {
  if [[ "$KEY_VAULT_NAME" == "<NOMBRE_KEY_VAULT>" ]] || [[ "$MANAGED_IDENTITY_NAME" == "<NOMBRE_IDENTIDAD>" ]]; then
    return
  fi

  info "Concediendo permisos GET al Key Vault: $KEY_VAULT_NAME"
  local principal_id
  principal_id=$(az identity show --name "$MANAGED_IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query principalId -o tsv)
  az keyvault set-policy \
    --name "$KEY_VAULT_NAME" \
    --object-id "$principal_id" \
    --secret-permissions get >/dev/null
}

function set_containerapp_secret_from_keyvault() {
  if [[ "$KEY_VAULT_NAME" == "<NOMBRE_KEY_VAULT>" ]] || [[ "$VAULT_SECRET_NAME" == "<NOMBRE_SECRETO_EN_KEYVAULT>" ]] || [[ "$CONTAINER_APP_SECRET_NAME" == "<NOMBRE_SECRET_CONTAINERAPP>" ]]; then
    return
  fi

  info "Obteniendo secreto de Key Vault: $VAULT_SECRET_NAME"
  local secret_value
  secret_value=$(az keyvault secret show --vault-name "$KEY_VAULT_NAME" --name "$VAULT_SECRET_NAME" --query value -o tsv)

  info "Registrando secreto en Container App como: $CONTAINER_APP_SECRET_NAME"
  az containerapp secret set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --secret "$CONTAINER_APP_SECRET_NAME=$secret_value" >/dev/null

  info "Asignando variable de entorno segura a la Container App"
  az containerapp update \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --env-vars "APP_SECRET=$CONTAINER_APP_SECRET_NAME" >/dev/null
}

function print_guidance() {
  cat <<EOF

Guía breve de variables de entorno y Key Vault para este frontend:

1) Local (.env)
   - Para desarrollo local puedes usar un archivo .env con variables como:
       STREAMLIT_SERVER_PORT=8501
       API_BASE_URL=https://api.tu-dominio.com
   - No subas .env a Git ni lo incluyas en la imagen de producción.

2) En Azure Container Apps
   - Usa env vars configuradas en la Container App, no un archivo .env dentro del contenedor.
   - Ejemplo de env var segura:
       az containerapp update --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --env-vars API_BASE_URL=https://api.tu-dominio.com

3) Inyección segura con Key Vault y Managed Identity
   - Crea una Managed Identity en Azure:
       az identity create --name "$MANAGED_IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION"
   - Asigna permisos GET al Key Vault:
       az keyvault set-policy --name "$KEY_VAULT_NAME" --object-id <IDENTITY_PRINCIPAL_ID> --secret-permissions get
   - Asigna la identidad a la Container App.
   - Dentro de la app, usa Azure SDK o Managed Identity para leer secretos de Key Vault en runtime.

4) Recomendación de implementación en el frontend
   - No guardes secretos en el código.
   - Usa variables de entorno COLOCADAS por Container Apps.
   - Para secretos críticos, guarda los valores en Key Vault y distribúyelos mediante Azure Managed Identity.

EOF
}

require_cli az
require_cli docker

build_image
#login_azure
login_acr
push_image
create_resource_group
create_containerapps_environment
create_managed_identity >/tmp/identity_id.txt || true
assign_keyvault_policy
deploy_container_app
set_containerapp_secret_from_keyvault
print_guidance

info "Despliegue completado. Revisa la URL de la Container App en Azure Portal o con:\n  az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv"
