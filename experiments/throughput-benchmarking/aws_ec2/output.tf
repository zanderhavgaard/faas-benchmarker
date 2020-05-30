output "ip_address" {
  value = aws_eip.throughput-benchmarking1-worker-eip.public_ip
}
