# this terraform file creates an azure function using the zip file deployment
# hostname and function key outputted and can be used to invoke functions
# make sure to point the file resource to the directory containing the function code

# import variables
variable "subscription_id" {}
variable "client_id" {}
variable "client_secret" {}
variable "tenant_id" {}
variable "azure_region" {}

# setup provider
provider "azurerm" {
  subscription_id = var.subscription_id
  client_id = var.client_id
  client_secret = var.client_secret
  tenant_id = var.tenant_id
  version = "2.0"
  features {}
}

# create resource group
resource "azurerm_resource_group" "hw-rg" {
  name = "hw-rg"
  location = var.azure_region
}

# create service plan for rg
resource "azurerm_app_service_plan" "hw-plan" {
  name = "hw-plan"
  location = var.azure_region
  resource_group_name = azurerm_resource_group.hw-rg.name
  kind = "Linux"
  reserved = true
  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

# create storage account for holding function code
resource "azurerm_storage_account" "helloworld" {
  name = "thesishelloworld"
  resource_group_name = azurerm_resource_group.hw-rg.name
  location = var.azure_region
  account_tier = "Standard"
  account_replication_type = "LRS"
}

# create storage container for holding fuctiom code
resource "azurerm_storage_container" "hw-container" {
  name = "hw-container"
  storage_account_name = azurerm_storage_account.helloworld.name
  container_access_type = "private"
}

# create permission for function app to access storage container
data "azurerm_storage_account_sas" "sas-hw" {
  connection_string = azurerm_storage_account.helloworld.primary_connection_string
  https_only        = false
  resource_types {
    service   = false
    container = false
    object    = true
  }
  services {
    blob  = true
    queue = false
    table = false
    file  = false
  }
  start  = "2020-03-10"
  expiry = "2020-07-01"
  permissions {
    read    = true
    write   = false
    delete  = false
    list    = false
    add     = false
    create  = false
    update  = false
    process = false
  }
}

# create zip archive locally
data "archive_file" "hw-function-code" {
  type = "zip"
  source_dir = "function_code"
  output_path = "function.zip"
}

# upload zip archive to storage contianer
resource "azurerm_storage_blob" "hw-code" {
  name = "function.zip"
  storage_account_name = azurerm_storage_account.helloworld.name
  storage_container_name = azurerm_storage_container.hw-container.name
  type = "Block"
  source = "function.zip"
}

# create function app 'environment'
# different from how AWS lambda works
resource "azurerm_function_app" "hw1" {
  name = "hw-python"
  location = var.azure_region
  resource_group_name = azurerm_resource_group.hw-rg.name
  app_service_plan_id = azurerm_app_service_plan.hw-plan.id
  storage_connection_string = azurerm_storage_account.helloworld.primary_connection_string
  version = "~2"

  app_settings = {
    HASH = filesha256("function.zip")
    WEBSITE_RUN_FROM_PACKAGE = "${azurerm_storage_blob.hw-code.url}${data.azurerm_storage_account_sas.sas-hw.sas}"
  }
}

# Get the functions key out of the app
resource "azurerm_template_deployment" "function_key" {
  depends_on = [azurerm_function_app.hw1]

  name = "get_fucntion_keys"
  parameters = {
    "functionApp" = azurerm_function_app.hw1.name
  }
  resource_group_name    = azurerm_resource_group.hw-rg.name
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
output "func_key" {
  value = "${lookup(azurerm_template_deployment.function_key.outputs, "functionkey")}"
}
output "function_app_url" {
  value = azurerm_function_app.hw1.default_hostname
}
