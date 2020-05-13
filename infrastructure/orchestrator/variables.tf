# digital ocean credentials
variable "do_token" {}
variable "orch_pub_key" {}
variable "orch_pvt_key" {}
variable "orch_ssh_fingerprint" {}

# azure cli credentials
variable "client_id" {}
variable "client_secret" {}
variable "tenant_id" {}

# username for new vm user
variable "username" {
  type = string
  default = "ubuntu"
}

# credentials for digital ocean space for stoting backups
variable "space_name" {}
variable "space_key" {}
variable "space_secret_key" {}
