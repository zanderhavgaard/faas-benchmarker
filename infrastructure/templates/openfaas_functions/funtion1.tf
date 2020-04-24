resource "openfaas_function" "function1" {
  name = "function1"
  image = "${var.dockerhub_username}/function1"
}

resource "openfaas_function" "function2" {
  name = "function2"
  image = "${var.dockerhub_username}/function2"
}

resource "openfaas_function" "function3" {
  name = "function3"
  image = "${var.dockerhub_username}/function3"
}
