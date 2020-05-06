# output the invocation url
output "invoke_url" {
  value = aws_api_gateway_deployment.single-function-time-to-cold-start-prod.invoke_url
}

# output the api key
output "api_key" {
  value = aws_api_gateway_api_key.single-function-time-to-cold-start-key.value
}
