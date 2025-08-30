#!/bin/bash

# Development Mode Deployment Script
# Optimized for cost savings and development workflow

set -e

# Configuration
AWS_REGION="us-east-1"
CLUSTER_NAME="document-portal-cluster"
SERVICE_NAME="document-portal-service"
TASK_FAMILY="document-portal-task"
ECR_REPOSITORY="document-portal-system"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 DEVELOPMENT MODE DEPLOYMENT${NC}"
echo -e "${BLUE}================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS CLI not configured. Please run 'aws configure'"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
print_status "Using AWS Account: $ACCOUNT_ID"

# Development Mode Options Menu
echo -e "\n${YELLOW}📋 DEVELOPMENT MODE OPTIONS:${NC}"
echo "1) 💰 Cost-Optimized (0.5 vCPU, 1GB RAM) - ~$17/month"
echo "2) 🕐 Schedule-Based (8 hours/day) - ~$8/month"
echo "3) 💸 Fargate Spot (70% savings) - ~$10/month"
echo "4) 🛑 Shutdown Service (Stop all tasks) - $0/month"
echo "5) 📊 Check Current Status"
echo "6) 🔄 Standard Restart"

echo ""
read -p "Choose deployment mode (1-6): " choice

case $choice in
    1)
        print_status "Deploying COST-OPTIMIZED mode (0.5 vCPU, 1GB RAM)..."
        
        # Create optimized task definition
        cat > /tmp/dev-task-definition.json << EOF
{
    "family": "$TASK_FAMILY",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskRole",
    "containerDefinitions": [
        {
            "name": "document-portal",
            "image": "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest",
            "portMappings": [
                {
                    "containerPort": 8080,
                    "protocol": "tcp"
                }
            ],
            "essential": true,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/document-portal",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "secrets": [
                {
                    "name": "GROQ_API_KEY",
                    "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$ACCOUNT_ID:secret:document-portal/groq-api-key"
                },
                {
                    "name": "GOOGLE_API_KEY", 
                    "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$ACCOUNT_ID:secret:document-portal/google-api-key"
                }
            ],
            "environment": [
                {
                    "name": "ENVIRONMENT",
                    "value": "development"
                }
            ]
        }
    ]
}
EOF
        
        # Register new task definition
        print_status "Registering optimized task definition..."
        TASK_DEF_ARN=$(aws ecs register-task-definition \
            --cli-input-json file:///tmp/dev-task-definition.json \
            --query 'taskDefinition.taskDefinitionArn' \
            --output text)
        
        print_status "Task definition registered: $TASK_DEF_ARN"
        
        # Update service
        print_status "Updating service with cost-optimized configuration..."
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --task-definition $TASK_FAMILY \
            --desired-count 1 \
            --region $AWS_REGION > /dev/null
        
        print_status "✅ COST-OPTIMIZED mode deployed! (~$17/month)"
        ;;
        
    2)
        print_warning "Schedule-based deployment requires setting up CloudWatch Events/EventBridge"
        print_status "For now, scaling down to 0. You can scale up when needed."
        
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --desired-count 0 \
            --region $AWS_REGION > /dev/null
            
        print_status "✅ Service scaled to 0. Use option 6 to restart when needed."
        print_status "💡 To implement full schedule-based scaling, set up EventBridge rules"
        ;;
        
    3)
        print_status "Deploying FARGATE SPOT mode (70% cost savings)..."
        
        # Update cluster to support Spot
        print_status "Configuring Fargate Spot capacity providers..."
        aws ecs put-cluster-capacity-providers \
            --cluster $CLUSTER_NAME \
            --capacity-providers FARGATE_SPOT FARGATE \
            --default-capacity-provider-strategy \
                capacityProvider=FARGATE_SPOT,weight=3 \
                capacityProvider=FARGATE,weight=1 \
            --region $AWS_REGION > /dev/null 2>&1 || true
        
        # Update service to use capacity provider strategy
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --desired-count 1 \
            --capacity-provider-strategy \
                capacityProvider=FARGATE_SPOT,weight=1 \
            --region $AWS_REGION > /dev/null
            
        print_status "✅ FARGATE SPOT mode deployed! (~70% cost savings)"
        print_warning "Note: Spot instances may be interrupted with 2-minute notice"
        ;;
        
    4)
        print_status "Shutting down service to stop all costs..."
        
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --desired-count 0 \
            --region $AWS_REGION > /dev/null
            
        print_status "✅ Service shut down. Costs reduced to ~$1/month (storage only)"
        print_status "Use option 6 to restart when needed"
        ;;
        
    5)
        print_status "Checking current deployment status..."
        
        # Get service info
        SERVICE_INFO=$(aws ecs describe-services \
            --cluster $CLUSTER_NAME \
            --services $SERVICE_NAME \
            --region $AWS_REGION \
            --query 'services[0].{Status:status,DesiredCount:desiredCount,RunningCount:runningCount,TaskDefinition:taskDefinition}' 2>/dev/null || echo "null")
        
        if [ "$SERVICE_INFO" != "null" ]; then
            echo -e "${GREEN}📊 Current Service Status:${NC}"
            echo "$SERVICE_INFO"
            
            # Get task definition details
            TASK_DEF=$(aws ecs describe-services \
                --cluster $CLUSTER_NAME \
                --services $SERVICE_NAME \
                --region $AWS_REGION \
                --query 'services[0].taskDefinition' \
                --output text 2>/dev/null || echo "null")
            
            if [ "$TASK_DEF" != "null" ]; then
                TASK_INFO=$(aws ecs describe-task-definition \
                    --task-definition "$TASK_DEF" \
                    --region $AWS_REGION \
                    --query 'taskDefinition.{Cpu:cpu,Memory:memory,RequiresCompatibilities:requiresCompatibilities}')
                
                echo -e "${GREEN}💻 Current Task Configuration:${NC}"
                echo "$TASK_INFO"
            fi
            
            # Get public IP if running
            RUNNING_COUNT=$(aws ecs describe-services \
                --cluster $CLUSTER_NAME \
                --services $SERVICE_NAME \
                --region $AWS_REGION \
                --query 'services[0].runningCount' \
                --output text 2>/dev/null || echo "0")
            if [ "$RUNNING_COUNT" -gt 0 ]; then
                print_status "Getting service endpoint..."
                TASK_ARN=$(aws ecs list-tasks \
                    --cluster $CLUSTER_NAME \
                    --service-name $SERVICE_NAME \
                    --region $AWS_REGION \
                    --query 'taskArns[0]' \
                    --output text 2>/dev/null || echo "None")
                
                if [ "$TASK_ARN" != "None" ] && [ "$TASK_ARN" != "null" ]; then
                    ENI_ID=$(aws ecs describe-tasks \
                        --cluster $CLUSTER_NAME \
                        --tasks $TASK_ARN \
                        --region $AWS_REGION \
                        --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
                        --output text 2>/dev/null || echo "")
                    
                    if [ -n "$ENI_ID" ]; then
                        PUBLIC_IP=$(aws ec2 describe-network-interfaces \
                            --network-interface-ids $ENI_ID \
                            --region $AWS_REGION \
                            --query 'NetworkInterfaces[0].Association.PublicIp' \
                            --output text 2>/dev/null || echo "")
                        
                        if [ -n "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "None" ]; then
                            echo -e "${GREEN}🌐 Service URL: http://$PUBLIC_IP:8080${NC}"
                            echo -e "${GREEN}🏥 Health Check: http://$PUBLIC_IP:8080/health${NC}"
                        fi
                    fi
                fi
            fi
        else
            print_error "Service not found or not accessible"
        fi
        ;;
        
    6)
        print_status "Restarting service with standard configuration..."
        
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --desired-count 1 \
            --force-new-deployment \
            --region $AWS_REGION > /dev/null
            
        print_status "✅ Service restarted"
        ;;
        
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

