output "ip_address" {
  value = aws_eip.track-cloudfunctions-lifecycle1-worker-eip.public_ip
}
