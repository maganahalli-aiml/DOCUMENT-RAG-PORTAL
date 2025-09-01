#!/bin/bash

# AWS ECS Deployment Script for Document Portal
# This script automates the deployment of the Document Portal to AWS ECS/Fargate

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - UPDATE THESE VALUES FOR YOUR ENVIRONMENT
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-}"  # Will be auto-detected or passed as parameter
ECR_REPOSITORY="document-portal-system"
ECS_CLUSTER="document-portal-cluster"
ECS_SERVICE="document-portal-service"
TASK_DEFINITION="document-portal-task"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "All prerequisites are met!"
}

# Function to get AWS account ID dynamically
get_aws_account_id() {
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        print_status "Getting AWS Account ID..."
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        if [ $? -ne 0 ]; then
            print_error "Failed to get AWS Account ID. Please ensure AWS CLI is configured or provide --account-id parameter."
            exit 1
        fi
        print_success "AWS Account ID: $AWS_ACCOUNT_ID"
    else
        print_success "Using provided AWS Account ID: $AWS_ACCOUNT_ID"
    fi
}

# Function to check if ECR repository exists, create if not
setup_ecr_repository() {
    print_status "Setting up ECR repository..."
    
    if aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &> /dev/null; then
        print_success "ECR repository '$ECR_REPOSITORY' already exists"
    else
        print_status "Creating ECR repository '$ECR_REPOSITORY'..."
        aws ecr create-repository \
            --repository-name $ECR_REPOSITORY \
            --region $AWS_REGION \
            --image-scanning-configuration scanOnPush=true
        print_success "ECR repository created successfully"
    fi
}

# Function to build and push Docker image
build_and_push_image() {
    print_status "Building Docker image..."
    docker build -t $ECR_REPOSITORY:$IMAGE_TAG .
    
    print_status "Logging into ECR..."
    aws ecr get-login-password --region $AWS_REGION | \
        docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    print_status "Tagging image for ECR..."
    ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG"
    docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_URI
    
    print_status "Pushing image to ECR..."
    docker push $ECR_URI
    
    print_success "Image pushed successfully to ECR: $ECR_URI"
}

# Function to update task definition with correct account ID and region
update_task_definition() {
    print_status "Updating task definition..."
    
    # Create a copy of the task definition template
    cp ecs-task-definition.json ecs-task-definition-temp.json
    
    # Update the task definition JSON with current account ID and region
    if command -v sed &> /dev/null; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS sed
            sed -i '' "s/123456789012/$AWS_ACCOUNT_ID/g" ecs-task-definition-temp.json
            sed -i '' "s/us-east-1/$AWS_REGION/g" ecs-task-definition-temp.json
        else
            # Linux sed
            sed -i "s/123456789012/$AWS_ACCOUNT_ID/g" ecs-task-definition-temp.json
            sed -i "s/us-east-1/$AWS_REGION/g" ecs-task-definition-temp.json
        fi
    else
        print_error "sed command not found. Please install sed or manually update ecs-task-definition.json"
        exit 1
    fi
    
    print_success "Task definition updated with Account ID: $AWS_ACCOUNT_ID and Region: $AWS_REGION"
}

# Function to setup required IAM roles
setup_iam_roles() {
    print_status "Setting up IAM roles..."
    
    # Check and create ECS Task Execution Role
    if ! aws iam get-role --role-name ecsTaskExecutionRole &> /dev/null; then
        print_status "Creating ECS Task Execution Role..."
        aws iam create-role \
            --role-name ecsTaskExecutionRole \
            --assume-role-policy-document '{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ecs-tasks.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }' > /dev/null
        
        aws iam attach-role-policy \
            --role-name ecsTaskExecutionRole \
            --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
        print_success "ECS Task Execution Role created"
    else
        print_success "ECS Task Execution Role already exists"
    fi
    
    # Add Secrets Manager permissions to execution role
    print_status "Adding Secrets Manager permissions to execution role..."
    aws iam put-role-policy \
        --role-name ecsTaskExecutionRole \
        --policy-name SecretsManagerAccess \
        --policy-document '{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "secretsmanager:GetSecretValue"
                    ],
                    "Resource": [
                        "arn:aws:secretsmanager:'$AWS_REGION':'$AWS_ACCOUNT_ID':secret:document-portal/*"
                    ]
                }
            ]
        }' > /dev/null
    print_success "Secrets Manager permissions added"
    
    # Check and create ECS Task Role
    if ! aws iam get-role --role-name ecsTaskRole &> /dev/null; then
        print_status "Creating ECS Task Role..."
        aws iam create-role \
            --role-name ecsTaskRole \
            --assume-role-policy-document '{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ecs-tasks.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }' > /dev/null
        print_success "ECS Task Role created"
    else
        print_success "ECS Task Role already exists"
    fi
}

