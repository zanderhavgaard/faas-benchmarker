# attach elastic public ip to instance
resource "aws_eip" "throughput-benchmarking1-worker-eip" {
  instance = aws_instance.throughput-benchmarking1-worker-aws.id
  vpc      = true
}
