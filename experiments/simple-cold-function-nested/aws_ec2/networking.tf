# attach elastic public ip to instance
resource "aws_eip" "simple-cold-function-nested1-worker-eip" {
  instance = aws_instance.simple-cold-function-nested1-worker-aws.id
  vpc      = true
}
