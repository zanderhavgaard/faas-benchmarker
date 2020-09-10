# attach elastic public ip to instance
resource "aws_eip" "basic-weakest-link1-worker-eip" {
  instance = aws_instance.basic-weakest-link1-worker-aws.id
  vpc      = true
}
