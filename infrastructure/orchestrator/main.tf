provider "digitalocean" {
  token = var.do_token
  version = "~> 1.14"
}

provider "null" {
  version = "~> 2.1"
}

provider "random" {
  version = "~> 2.2"
}
