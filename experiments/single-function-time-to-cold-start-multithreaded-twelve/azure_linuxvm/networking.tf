# see https://docs.microsoft.com/en-us/azure/terraform/terraform-install-configure
# and https://www.terraform.io/docs/providers/azurerm/guides/service_principal_client_secret.html
# on how to get up and running

# template for creating azure experiment worker vm
# based on: https://www.terraform.io/docs/providers/azurerm/r/linux_virtual_machine.html
# and: https://docs.microsoft.com/en-us/azure/terraform/terraform-create-complete-vm

# create resource group
resource "azurerm_resource_group" "single-function-time-to-cold-start-multithreaded-twelve-worker-rg" {
  name     = "single-function-time-to-cold-start-multithreaded-twelve-worker"
  location = "West Europe"
}

# create VPC
resource "azurerm_virtual_network" "single-function-time-to-cold-start-multithreaded-twelve-worker-network" {
  name                = "single-function-time-to-cold-start-multithreaded-twelve-worker-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.single-function-time-to-cold-start-multithreaded-twelve-worker-rg.location
  resource_group_name = azurerm_resource_group.single-function-time-to-cold-start-multithreaded-twelve-worker-rg.name
}

# create subnet
resource "azurerm_subnet" "single-function-time-to-cold-start-multithreaded-twelve-worker-subnet" {
  name                 = "single-function-time-to-cold-start-multithreaded-twelve-worker-subnet"
  resource_group_name  = azurerm_resource_group.single-function-time-to-cold-start-multithreaded-twelve-worker-rg.name
  virtual_network_name = azurerm_virtual_network.single-function-time-to-cold-start-multithreaded-twelve-worker-network.name
  address_prefix       = "10.0.2.0/24"
}

# create network interface
resource "azurerm_network_interface" "single-function-time-to-cold-start-multithreaded-twelve-worker-ni" {
  name                = "single-function-time-to-cold-start-multithreaded-twelve-worker-nic"
  location            = azurerm_resource_group.single-function-time-to-cold-start-multithreaded-twelve-worker-rg.location
  resource_group_name = azurerm_resource_group.single-function-time-to-cold-start-multithreaded-twelve-worker-rg.name

  ip_configuration {
    name                          = "single-function-time-to-cold-start-multithreaded-twelve-worker-ip-config"
    subnet_id                     = azurerm_subnet.single-function-time-to-cold-start-multithreaded-twelve-worker-subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id = azurerm_public_ip.single-function-time-to-cold-start-multithreaded-twelve-worker-public-ip.id
  }
}

# create public ip address
resource "azurerm_public_ip" "single-function-time-to-cold-start-multithreaded-twelve-worker-public-ip" {
  name = "single-function-time-to-cold-start-multithreaded-twelve-worker-public-ip"
  location = azurerm_resource_group.single-function-time-to-cold-start-multithreaded-twelve-worker-rg.location
  resource_group_name = azurerm_resource_group.single-function-time-to-cold-start-multithreaded-twelve-worker-rg.name
  allocation_method = "Dynamic"
}
