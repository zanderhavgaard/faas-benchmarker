# create zip archive locally
data "archive_file" "changeme1-function-code" {
  type = "zip"
  source_dir = "function_code/changeme1"
  output_path = "function1.zip"
}

# upload zip archive to storage contianer
resource "azurerm_storage_blob" "changeme1-code" {
  name = "changeme1-function.zip"
  storage_account_name = azurerm_storage_account.changeme-experiment-storage.name
  storage_container_name = azurerm_storage_container.changeme-container.name
  type = "Block"
  source = "function1.zip"
}

# create function app 'environment'
# different from how AWS lambda works
resource "azurerm_function_app" "changeme1" {
  depends_on = [azurerm_storage_blob.changeme1-code]

  name = "changeme1-python"
  location = var.azure_region
  resource_group_name = azurerm_resource_group.changeme-rg.name
  app_service_plan_id = azurerm_app_service_plan.changeme-plan.id
  storage_connection_string = azurerm_storage_account.changeme-experiment-storage.primary_connection_string
  version = "~3"

  app_settings = {
    HASH = data.archive_file.changeme1-function-code.output_base64sha256
    WEBSITE_RUN_FROM_PACKAGE = "${azurerm_storage_blob.changeme1-code.url}${data.azurerm_storage_account_sas.sas-changeme.sas}"
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.changeme.instrumentation_key
  }
}

# Get the functions key out of the app
resource "azurerm_template_deployment" "chageme1-function-key" {
  depends_on = [azurerm_function_app.changeme1]

  name = "changeme1_get_function_key"
  parameters = {
    "functionApp" = azurerm_function_app.changeme1.name
  }
  resource_group_name    = azurerm_resource_group.changeme-rg.name
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
output "changeme1_function_key" {
  value = "${lookup(azurerm_template_deployment.chageme1-function-key.outputs, "functionkey")}"
}
output "changeme1_function_app_url" {
  value = azurerm_function_app.changeme1.default_hostname
}
