variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_datacenter_region" {}
variable "client_pub_key" {}
variable "client_pvt_key" {}
variable "client_ssh_fingerprint" {}

# you must supply the experiment context as a command line argument
variable "remote_env_file" {}
variable "env_file" {}

# ip address of the db server
variable "db_server_static_ip" {}

variable "subnet_id" {}
variable "security_group_id" {}

# for variable experiment based client size
variable "aws_ec2_size" {}
