# output the invocation url
output "invoke_url" {
  value = aws_api_gateway_deployment.time-to-cold-start-twelve-threads-prod.invoke_url
}

# output the api key
output "api_key" {
  value = aws_api_gateway_api_key.time-to-cold-start-twelve-threads-key.value
}
