# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.scenario-pyramid-worker.public_ip_address
}
