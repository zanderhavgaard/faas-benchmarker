output "ip_address" {
  value = aws_eip.single-function-time-to-cold-start1-worker-eip.public_ip
}
