# attach elastic public ip to instance
resource "aws_eip" "track-cloudfunctions-lifecycle1-worker-eip" {
  instance = aws_instance.track-cloudfunctions-lifecycle1-worker-aws.id
  vpc      = true
}
