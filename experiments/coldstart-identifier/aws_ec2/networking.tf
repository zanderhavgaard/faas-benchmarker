# attach elastic public ip to instance
resource "aws_eip" "coldstart-identifier1-worker-eip" {
  instance = aws_instance.coldstart-identifier1-worker-aws.id
  vpc      = true
}
