# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.linear-invocation-worker.public_ip_address
}
