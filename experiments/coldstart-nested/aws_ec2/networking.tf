# attach elastic public ip to instance
resource "aws_eip" "coldstart-nested1-worker-eip" {
  instance = aws_instance.coldstart-nested1-worker-aws.id
  vpc      = true
}
