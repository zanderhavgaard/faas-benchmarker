# attach elastic public ip to instance
resource "aws_eip" "concurrency-benchmarking1-worker-eip" {
  instance = aws_instance.concurrency-benchmarking1-worker-aws.id
  vpc      = true
}
