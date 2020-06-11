# attach elastic public ip to instance
resource "aws_eip" "growing-load-spikes1-worker-eip" {
  instance = aws_instance.growing-load-spikes1-worker-aws.id
  vpc      = true
}
