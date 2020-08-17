# output the invocation url
output "invoke_url" {
  value = aws_api_gateway_deployment.linear-invocation-prod.invoke_url
}

# output the api key
output "api_key" {
  value = aws_api_gateway_api_key.linear-invocation-key.value
}
