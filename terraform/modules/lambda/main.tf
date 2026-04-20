# Lambda CloudWatcg log group
resource "aws_cloudwatch_log_group" "main" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = 30
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda-auth-app-role"

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

resource "aws_lambda_function" "main" {
  # disabled for academical reasons
  function_name = var.lambda_name
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.image_registry.repository_url}@${data.aws_ecr_image.app.image_digest}"
  architectures = ["x86_64"]
  timeout       = 10

  environment {
    variables = var.env_variables
  }
}

