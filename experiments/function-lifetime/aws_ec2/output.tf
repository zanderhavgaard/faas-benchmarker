output "ip_address" {
  value = aws_eip.function-lifetime1-worker-eip.public_ip
}
