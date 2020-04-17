# this terraform file creates an EC2 instance on aws
# based on example @ https://medium.com/@hmalgewatta/setting-up-an-aws-ec2-instance-with-ssh-access-using-terraform-c336c812322f

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_token" {}
variable "aws_datacenter_region" {}
variable "client_pub_key" {}
variable "client_pvt_key" {}
variable "client_ssh_fingerprint" {}

# you must supply the experiment context as a command line argument
variable "remote_env_file" {}
variable "env_file" {}

# setup aws provider
provider "aws" {
  region = var.aws_datacenter_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  token = var.aws_token
  version = "2.51"
}

provider "null" {
  version = "2.1"
}

# ec2 instance
resource "aws_instance" "changeme1-worker-aws" {
  tags = {
    Name = "changeme1-worker"
  }
  ami = "ami-085925f297f89fce1"
  instance_type = "t2.micro"
  key_name = "changeme1_worker"
  subnet_id = aws_subnet.changeme1-worker-subnet.id
  security_groups = [aws_security_group.allow-ssh.id]
}

# HACK to run provisioners over SSH after instance
# has been created and recieved a public ip address
resource "null_resource" "ec2-provisioners" {
  # run the provisioners after the instance has been created
  # and the ip address has been assigned
  depends_on = [
    aws_eip.changeme1-worker-eip,
    aws_instance.changeme1-worker-aws
  ]
  # setup ssh connection for provisioners
  connection {
    user = "ubuntu"
    # host = aws_instance.experiment-worker-aws.public_ip
    host = aws_eip.changeme1-worker-eip.public_ip
    type = "ssh"
    private_key = file(var.client_pvt_key)
    timeout = "2m"
  }

  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",
      "sudo apt-get update -q",
      "sudo apt-get install -y -qq git python3 python3-dev python3-pip",
      "git clone --quiet https://github.com/zanderhavgaard/faas-benchmarker /home/ubuntu/faas-benchmarker",
      "{ echo -n 'export fbrd=/home/ubuntu/faas-benchmarker\n' ; echo -n 'export PYTHONPATH=$PYTHONPATH:/home/ubuntu/faas-benchmarker/benchmark\n' ; cat .bashrc ; } > /home/ubuntu/.bashrc.new",
      "mv .bashrc.new .bashrc",
      "cd /home/ubuntu/faas-benchmarker",
      "pip3 install -q -r requirements.txt",
    ]
  }

  # copy local files to remote server
  # useage: https://www.terraform.io/docs/provisioners/file.html
  provisioner "file" {
    source = var.env_file
    destination = var.remote_env_file
  }
}

# register ssh keys with aws
resource "aws_key_pair" "changeme1_worker_key" {
  key_name = "changeme1_worker"
  public_key = file(var.client_pub_key)
}

# create VPC
resource "aws_vpc" "changeme1-worker-vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
  tags = {
    Name = "changeme1-worker-vpc"
  }
}

# attach elastic public ip to instance
resource "aws_eip" "changeme1-worker-eip" {
  instance = aws_instance.changeme1-worker-aws.id
  vpc      = true
}

# create internet gateway to VPC
resource "aws_internet_gateway" "changeme1-worker-vpc-gateway" {
  vpc_id = aws_vpc.changeme1-worker-vpc.id
  tags = {
    Name = "changeme1-worker-vpc-gateway"
  }
}

# create VPC subnet
resource "aws_subnet" "changeme1-worker-subnet" {
  cidr_block = cidrsubnet(aws_vpc.changeme1-worker-vpc.cidr_block, 3, 1)
  vpc_id = aws_vpc.changeme1-worker-vpc.id
  availability_zone = "us-east-1c"
}

# create routing table in subnet
resource "aws_route_table" "changeme1-worker-vpc-route-table" {
  vpc_id = aws_vpc.changeme1-worker-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.changeme1-worker-vpc-gateway.id
  }
  tags = {
    Name = "changeme1-worker-vpc-route-table"
  }
}
# attach route table to subnet
resource "aws_route_table_association" "subnet-association" {
  subnet_id      = aws_subnet.changeme1-worker-subnet.id
  route_table_id = aws_route_table.changeme1-worker-vpc-route-table.id
}

# setup security group to allow traffic from outside VPC
resource "aws_security_group" "allow-ssh" {
  name = "allow-ssh"
  vpc_id = aws_vpc.changeme1-worker-vpc.id
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
  value = aws_eip.changeme1-worker-eip.public_ip
}
