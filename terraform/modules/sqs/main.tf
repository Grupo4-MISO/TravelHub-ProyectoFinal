resource "aws_sqs_queue" "main" {
  name                       = var.queue_name
  delay_seconds              = 0
  max_message_size           = 262144 # 256 KB
  message_retention_seconds  = 3600 # 1 hour
  receive_wait_time_seconds  = 5
  visibility_timeout_seconds = 15
}

data "aws_iam_policy_document" "allow" {
  statement {
    sid    = "First"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["sqs:*"]
    resources = [aws_sqs_queue.main.arn]
  }
}

resource "aws_sqs_queue_policy" "test" {
  queue_url = aws_sqs_queue.main.id
  policy    = data.aws_iam_policy_document.allow.json
}
