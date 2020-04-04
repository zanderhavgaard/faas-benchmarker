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

provider "archive" {
  version = "1.3"
}

provider "random" {
  version = "2.2"
}

# create resource group
resource "azurerm_resource_group" "changeme-rg" {
  name = "changeme-rg"
  location = var.azure_region
}

# create service plan for rg
resource "azurerm_app_service_plan" "changeme-plan" {
  name = "changeme-plan"
  location = var.azure_region
  resource_group_name = azurerm_resource_group.changeme-rg.name
  kind = "Linux"
  reserved = true
  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

# generate random name for storage account
resource "random_string" "random-name" {
  length = 24
  special = false
  upper = false
  lower = true
  number = true
}

# create storage account for holding function code
resource "azurerm_storage_account" "changeme-experiment-storage" {
  name = random_string.random-name.result
  resource_group_name = azurerm_resource_group.changeme-rg.name
  location = var.azure_region
  account_tier = "Standard"
  account_replication_type = "LRS"
}

# create storage container for holding fuctiom code
resource "azurerm_storage_container" "changeme-container" {
  name = "changeme-container"
  storage_account_name = azurerm_storage_account.changeme-experiment-storage.name
  container_access_type = "private"
}

# create permission for function app to access storage container
data "azurerm_storage_account_sas" "sas-changeme" {
  connection_string = azurerm_storage_account.changeme-experiment-storage.primary_connection_string
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
