# create function app 'environment'
# different from how AWS lambda works
resource "azurerm_function_app" "linear-invocation2" {

  name = "linear-invocation-function2"
  location = var.azure_region
  resource_group_name = azurerm_resource_group.linear-invocation-rg.name
  app_service_plan_id = azurerm_app_service_plan.linear-invocation-plan.id
  storage_connection_string = azurerm_storage_account.linear-invocation-experiment-storage.primary_connection_string
  version = "~2"

  app_settings = {
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.linear-invocation.instrumentation_key
    FUNCTIONS_WORKER_RUNTIME = "python"
  }
}

# Get the functions key out of the app
resource "azurerm_template_deployment" "linear-invocation2-function-key" {
  depends_on = [azurerm_function_app.linear-invocation2]

  name = "linear-invocation2_get_function_key"
  parameters = {
    "functionApp" = azurerm_function_app.linear-invocation2.name
  }
  resource_group_name    = azurerm_resource_group.linear-invocation-rg.name
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
output "linear-invocation-function2_function_key" {
  value = "${lookup(azurerm_template_deployment.linear-invocation2-function-key.outputs, "functionkey")}"
}
output "linear-invocation-function2_function_app_url" {
  value = azurerm_function_app.linear-invocation2.default_hostname
}
