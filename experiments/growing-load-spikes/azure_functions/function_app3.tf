# create function app 'environment'
# different from how AWS lambda works
resource "azurerm_function_app" "growing-load-spikes3" {

  name = "growing-load-spikes-function3"
  location = var.azure_region
  resource_group_name = azurerm_resource_group.growing-load-spikes-rg.name
  app_service_plan_id = azurerm_app_service_plan.growing-load-spikes-plan.id
  storage_connection_string = azurerm_storage_account.growing-load-spikes-experiment-storage.primary_connection_string
  version = "~2"

  app_settings = {
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.growing-load-spikes.instrumentation_key
    FUNCTIONS_WORKER_RUNTIME = "python"
  }
}

# Get the functions key out of the app
resource "azurerm_template_deployment" "growing-load-spikes3-function-key" {
  depends_on = [azurerm_function_app.growing-load-spikes3]

  name = "growing-load-spikes3_get_function_key"
  parameters = {
    "functionApp" = azurerm_function_app.growing-load-spikes3.name
  }
  resource_group_name    = azurerm_resource_group.growing-load-spikes-rg.name
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
output "growing-load-spikes-function3_function_key" {
  value = "${lookup(azurerm_template_deployment.growing-load-spikes3-function-key.outputs, "functionkey")}"
}
output "growing-load-spikes-function3_function_app_url" {
  value = azurerm_function_app.growing-load-spikes3.default_hostname
}
