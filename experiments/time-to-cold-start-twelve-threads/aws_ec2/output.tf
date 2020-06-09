output "ip_address" {
  value = aws_eip.time-to-cold-start-twelve-threads1-worker-eip.public_ip
}
