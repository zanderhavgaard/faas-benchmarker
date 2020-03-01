# this terraform file creates an EC2 instance on aws
# from example @ https://medium.com/@hmalgewatta/setting-up-an-aws-ec2-instance-with-ssh-access-using-terraform-c336c812322f

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "exp_pub_key" {}
variable "exp_pvt_key" {}
variable "exp_ssh_fingerprint" {}

provider "aws" {
  region = "eu-central-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  version = "2.51"
}

# ec2 instance
resource "aws_instance" "experiment-worker-aws" {
  tags = {
    Name = "experiment-worker"
  }
  ami = "ami-00f69856ea899baec"
  instance_type = "t2.micro"
  key_name = "experiment_worker"
  subnet_id = aws_subnet.subnet-uno.id
  security_groups = [aws_security_group.ingress-all-test.id]
}

# register ssh keys
resource "aws_key_pair" "experiment_worker_key" {
  key_name = "experiment_worker"
  public_key = file(var.exp_pub_key)
}

# create VPC
resource "aws_vpc" "test-env" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
  tags = {
    Name = "test-env"
  }
}

# attach elastic public ip to VPC
resource "aws_eip" "ip-test-env" {
  instance = aws_instance.experiment-worker-aws.id
  vpc      = true
}

# create internet gateway
resource "aws_internet_gateway" "test-env-gw" {
  vpc_id = aws_vpc.test-env.id
  tags = {
    Name = "test-env-gw"
  }
}

# create network subnet
resource "aws_subnet" "subnet-uno" {
  cidr_block = cidrsubnet(aws_vpc.test-env.cidr_block, 3, 1)
  vpc_id = aws_vpc.test-env.id
  availability_zone = "eu-central-1c"
}

# create routing table in subnet
resource "aws_route_table" "route-table-test-env" {
  vpc_id = aws_vpc.test-env.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.test-env-gw.id
  }
  tags = {
    Name = "test-env-route-table"
  }
}
resource "aws_route_table_association" "subnet-association" {
  subnet_id      = aws_subnet.subnet-uno.id
  route_table_id = aws_route_table.route-table-test-env.id
}

# setup security group to allow traffic from outside VPC
resource "aws_security_group" "ingress-all-test" {
  name = "allow-all-sg"
  vpc_id = aws_vpc.test-env.id
  ingress {
    cidr_blocks = [
      "0.0.0.0/0"
    ]
    from_port = 22
    to_port = 22
    protocol = "tcp"
  }
  // Terraform removes the default rule
  egress {
   from_port = 0
   to_port = 0
   protocol = "-1"
   cidr_blocks = ["0.0.0.0/0"]
 }
}
