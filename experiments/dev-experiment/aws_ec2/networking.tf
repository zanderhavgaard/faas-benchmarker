# attach elastic public ip to instance
resource "aws_eip" "dev-experiment1-worker-eip" {
  instance = aws_instance.dev-experiment1-worker-aws.id
  vpc      = true
}
