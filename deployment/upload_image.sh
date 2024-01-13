aws_profile="$1"
aws_region="$2"
env="$3"
app="$4"
aws_account="$5"

ecr_repo="$app-$env"
base_uri="$aws_account.dkr.ecr.$aws_region.amazonaws.com"
image_uri="$base_uri/$ecr_repo:$env"

## Use to deploy new model when there are changes in code folder
# Upload docker image to ECR
echo "Docker Image Built"
docker build --platform linux/amd64 -t $ecr_repo:$env ../

export fuzzw=$(aws ecr get-login-password --region $aws_region --profile $aws_profile)

eval $fuzzw
echo "Successful ECR Login"

docker login --username AWS --password $fuzzw $base_uri

docker tag $ecr_repo:$env $image_uri
echo "Successful ECR Image tagging"

docker push $image_uri
echo "Successful ECR Push"