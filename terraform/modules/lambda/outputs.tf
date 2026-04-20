output "lambda_function_arn" {
  value = aws_lambda_function.main.arn
}

output "lambda_name" {
  description = "Final lambda function name."
  value       = aws_lambda_function.main.function_name
}

output "lambda_invoke_arn" {
  description = "ARN to invoke Lambda Function from other services. e.g API Gateway"
  value       = aws_lambda_function.main.invoke_arn
}