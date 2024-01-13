## Purpose

This repo is the follow-up tutorial of [this repo](https://github.com/tquean15012003/lambda-function-with-docker). In this tutorial, we aim to automiate the entire deployment process.

## Prerequisites

- [Docker](https://docs.docker.com/engine/install/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Terraform CLI](https://developer.hashicorp.com/terraform/install)

## Deployment steps

#### 1. Update deployment information

- Edit `deployment/deploy.sh` with your own aws credentials

#### 2. Create ECR repo

- Name your ECR repo with this format `{app}-{env}` e.g. `lambda-docker-dev`

#### 3. Push Docker Image to ECR

1. Navigate the ternimal to `deployment` folder
2. Run `deploy.sh` file

```bash
bash deploy/deploy.sh dev
```

## Additionals

- For more details, please check out [this article](https://medium.com/@tqueansg15012003/python-lambda-functions-with-container-images-deployment-a-77b8c53d224b)
