output "sqs_queue_arn" {
  description = "The ARN of the created SQS queue."
  value       = aws_sqs_queue.main.arn
}

output "sqs_queue_url" {
  description = "The URL of the created SQS queue."
  value       = aws_sqs_queue.main.url
}

output "sqs_queue_name" {
  description = "The name of the created SQS queue."
  value       = aws_sqs_queue.main.name
}