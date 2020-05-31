# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.growing-load-spikes-worker.public_ip_address
}
