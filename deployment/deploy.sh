# Step 1: Get the environment
if [ -z "$1" ]; then
  env="dev"
else
  env=$(awk '{print tolower($0)}' <<< "$1")
fi

# Step 2: Specify your aws credentials and app name
aws_profile="AdministratorAccess-007985056474"
app="lambda-docker"
aws_account="007985056474"
aws_region="ap-southeast-1"
version="0.0.2"

# Step 3: Run uploading image script
source ./upload_image.sh $aws_profile $aws_region $env $app $aws_account $version

# Step 4: Configure variable for terraform script
export TF_VAR_aws_profile=$aws_profile
export TF_VAR_aws_region=$aws_region
export TF_VAR_env=$env
export TF_VAR_app=$app
export TF_VAR_app_version=$version


# Step 5: Run terraform script
cd ../infra/$env
terraform init
# Generate and show an execution plan
terraform plan -var-file=tfvariables.tfvars
# Apply the changes
terraform apply -auto-approve -var-file=tfvariables.tfvars