# create zip archive locally
data "archive_file" "dev-experiment-monolith-function-code" {
  type = "zip"
  source_dir = "function_code/dev-experiment-monolith"
  output_path = "function1.zip"
}

# upload zip archive to storage contianer
resource "azurerm_storage_blob" "dev-experiment-monolith-code" {
  name = "dev-experiment-monolith-function.zip"
  storage_account_name = azurerm_storage_account.dev-experiment-experiment-storage.name
  storage_container_name = azurerm_storage_container.dev-experiment-container.name
  type = "Block"
  source = "function1.zip"
}

# create function app 'environment'
# different from how AWS lambda works
resource "azurerm_function_app" "dev-experiment-monolith" {
  depends_on = [azurerm_storage_blob.dev-experiment-monolith-code]

  name = "dev-experiment-function1"
  location = var.azure_region
  resource_group_name = azurerm_resource_group.dev-experiment-rg.name
  app_service_plan_id = azurerm_app_service_plan.dev-experiment-plan.id
  storage_connection_string = azurerm_storage_account.dev-experiment-experiment-storage.primary_connection_string
  version = "~2"

  app_settings = {
    HASH = data.archive_file.dev-experiment-monolith-function-code.output_base64sha256
    WEBSITE_RUN_FROM_PACKAGE = "${azurerm_storage_blob.dev-experiment-monolith-code.url}${data.azurerm_storage_account_sas.sas-dev-experiment.sas}"
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.dev-experiment.instrumentation_key
    FUNCTIONS_WORKER_RUNTIME = "python"
  }
}

# Get the functions key out of the app
resource "azurerm_template_deployment" "dev-experiment-monolith-function-key" {
  depends_on = [azurerm_function_app.dev-experiment-monolith]

  name = "dev-experiment-monolith_get_function_key"
  parameters = {
    "functionApp" = azurerm_function_app.dev-experiment-monolith.name
  }
  resource_group_name    = azurerm_resource_group.dev-experiment-rg.name
  deployment_mode = "Incremental"

  template_body = <<BODY
  {
      "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
      "contentVersion": "1.0.0.0",
      "parameters": {
          "functionApp": {"type": "string", "defaultValue": ""}
      },
      "variables": {
          "functionAppId": "[resourceId('Microsoft.Web/sites', parameters('functionApp'))]"
      },
      "resources": [
      ],
      "outputs": {
          "functionkey": {
              "type": "string",
              "value": "[listkeys(concat(variables('functionAppId'), '/host/default'), '2018-11-01').functionKeys.default]"                                                                                }
      }
  }
  BODY
}

# output some useful variables
output "dev-experiment-monolith_function_key" {
  value = "${lookup(azurerm_template_deployment.dev-experiment-monolith-function-key.outputs, "functionkey")}"
}
output "dev-experiment-monolith_function_app_url" {
  value = azurerm_function_app.dev-experiment-monolith.default_hostname
}
