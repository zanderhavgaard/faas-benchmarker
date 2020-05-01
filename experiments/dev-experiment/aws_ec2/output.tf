output "ip_address" {
  value = aws_eip.dev-experiment1-worker-eip.public_ip
}
