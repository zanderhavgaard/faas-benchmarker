# see https://docs.microsoft.com/en-us/azure/terraform/terraform-install-configure
# and https://www.terraform.io/docs/providers/azurerm/guides/service_principal_client_secret.html
# on how to get up and running

# template for creating azure experiment worker vm
# based on: https://www.terraform.io/docs/providers/azurerm/r/linux_virtual_machine.html
# and: https://docs.microsoft.com/en-us/azure/terraform/terraform-create-complete-vm

# create resource group
resource "azurerm_resource_group" "changeme-openfaas-worker-rg" {
  name     = "changeme-openfaas-worker"
  location = "West Europe"
}

# create VPC
resource "azurerm_virtual_network" "changeme-openfaas-worker-network" {
  name                = "changeme-openfaas-worker-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.changeme-openfaas-worker-rg.location
  resource_group_name = azurerm_resource_group.changeme-openfaas-worker-rg.name
}

# create subnet
resource "azurerm_subnet" "changeme-openfaas-worker-subnet" {
  name                 = "changeme-openfaas-worker-subnet"
  resource_group_name  = azurerm_resource_group.changeme-openfaas-worker-rg.name
  virtual_network_name = azurerm_virtual_network.changeme-openfaas-worker-network.name
  address_prefix       = "10.0.2.0/24"
}

# create network interface
resource "azurerm_network_interface" "changeme-openfaas-worker-ni" {
  name                = "changeme-openfaas-worker-nic"
  location            = azurerm_resource_group.changeme-openfaas-worker-rg.location
  resource_group_name = azurerm_resource_group.changeme-openfaas-worker-rg.name

  ip_configuration {
    name                          = "changeme-openfaas-worker-ip-config"
    subnet_id                     = azurerm_subnet.changeme-openfaas-worker-subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id = azurerm_public_ip.changeme-openfaas-worker-public-ip.id
  }
}

# create public ip address
resource "azurerm_public_ip" "changeme-openfaas-worker-public-ip" {
  name = "changeme-openfaas-worker-public-ip"
  location = azurerm_resource_group.changeme-openfaas-worker-rg.location
  resource_group_name = azurerm_resource_group.changeme-openfaas-worker-rg.name
  allocation_method = "Dynamic"
}
