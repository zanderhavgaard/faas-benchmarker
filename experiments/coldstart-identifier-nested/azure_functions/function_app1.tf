# create function app 'environment'
# different from how AWS lambda works
resource "azurerm_function_app" "coldstart-identifier-nested1" {

  name = "coldstart-identifier-nested-function1"
  location = var.azure_region
  resource_group_name = azurerm_resource_group.coldstart-identifier-nested-rg.name
  app_service_plan_id = azurerm_app_service_plan.coldstart-identifier-nested-plan.id
  storage_connection_string = azurerm_storage_account.coldstart-identifier-nested-experiment-storage.primary_connection_string
  version = "~2"

  app_settings = {
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.coldstart-identifier-nested.instrumentation_key
    FUNCTIONS_WORKER_RUNTIME = "python"
  }
}

# Get the functions key out of the app
resource "azurerm_template_deployment" "coldstart-identifier-nested1-function-key" {
  depends_on = [azurerm_function_app.coldstart-identifier-nested1]

  name = "coldstart-identifier-nested1_get_function_key"
  parameters = {
    "functionApp" = azurerm_function_app.coldstart-identifier-nested1.name
  }
  resource_group_name    = azurerm_resource_group.coldstart-identifier-nested-rg.name
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
output "coldstart-identifier-nested-function1_function_key" {
  value = "${lookup(azurerm_template_deployment.coldstart-identifier-nested1-function-key.outputs, "functionkey")}"
}
output "coldstart-identifier-nested-function1_function_app_url" {
  value = azurerm_function_app.coldstart-identifier-nested1.default_hostname
}