# Function to setup secrets
setup_secrets() {
    print_status "Setting up API key secrets..."
    
    # Check and create GROQ API key secret
    if ! aws secretsmanager describe-secret --secret-id document-portal/groq-api-key --region $AWS_REGION &> /dev/null; then
        print_status "Creating placeholder GROQ API key secret..."
        aws secretsmanager create-secret \
            --name document-portal/groq-api-key \
            --description "GROQ API key for document portal" \
            --secret-string "PLACEHOLDER_GROQ_KEY_REPLACE_WITH_ACTUAL_KEY" \
            --region $AWS_REGION > /dev/null
        print_warning "Created placeholder GROQ API key. Please update with actual key:"
        echo "aws secretsmanager update-secret --secret-id document-portal/groq-api-key --secret-string 'your-actual-groq-key' --region $AWS_REGION"
    else
        print_success "GROQ API key secret already exists"
    fi
    
    # Check and create Google API key secret
    if ! aws secretsmanager describe-secret --secret-id document-portal/google-api-key --region $AWS_REGION &> /dev/null; then
        print_status "Creating placeholder Google API key secret..."
        aws secretsmanager create-secret \
            --name document-portal/google-api-key \
            --description "Google API key for document portal" \
            --secret-string "PLACEHOLDER_GOOGLE_KEY_REPLACE_WITH_ACTUAL_KEY" \
            --region $AWS_REGION > /dev/null
        print_warning "Created placeholder Google API key. Please update with actual key:"
        echo "aws secretsmanager update-secret --secret-id document-portal/google-api-key --secret-string 'your-actual-google-key' --region $AWS_REGION"
    else
        print_success "Google API key secret already exists"
    fi
}

# Function to setup networking (VPC, subnets, security groups)
setup_networking() {
    print_status "Setting up networking..."
    
    # Get default VPC
    DEFAULT_VPC=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text 2>/dev/null || echo "None")
    
    if [ "$DEFAULT_VPC" = "None" ] || [ "$DEFAULT_VPC" = "null" ]; then
        print_error "No default VPC found. Please create a VPC manually or use CloudFormation template."
        exit 1
    fi
    
    print_success "Using default VPC: $DEFAULT_VPC"
    
    # Get subnets from default VPC
    SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$DEFAULT_VPC" --query 'Subnets[0:2].SubnetId' --output text)
    if [ -z "$SUBNETS" ]; then
        print_error "No subnets found in default VPC"
        exit 1
    fi
    
    SUBNET_1=$(echo $SUBNETS | cut -d' ' -f1)
    SUBNET_2=$(echo $SUBNETS | cut -d' ' -f2)
    print_success "Using subnets: $SUBNET_1, $SUBNET_2"
    
    # Create security group if it doesn't exist
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=document-portal-sg" "Name=vpc-id,Values=$DEFAULT_VPC" \
        --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "None")
    
    if [ "$SECURITY_GROUP_ID" = "None" ] || [ "$SECURITY_GROUP_ID" = "null" ]; then
        print_status "Creating security group..."
        SECURITY_GROUP_ID=$(aws ec2 create-security-group \
            --group-name document-portal-sg \
            --description "Security group for Document Portal ECS service" \
            --vpc-id $DEFAULT_VPC \
            --query 'GroupId' --output text)
        
        # Add inbound rule for port 8080
        aws ec2 authorize-security-group-ingress \
            --group-id $SECURITY_GROUP_ID \
            --protocol tcp \
            --port 8080 \
            --cidr 0.0.0.0/0 > /dev/null
        
        print_success "Security group created: $SECURITY_GROUP_ID"
    else
        print_success "Using existing security group: $SECURITY_GROUP_ID"
    fi
    
    # Export for use in service creation
    export VPC_ID=$DEFAULT_VPC
    export SUBNET_1=$SUBNET_1
    export SUBNET_2=$SUBNET_2
    export SECURITY_GROUP_ID=$SECURITY_GROUP_ID
}
# Function to check if ECS cluster exists, create if not
setup_ecs_cluster() {
    print_status "Setting up ECS cluster..."
    
    if aws ecs describe-clusters --clusters $ECS_CLUSTER --region $AWS_REGION --query 'clusters[0].status' --output text 2>/dev/null | grep -q "ACTIVE"; then
        print_success "ECS cluster '$ECS_CLUSTER' already exists and is active"
    else
        print_status "Creating ECS cluster '$ECS_CLUSTER'..."
        aws ecs create-cluster \
            --cluster-name $ECS_CLUSTER \
            --capacity-providers FARGATE \
            --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
            --region $AWS_REGION > /dev/null
        print_success "ECS cluster created successfully"
    fi
}

