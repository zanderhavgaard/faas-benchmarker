# attach elastic public ip to instance
resource "aws_eip" "scenario-pyramid1-worker-eip" {
  instance = aws_instance.scenario-pyramid1-worker-aws.id
  vpc      = true
}
