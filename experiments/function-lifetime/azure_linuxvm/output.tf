# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.function-lifetime-worker.public_ip_address
}
