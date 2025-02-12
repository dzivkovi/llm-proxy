# Azure Web App Deployment Guide

This guide covers deploying a Python Flask application to Azure Web Apps using buildpacks - a modern approach that automates container creation and standardizes deployment processes.

## About Azure Buildpacks

Azure Web Apps uses [Cloud Native Buildpacks](https://buildpacks.io/) through [Oryx](https://github.com/microsoft/Oryx) to automatically detect and build applications. This approach offers:

- **Automated Container Management**:

  - Eliminates error-prone Dockerfile maintenance
  - Standardizes build process across applications
  - Reduces deployment inconsistencies
- **Automated Build Process**:
  - Detects Python/Flask applications automatically
  - Installs dependencies from `requirements.txt`
  - Configures Gunicorn and other runtime components
- **Enterprise-Ready**:

  - Uses hardened container images
  - Maintains latest security patches
  - Simplified deployment and updates

Learn more about buildpacks:

- [Azure App Service Python Guide](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python) - Official Python deployment guide
- [Build and push an image from an app using a Cloud Native Buildpack](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tasks-pack-build) - Azure's buildpack implementation
- [Why Cloud Native Buildpacks?](https://buildpacks.io/)

## Prerequisites

1. Install Azure CLI:

    ```powershell
    winget install -e --id Microsoft.AzureCLI
    ```

2. Login to Azure:

    ```bash
    az login
    ```

3. List available subscriptions:

    ```bash
    az account list --output table
    ```

4. Get current subscription:

    ```bash
    az account show --output table
    ```

## Environment Setup

1. Copy the sample environment file:

    ```bash
    cp .env.sample .env
    ```

2. Get required Azure values:

    ```bash
    # Get subscription ID
    az account show --query id --output tsv

    # List available locations
    az account list-locations --output table

    # List available SKUs
    az appservice plan create --help
    ```

3. Update `.env` file:

    ```bash
    AZURE_APP_NAME=mock-service-demo              # Your choice (must be unique)
    AZURE_SUBSCRIPTION_ID="your-subscription-id"  # From az account show
    AZURE_RESOURCE_GROUP="your-resource-group"    # Your choice
    AZURE_LOCATION="eastus"                       # From locations list
    AZURE_SKU="B1"                                # Basic tier
    AZURE_RUNTIME="PYTHON|3.11"                   # Python version
    ```

## Deployment

1. Ensure you have required files:

    ```text
    llm-proxy/
    ├── app/
    │   ├── __init__.py
    │   └── mock_server.py
    ├── requirements.txt
    ├── startup.txt
    └── start_server.sh
    ```

2. Run deployment script:

    ```bash
    chmod +x start_server.sh
    ./start_server.sh
    ```

## Usage

### API Tests

1. **Basic Chat Completion**:

    ```bash
    curl -X POST "https://mock-service-demo.azurewebsites.net/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer dummy-key" \
    -d '{
        "messages": [
        {
            "role": "user",
            "content": "Hello"
        }
        ],
        "model": "gpt-3.5-turbo"
    }'
    ```

2. **Streaming Response**:

    ```bash
    curl -X POST "https://mock-service-demo.azurewebsites.net/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer dummy-key" \
    -d '{
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello!"}],
        "stream": true
    }'
    ```

### Continue.dev Integration

Add to your Continue configuration:

```bash
{
    "title": "Azure Mock GPT",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "apiKey": "dummy-key",
    "apiBase": "https://mock-service-demo.azurewebsites.net/v1",
    "useLegacyCompletionsEndpoint": false
},
```

## Security

Verify service access restrictions:

```bash
az webapp config access-restriction show \
  --name mock-service-demo \
  --resource-group "your-resource-group"
```

Restrict access to your IP address:

```bash
# Get your public IP
MY_IP=$(curl -s https://api.ipify.org)

# Add IP restriction
az webapp config access-restriction add \
  --name mock-service-demo \
  --resource-group "your-resource-group" \
  --rule-name 'Allow my IP' \
  --action Allow \
  --ip-address "${MY_IP}/32" \
  --priority 100
```

## Cost Management

Since B1 SKU is not serverless, manage costs by stopping/starting the service:

```bash
# Stop the web app
az webapp stop --name mock-service-demo --resource-group "your-resource-group"

# Start the web app
az webapp start --name mock-service-demo --resource-group "your-resource-group"
```

## Cleanup

To completely remove the deployment:

```bash
# Delete the web app
az webapp delete --name mock-service-demo --resource-group "your-resource-group"

# Optional: Delete the resource group and all resources
az group delete --name "your-resource-group" --yes --no-wait
```

## Troubleshooting

View application logs:

```bash
az webapp log tail --name mock-service-demo --resource-group "your-resource-group"
```

Check deployment status:

```bash
az webapp show --name mock-service-demo --resource-group "your-resource-group" --query "state"
```

## Notes

- The B1 SKU costs approximately $0.075 per hour ($54.75/month)
- Service runs continuously unless stopped
- Consider F1 (Free) tier for testing, but with limitations
- IP restrictions might need updates if your IP changes