# Function to register task definition
register_task_definition() {
    print_status "Registering task definition..."
    
    TASK_DEF_ARN=$(aws ecs register-task-definition \
        --cli-input-json file://ecs-task-definition-temp.json \
        --region $AWS_REGION \
        --query 'taskDefinition.taskDefinitionArn' \
        --output text)
    
    print_success "Task definition registered: $TASK_DEF_ARN"
}

# Function to update or create ECS service
deploy_service() {
    print_status "Deploying ECS service..."
    
    # Check if service exists
    if aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE --region $AWS_REGION --query 'services[0].status' --output text 2>/dev/null | grep -q "ACTIVE"; then
        print_status "Updating existing service..."
        aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --task-definition $TASK_DEFINITION \
            --force-new-deployment \
            --region $AWS_REGION > /dev/null
        print_success "Service update initiated"
    else
        print_status "Creating new ECS service..."
        # Ensure we have networking variables
        if [ -z "$SUBNET_1" ] || [ -z "$SECURITY_GROUP_ID" ]; then
            print_error "Networking not properly set up. Please run setup_networking first."
            exit 1
        fi
        
        # Create the service
        aws ecs create-service \
            --cluster $ECS_CLUSTER \
            --service-name $ECS_SERVICE \
            --task-definition $TASK_DEFINITION:1 \
            --desired-count 1 \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1,$SUBNET_2],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
            --region $AWS_REGION > /dev/null
        
        print_success "ECS service created successfully"
    fi
}

# Function to wait for deployment to complete
wait_for_deployment() {
    print_status "Waiting for deployment to stabilize..."
    
    if aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE --region $AWS_REGION --query 'services[0].status' --output text 2>/dev/null | grep -q "ACTIVE"; then
        aws ecs wait services-stable \
            --cluster $ECS_CLUSTER \
            --services $ECS_SERVICE \
            --region $AWS_REGION
        print_success "Deployment completed successfully!"
        
        # Get service status
        print_status "Service status:"
        aws ecs describe-services \
            --cluster $ECS_CLUSTER \
            --services $ECS_SERVICE \
            --region $AWS_REGION \
            --query 'services[0].{Status:status,RunningCount:runningCount,PendingCount:pendingCount,DesiredCount:desiredCount}'
    else
        print_warning "Service not found - skipping deployment wait"
    fi
}

# Function to clean up backup files
cleanup() {
    print_status "Cleaning up..."
    rm -f ecs-task-definition.json.bak
    rm -f ecs-task-definition-temp.json
    print_success "Cleanup completed"
}

