provider "aws" {
  profile = var.profile
  region = "eu-central-1"
}

data "aws_iam_policy_document" "lambda" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_mtglayer" {
  name = "lambda_mtglayer"

  assume_role_policy = data.aws_iam_policy_document.lambda.json
}

resource "aws_iam_role_policy" "cloudwatch_ec2" {
  role = aws_iam_role.lambda_mtglayer.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
EOF
}

resource "aws_lambda_function" "lambda_function" {
  filename = "lambda_function.zip"
  function_name = "lambda_function"
  role = aws_iam_role.lambda_mtglayer.arn
  handler = "launcher.scrape"
  source_code_hash = filebase64sha256("lambda_function.zip")

  runtime = "python3.7"
  timeout = 120
}

resource "aws_lambda_alias" "lambda_function" {
  name = "lambda_function"
  function_name = aws_lambda_function.lambda_function.function_name
  function_version = "$LATEST"
}
