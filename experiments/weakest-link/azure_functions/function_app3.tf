# create zip archive locally
data "archive_file" "weakest-link3-function-code" {
  type = "zip"
  source_dir = "function_code/weakest-link3"
  output_path = "function3.zip"
}

# upload zip archive to storage contianer
resource "azurerm_storage_blob" "weakest-link3-code" {
  name = "weakest-link3-function.zip"
  storage_account_name = azurerm_storage_account.weakest-link-experiment-storage.name
  storage_container_name = azurerm_storage_container.weakest-link-container.name
  type = "Block"
  source = "function3.zip"
}

# create function app 'environment'
# different from how AWS lambda works
resource "azurerm_function_app" "weakest-link3" {
  depends_on = [azurerm_storage_blob.weakest-link3-code]

  name = "weakest-link3-python"
  location = var.azure_region
  resource_group_name = azurerm_resource_group.weakest-link-rg.name
  app_service_plan_id = azurerm_app_service_plan.weakest-link-plan.id
  storage_connection_string = azurerm_storage_account.weakest-link-experiment-storage.primary_connection_string
  version = "~2"

  app_settings = {
    HASH = data.archive_file.weakest-link3-function-code.output_base64sha256
    WEBSITE_RUN_FROM_PACKAGE = "${azurerm_storage_blob.weakest-link3-code.url}${data.azurerm_storage_account_sas.sas-weakest-link.sas}"
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.weakest-link.instrumentation_key
    FUNCTIONS_WORKER_RUNTIME = "python"
  }
}

# Get the functions key out of the app
resource "azurerm_template_deployment" "chageme3-function-key" {
  depends_on = [azurerm_function_app.weakest-link3]

  name = "weakest-link3_get_function_key"
  parameters = {
    "functionApp" = azurerm_function_app.weakest-link3.name
  }
  resource_group_name    = azurerm_resource_group.weakest-link-rg.name
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
output "weakest-link3_function_key" {
  value = "${lookup(azurerm_template_deployment.chageme3-function-key.outputs, "functionkey")}"
}
output "weakest-link3_function_app_url" {
  value = azurerm_function_app.weakest-link3.default_hostname
}
