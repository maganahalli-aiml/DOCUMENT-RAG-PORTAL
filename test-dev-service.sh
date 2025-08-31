#!/bin/bash

# Development Mode Testing Script
# Quick tests for the deployed development service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current service URL
echo -e "${BLUE}🔍 Finding Development Service...${NC}"

CLUSTER_NAME="document-portal-cluster"
SERVICE_NAME="document-portal-service"
AWS_REGION="us-east-1"

# Get running task
TASK_ARN=$(aws ecs list-tasks \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'taskArns[0]' \
    --output text 2>/dev/null || echo "None")

if [ "$TASK_ARN" == "None" ] || [ "$TASK_ARN" == "null" ]; then
    echo -e "${RED}❌ No running tasks found. Service may be stopped.${NC}"
    echo -e "${YELLOW}💡 Run './deploy-dev-mode.sh' and choose option 1 or 6 to start the service${NC}"
    exit 1
fi

# Get public IP
ENI_ID=$(aws ecs describe-tasks \
    --cluster $CLUSTER_NAME \
    --tasks $TASK_ARN \
    --region $AWS_REGION \
    --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
    --output text 2>/dev/null || echo "")

if [ -z "$ENI_ID" ]; then
    echo -e "${RED}❌ Could not get network interface ID${NC}"
    exit 1
fi

PUBLIC_IP=$(aws ec2 describe-network-interfaces \
    --network-interface-ids $ENI_ID \
    --region $AWS_REGION \
    --query 'NetworkInterfaces[0].Association.PublicIp' \
    --output text 2>/dev/null || echo "")

if [ -z "$PUBLIC_IP" ] || [ "$PUBLIC_IP" == "None" ]; then
    echo -e "${RED}❌ Could not get public IP${NC}"
    exit 1
fi

BASE_URL="http://$PUBLIC_IP:8080"

echo -e "${GREEN}✅ Found service at: $BASE_URL${NC}"
echo ""

# Test 1: Health Check
echo -e "${BLUE}🏥 Testing Health Endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/health" || echo "ERROR")

if [[ $HEALTH_RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "Response: $(echo "$HEALTH_RESPONSE" | sed 's/HTTP_CODE:.*//')"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Response: $HEALTH_RESPONSE"
fi

echo ""

# Test 2: API Root
echo -e "${BLUE}🌐 Testing API Root...${NC}"
API_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/" || echo "ERROR")

if [[ $API_RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo -e "${GREEN}✅ API root accessible${NC}"
else
    echo -e "${YELLOW}⚠️ API root returned: $(echo "$API_RESPONSE" | grep -o 'HTTP_CODE:.*')${NC}"
fi

echo ""

# Test 3: Check if docs endpoint exists
echo -e "${BLUE}📚 Testing Documentation Endpoint...${NC}"
DOCS_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/docs" || echo "ERROR")

if [[ $DOCS_RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo -e "${GREEN}✅ API docs available at: $BASE_URL/docs${NC}"
else
    echo -e "${YELLOW}⚠️ API docs: $(echo "$DOCS_RESPONSE" | grep -o 'HTTP_CODE:.*')${NC}"
fi

echo ""

# Test 4: Resource usage
echo -e "${BLUE}💻 Checking Resource Configuration...${NC}"
TASK_DEF_ARN=$(aws ecs describe-tasks \
    --cluster $CLUSTER_NAME \
    --tasks $TASK_ARN \
    --region $AWS_REGION \
    --query 'tasks[0].taskDefinitionArn' \
    --output text 2>/dev/null || echo "")

if [ -n "$TASK_DEF_ARN" ]; then
    RESOURCES=$(aws ecs describe-task-definition \
        --task-definition "$TASK_DEF_ARN" \
        --region $AWS_REGION \
        --query 'taskDefinition.{Cpu:cpu,Memory:memory}' \
        --output text 2>/dev/null || echo "")
    
    echo -e "${GREEN}📊 Current Resources: $RESOURCES${NC}"
    
    # Calculate approximate cost
    CPU=$(echo "$RESOURCES" | cut -f1)
    MEMORY=$(echo "$RESOURCES" | cut -f2)
    
    if [ "$CPU" == "512" ] && [ "$MEMORY" == "1024" ]; then
        echo -e "${GREEN}💰 Cost-optimized mode active (~$17/month)${NC}"
    elif [ "$CPU" == "1024" ] && [ "$MEMORY" == "2048" ]; then
        echo -e "${YELLOW}💸 Standard mode active (~$35/month)${NC}"
    else
        echo -e "${BLUE}💻 Custom configuration: $CPU CPU units, $MEMORY MB RAM${NC}"
    fi
fi

echo ""

# Summary
echo -e "${BLUE}📋 DEVELOPMENT SERVICE SUMMARY${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "🌐 Service URL: $BASE_URL"
echo -e "🏥 Health Check: $BASE_URL/health"
echo -e "📚 API Docs: $BASE_URL/docs"
echo -e "💻 Resources: $RESOURCES"
echo ""
echo -e "${GREEN}🎉 Development service is running and accessible!${NC}"
echo ""
echo -e "${YELLOW}💡 Development Tips:${NC}"
echo -e "• Use './deploy-dev-mode.sh' option 4 to stop the service when not needed"
echo -e "• Use './deploy-dev-mode.sh' option 3 for Fargate Spot (70% cost savings)"
echo -e "• Monitor costs with AWS Cost Explorer"
echo -e "• Consider auto-scaling for production workloads"
