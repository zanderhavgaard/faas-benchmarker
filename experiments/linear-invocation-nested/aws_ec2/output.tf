output "ip_address" {
  value = aws_eip.linear-invocation-nested1-worker-eip.public_ip
}
