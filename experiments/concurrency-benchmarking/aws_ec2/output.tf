output "ip_address" {
  value = aws_eip.concurrency-benchmarking1-worker-eip.public_ip
}
