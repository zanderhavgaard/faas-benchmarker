# this terraform file creates an EC2 instance on aws
# based on example @ https://medium.com/@hmalgewatta/setting-up-an-aws-ec2-instance-with-ssh-access-using-terraform-c336c812322f

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "exp_pub_key" {}
variable "exp_pvt_key" {}
variable "exp_ssh_fingerprint" {}

# setup aws provider
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
  subnet_id = aws_subnet.experiment-worker-subnet.id
  security_groups = [aws_security_group.allow-ssh.id]
}

# HACK to run provisioners over SSH after instance
# has been created and recieved a public ip address
resource "null_resource" "ec2-provisioners" {
  # run the provisioners after the instance has been created
  # and the ip address has been assigned
  depends_on = [
    aws_eip.experiment-worker-eip,
    aws_instance.experiment-worker-aws
  ]
  # setup ssh connection for provisioners
  connection {
    user = "ubuntu"
    # host = aws_instance.experiment-worker-aws.public_ip
    host = aws_eip.experiment-worker-eip.public_ip
    type = "ssh"
    private_key = file(var.exp_pvt_key)
    timeout = "2m"
  }

  # copy local files to remote server
  # useage: https://www.terraform.io/docs/provisioners/file.html
  # provisioner "file" {
    # source = "../../benchmark"
    # destination = "/home/ubuntu"
  # }

  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      # "sudo apt update",
      # "sudo apt install -y git python3 python3-pip",
      # "git clone https://github.com/zanderhavgaard/thesis-code",
      # "cd thesis-code",
      "echo hello from Frankfurt...",
      "ls -al",
    ]
  }
}

# register ssh keys with aws
resource "aws_key_pair" "experiment_worker_key" {
  key_name = "experiment_worker"
  public_key = file(var.exp_pub_key)
}

# create VPC
resource "aws_vpc" "experiment-worker-vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
  tags = {
    Name = "experiment-worker-vpc"
  }
}

# attach elastic public ip to instance
resource "aws_eip" "experiment-worker-eip" {
  instance = aws_instance.experiment-worker-aws.id
  vpc      = true
}

# create internet gateway to VPC
resource "aws_internet_gateway" "experiment-worker-vpc-gateway" {
  vpc_id = aws_vpc.experiment-worker-vpc.id
  tags = {
    Name = "experiment-worker-vpc-gateway"
  }
}

# create VPC subnet
resource "aws_subnet" "experiment-worker-subnet" {
  cidr_block = cidrsubnet(aws_vpc.experiment-worker-vpc.cidr_block, 3, 1)
  vpc_id = aws_vpc.experiment-worker-vpc.id
  availability_zone = "eu-central-1c"
}

# create routing table in subnet
resource "aws_route_table" "experiment-worker-vpc-route-table" {
  vpc_id = aws_vpc.experiment-worker-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.experiment-worker-vpc-gateway.id
  }
  tags = {
    Name = "experiment-worker-vpc-route-table"
  }
}
# attach route table to subnet
resource "aws_route_table_association" "subnet-association" {
  subnet_id      = aws_subnet.experiment-worker-subnet.id
  route_table_id = aws_route_table.experiment-worker-vpc-route-table.id
}

# setup security group to allow traffic from outside VPC
resource "aws_security_group" "allow-ssh" {
  name = "allow-ssh"
  vpc_id = aws_vpc.experiment-worker-vpc.id
  ingress {
    cidr_blocks = [
      "0.0.0.0/0"
    ]
    from_port = 22
    to_port = 22
    protocol = "tcp"
  }
  # Terraform removes the default rule
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# print ip address
output "ip_address" {
  value = aws_eip.experiment-worker-eip.public_ip
}
