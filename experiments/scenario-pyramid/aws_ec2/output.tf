output "ip_address" {
  value = aws_eip.scenario-pyramid1-worker-eip.public_ip
}
