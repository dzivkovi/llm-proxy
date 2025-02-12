#!/bin/bash
# Local server execution:
#   python -m app.mock_server  # Use mock_server.py for testing
#
# Azure server deployment using "az webapp up" command:

# Load configuration from environment file
if [ -f .env ]; then
    source ./.env
else
    echo "Error: .env file not found"
    echo "Please create .env file with required variables"
    exit 1
fi

# Required environment variables with defaults
: "${AZURE_SUBSCRIPTION_ID:?'AZURE_SUBSCRIPTION_ID is required'}"
: "${AZURE_RESOURCE_GROUP:=MyResourceGroup}"
: "${AZURE_LOCATION:=eastus}"
: "${AZURE_APP_NAME:=mock-service-demo}"
: "${AZURE_SKU:=B1}"
: "${AZURE_RUNTIME:=PYTHON|3.11}"

# Set the correct subscription
echo "Setting subscription..."
az account set --subscription "$AZURE_SUBSCRIPTION_ID"

# Verify subscription
echo "Verifying subscription..."
az account show --output table

# Create resource group
echo "Creating resource group..."
az group create --name "$AZURE_RESOURCE_GROUP" --location "$AZURE_LOCATION"

# Create the web app
echo "Creating and deploying web app..."
az webapp up \
  --name "$AZURE_APP_NAME" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --runtime "$AZURE_RUNTIME" \
  --sku "$AZURE_SKU"

# Configure startup command from startup.txt
echo "Setting startup command..."
STARTUP_COMMAND=$(cat startup.txt)
az webapp config set \
  --name "$AZURE_APP_NAME" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --generic-configurations "{'appCommandLine': '$STARTUP_COMMAND'}"

# Wait for deployment
echo "Waiting for deployment to complete..."
sleep 30

# Verify deployment
echo "Verifying deployment..."
az webapp log tail --name "$AZURE_APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP"