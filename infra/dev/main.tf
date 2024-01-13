module "lambda" {
  source             = "../aws_lambda"
  aws_profile        = var.aws_profile
  env                = var.env
  app                = var.app
  timeout            = var.timeout
  memory_size        = var.memory_size
}
