# IAM role which dictates what other AWS services the Lambda function
# may access.
resource "aws_iam_role" "lambda_exec" {
  name = "${var.app}-${var.env}-iam_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

data "aws_ecr_repository" "function_ecr_repo" {
  name = "${var.app}-${var.env}"
}

resource "aws_lambda_function" "lambda_function" {
  function_name = "${var.app}-${var.env}"
  timeout       = var.timeout
  memory_size   = var.memory_size
  image_uri     = "${data.aws_ecr_repository.function_ecr_repo.repository_url}:${var.env}"
  package_type  = "Image"

  role = aws_iam_role.lambda_exec.arn

  environment {
    variables = {
      ENV = var.env
      APP = var.app
    }
  }
}