# Function to get service public IP and URL
get_service_info() {
    print_status "Getting service information..."
    
    # Wait a moment for tasks to start
    sleep 10
    
    # Get task ARN
    TASK_ARN=$(aws ecs list-tasks \
        --cluster $ECS_CLUSTER \
        --service-name $ECS_SERVICE \
        --region $AWS_REGION \
        --query 'taskArns[0]' \
        --output text 2>/dev/null || echo "None")
    
    if [ "$TASK_ARN" != "None" ] && [ "$TASK_ARN" != "null" ] && [ -n "$TASK_ARN" ]; then
        # Get task details including network interface
        ENI_ID=$(aws ecs describe-tasks \
            --cluster $ECS_CLUSTER \
            --tasks $TASK_ARN \
            --region $AWS_REGION \
            --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
            --output text 2>/dev/null || echo "None")
        
        if [ "$ENI_ID" != "None" ] && [ "$ENI_ID" != "null" ] && [ -n "$ENI_ID" ]; then
            # Get public IP from ENI
            PUBLIC_IP=$(aws ec2 describe-network-interfaces \
                --network-interface-ids $ENI_ID \
                --region $AWS_REGION \
                --query 'NetworkInterfaces[0].Association.PublicIp' \
                --output text 2>/dev/null || echo "None")
            
            if [ "$PUBLIC_IP" != "None" ] && [ "$PUBLIC_IP" != "null" ] && [ -n "$PUBLIC_IP" ]; then
                print_success "Service is accessible at: http://$PUBLIC_IP:8080"
                print_success "Health check: http://$PUBLIC_IP:8080/health"
                
                # Test health endpoint
                print_status "Testing health endpoint..."
                sleep 30  # Wait for service to fully start
                if curl -s --connect-timeout 10 http://$PUBLIC_IP:8080/health > /dev/null 2>&1; then
                    print_success "Health check passed! Service is running properly."
                else
                    print_warning "Health check failed. Service may still be starting up."
                    print_status "You can check logs with: aws logs tail /ecs/document-portal --follow --region $AWS_REGION"
                fi
            else
                print_warning "Could not retrieve public IP. Service may still be starting."
            fi
        else
            print_warning "Could not retrieve network interface. Service may still be starting."
        fi
    else
        print_warning "No tasks found. Service may still be starting."
    fi
}
# Function to display next steps
show_next_steps() {
    print_success "Deployment process completed!"
    echo ""
    echo -e "${BLUE}What was deployed:${NC}"
    echo "✅ ECR Repository: $ECR_REPOSITORY"
    echo "✅ ECS Cluster: $ECS_CLUSTER"
    echo "✅ ECS Service: $ECS_SERVICE"
    echo "✅ Task Definition: $TASK_DEFINITION"
    echo "✅ Security Group: $SECURITY_GROUP_ID"
    echo "✅ IAM Roles: ecsTaskExecutionRole, ecsTaskRole"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. ✅ Basic infrastructure is set up and running"
    echo "2. 🔄 Set up your API keys in AWS Secrets Manager:"
    echo "   aws secretsmanager create-secret --name document-portal/groq-api-key --secret-string 'your-groq-key'"
    echo "   aws secretsmanager create-secret --name document-portal/google-api-key --secret-string 'your-google-key'"
    echo "3. 🔄 Configure an Application Load Balancer for production (optional)"
    echo "4. 🔄 Set up auto-scaling policies (optional)"
    echo "5. 🔄 Configure monitoring and alerting (optional)"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "# Check service status:"
    echo "aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE --region $AWS_REGION"
    echo ""
    echo "# View logs:"
    echo "aws logs tail /ecs/document-portal --follow --region $AWS_REGION"
    echo ""
    echo "# Scale service:"
    echo "aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --desired-count 2 --region $AWS_REGION"
    echo ""
    echo "# Update service (redeploy):"
    echo "./deploy-to-aws.sh --account-id $AWS_ACCOUNT_ID --region $AWS_REGION"
}

# Main deployment function
main() {
    echo -e "${GREEN}=====================================
AWS ECS/Fargate Deployment Script
Document Portal System
=====================================${NC}"
    
    check_prerequisites
    get_aws_account_id
    setup_iam_roles
    setup_secrets
    setup_ecr_repository
    build_and_push_image
    update_task_definition
    setup_networking
    setup_ecs_cluster
    register_task_definition
    deploy_service
    wait_for_deployment
    get_service_info
    cleanup
    show_next_steps
}

# Handle script interruption
trap cleanup EXIT

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --region)
            AWS_REGION="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --account-id)
            AWS_ACCOUNT_ID="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --region REGION      AWS region (default: us-east-1)"
            echo "  --tag TAG           Docker image tag (default: latest)"
            echo "  --account-id ID     AWS account ID (auto-detected if not provided)"
            echo "  --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Use auto-detected account ID"
            echo "  $0 --account-id 123456789012          # Use specific account ID"
            echo "  $0 --region us-west-2 --tag v1.0      # Custom region and tag"
            echo "  $0 --account-id 987654321098 --region eu-west-1  # Different account and region"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main
