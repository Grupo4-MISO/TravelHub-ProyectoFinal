# Log group
resource "aws_cloudwatch_log_group" "main" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = 30
}

# Rol único por lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.lambda_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# Permisos básicos (logs)
resource "aws_iam_role_policy_attachment" "basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda
resource "aws_lambda_function" "main" {
  function_name = var.lambda_name
  role          = aws_iam_role.lambda_role.arn

  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.image_registry.repository_url}@${data.aws_ecr_image.app.image_digest}"
  architectures = ["x86_64"]
  timeout       = 10

  environment {
    variables = var.env_variables
  }

  depends_on = [
    aws_cloudwatch_log_group.main
  ]
}

resource "aws_iam_role_policy" "sqs_access" {
  name = "${var.lambda_name}-sqs-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ]
      Resource = "*"
    }]
  })
}