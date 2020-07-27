output "ip_address" {
  value = aws_eip.simple-cold-function1-worker-eip.public_ip
}
