# Step 1: Configure AWS credentials and application-related values such as application name, environment (e.g., dev, sqa, uat, and prod), and AWS account number
aws_profile="$1"
aws_region="$2"
env="$3"
app="$4"
aws_account="$5"
version="$6" # New Change

# Step 2: Formulate ECR values
ecr_repo="$app-$env"
base_uri="$aws_account.dkr.ecr.$aws_region.amazonaws.com"
image_uri="$base_uri/$ecr_repo:$version" # New Change

# Step 3: Upload docker image to ECR
# Step 3.1: Docker Image Built
echo "Docker Image Built"
docker build --platform linux/amd64 -t $ecr_repo:$env ../

# Step 3.2: Login into AWS ECR
export ecr_password=$(aws ecr get-login-password --region $aws_region --profile $aws_profile)
eval $ecr_password
echo "Successful ECR Login"
docker login --username AWS --password $ecr_password $base_uri

# Step 3.3: Tag the Docker image
docker tag $ecr_repo:$env $image_uri
echo "Successfully tagged the ECR image"

# Step 3.4: Push the Docker image to ECR repository
docker push $image_uri
echo "Successfully pushed the Docker image to ECR"
