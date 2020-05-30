# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.track-cloudfunctions-lifecycle-worker.public_ip_address
}
