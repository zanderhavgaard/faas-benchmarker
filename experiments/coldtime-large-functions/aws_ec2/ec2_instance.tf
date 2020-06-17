# ec2 instance
resource "aws_instance" "coldtime-large-functions1-worker-aws" {
  tags = {
    Name = "coldtime-large-functions1-worker"
  }
  # ami = "ami-0701e7be9b2a77600"
  ami = "ami-0dad359ff462124ca"
  instance_type = var.aws_ec2_size
  key_name = "faasbenchmarker"
  subnet_id = var.subnet_id
  security_groups = [var.security_group_id]
}

# HACK to run provisioners over SSH after instance
# has been created and recieved a public ip address
resource "null_resource" "ec2-provisioners" {
  # run the provisioners after the instance has been created
  # and the ip address has been assigned
  depends_on = [
    aws_eip.coldtime-large-functions1-worker-eip,
    aws_instance.coldtime-large-functions1-worker-aws
  ]
  # setup ssh connection for provisioners
  connection {
    user = "ubuntu"
    # host = aws_instance.experiment-worker-aws.public_ip
    host = aws_eip.coldtime-large-functions1-worker-eip.public_ip
    type = "ssh"
    private_key = file(var.client_pvt_key)
    timeout = "2m"
  }

  provisioner "file" {
    source = "../../../secrets/ssh_keys/experiment_servers"
    destination = "/home/ubuntu/.ssh/id_rsa"
  }
  provisioner "file" {
    source = var.env_file
    destination = var.remote_env_file
  }

  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",

      "chmod 600 /home/ubuntu/.ssh/id_rsa",
      "{ echo -n 'export fbrd=/home/ubuntu/faas-benchmarker\n' ; echo -n 'export PYTHONPATH=$PYTHONPATH:/home/ubuntu/faas-benchmarker/benchmark\n' ; echo -n 'export DB_HOSTNAME=${var.db_server_static_ip}\n' ; cat .bashrc ; } > /home/ubuntu/.bashrc.new",
      "mv .bashrc.new .bashrc",

      "sudo apt-get update -q",
      "sudo apt-get install -qq docker-compose",
      "sudo systemctl enable --now docker",
      "sudo usermod -aG docker ubuntu",
      "sudo docker pull -q faasbenchmarker/client:latest"
    ]
  }
}