# Wait for deployment if service is being updated
if [ "$choice" != "4" ] && [ "$choice" != "5" ]; then
    print_status "Waiting for deployment to stabilize..."
    
    for i in {1..12}; do
        SERVICE_STATUS=$(aws ecs describe-services \
            --cluster $CLUSTER_NAME \
            --services $SERVICE_NAME \
            --region $AWS_REGION \
            --query 'services[0].{DesiredCount:desiredCount,RunningCount:runningCount}' 2>/dev/null || echo "null")
        
        if [ "$SERVICE_STATUS" != "null" ]; then
            DESIRED=$(aws ecs describe-services \
                --cluster $CLUSTER_NAME \
                --services $SERVICE_NAME \
                --region $AWS_REGION \
                --query 'services[0].desiredCount' \
                --output text 2>/dev/null || echo "0")
            RUNNING=$(aws ecs describe-services \
                --cluster $CLUSTER_NAME \
                --services $SERVICE_NAME \
                --region $AWS_REGION \
                --query 'services[0].runningCount' \
                --output text 2>/dev/null || echo "0")
            
            echo -ne "\r${BLUE}[INFO]${NC} Deployment progress: $RUNNING/$DESIRED tasks running..."
            
            if [ "$RUNNING" -eq "$DESIRED" ] && [ "$DESIRED" -gt 0 ]; then
                echo ""
                print_status "✅ Deployment stabilized!"
                
                # Get and display service URL
                sleep 5
                TASK_ARN=$(aws ecs list-tasks \
                    --cluster $CLUSTER_NAME \
                    --service-name $SERVICE_NAME \
                    --region $AWS_REGION \
                    --query 'taskArns[0]' \
                    --output text 2>/dev/null || echo "None")
                
                if [ "$TASK_ARN" != "None" ] && [ "$TASK_ARN" != "null" ]; then
                    ENI_ID=$(aws ecs describe-tasks \
                        --cluster $CLUSTER_NAME \
                        --tasks $TASK_ARN \
                        --region $AWS_REGION \
                        --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
                        --output text 2>/dev/null || echo "")
                    
                    if [ -n "$ENI_ID" ]; then
                        PUBLIC_IP=$(aws ec2 describe-network-interfaces \
                            --network-interface-ids $ENI_ID \
                            --region $AWS_REGION \
                            --query 'NetworkInterfaces[0].Association.PublicIp' \
                            --output text 2>/dev/null || echo "")
                        
                        if [ -n "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "None" ]; then
                            echo -e "\n${GREEN}🎉 Development deployment complete!${NC}"
                            echo -e "${GREEN}🌐 Service URL: http://$PUBLIC_IP:8080${NC}"
                            echo -e "${GREEN}🏥 Health Check: http://$PUBLIC_IP:8080/health${NC}"
                            
                            # Test health endpoint
                            echo -e "\n${BLUE}Testing health endpoint...${NC}"
                            if curl -s "http://$PUBLIC_IP:8080/health" > /dev/null 2>&1; then
                                print_status "✅ Health check passed!"
                            else
                                print_warning "Health check failed - service may still be starting"
                            fi
                        fi
                    fi
                fi
                break
            elif [ "$DESIRED" -eq 0 ]; then
                echo ""
                print_status "✅ Service scaled to 0 tasks"
                break
            fi
        fi
        
        sleep 10
    done
fi

echo -e "\n${BLUE}📊 COST SUMMARY:${NC}"
echo "• Standard (1 vCPU, 2GB): ~$35/month"
echo "• Cost-Optimized (0.5 vCPU, 1GB): ~$17/month"
echo "• Fargate Spot: ~$10/month"
echo "• Shutdown: ~$1/month (storage only)"

echo -e "\n${GREEN}Development mode deployment complete! 🚀${NC}"

# Cleanup temp files
rm -f /tmp/dev-task-definition.json
