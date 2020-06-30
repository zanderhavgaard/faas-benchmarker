variable "do_token" {}
variable "db_pub_key" {}
variable "db_pvt_key" {}
variable "db_ssh_fingerprint" {}
variable "client_ssh_fingerprint" {}
variable "orch_ssh_fingerprint" {}

# username for new vm user
variable "username" {
  type = string
  default = "ubuntu"
}

# credentials for digital ocean space for storing backups
variable "space_name" {}
variable "space_key" {}
variable "space_secret_key" {}

# credentials for database
variable "DB_SQL_USER" {}
variable "DB_SQL_PASS" {}
variable "DB_SQL_ROOT_PASS" {}
