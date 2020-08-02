output "ip_address" {
  value = aws_eip.simple-cold-function-threaded-twelve1-worker-eip.public_ip
}
