# AWS ECS/Fargate Deployment - Quick Start Guide

## 🚀 One-Click Infrastructure Setup

### Option 1: CloudFormation Template (Recommended)

Deploy complete infrastructure with one command:

```bash
# Deploy the stack
aws cloudformation create-stack \
  --stack-name document-portal-production \
  --template-body file://cloudformation-template.yml \
  --parameters \
    ParameterKey=GroqApiKey,ParameterValue=your-groq-api-key \
    ParameterKey=GoogleApiKey,ParameterValue=your-google-api-key \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Monitor deployment progress
aws cloudformation describe-stack-events \
  --stack-name document-portal-production \
  --region us-east-1
```

### Option 2: Automated Script

Use the automated deployment script:

```bash
# Make script executable
chmod +x deploy-to-aws.sh

# Run deployment (will auto-detect your AWS account)
./deploy-to-aws.sh

# Or with custom parameters
./deploy-to-aws.sh --region us-west-2 --tag v1.0
```

## 📋 Prerequisites

1. **AWS CLI** configured with appropriate permissions:
   ```bash
   aws configure
   ```

2. **Docker** installed locally

3. **Required AWS Permissions**:
   - ECR (Elastic Container Registry)
   - ECS (Elastic Container Service)
   - IAM (Identity and Access Management)
   - VPC (Virtual Private Cloud)
   - Application Load Balancer
   - Secrets Manager
   - CloudWatch Logs

## 🔑 API Keys Setup

Before deployment, store your API keys in AWS Secrets Manager:

```bash
# Store GROQ API key
aws secretsmanager create-secret \
  --name document-portal/groq-api-key \
  --secret-string "your-actual-groq-api-key" \
  --region us-east-1

# Store Google API key
aws secretsmanager create-secret \
  --name document-portal/google-api-key \
  --secret-string "your-actual-google-api-key" \
  --region us-east-1
```

## 🏗️ What Gets Created

The CloudFormation template creates:

### Networking:
- ✅ VPC with public subnets
- ✅ Internet Gateway and route tables
- ✅ Security groups with proper rules

### Compute:
- ✅ ECS Fargate cluster
- ✅ ECS service with auto-scaling
- ✅ Application Load Balancer

### Storage & Security:
- ✅ ECR repository for Docker images
- ✅ S3 bucket for document storage
- ✅ Secrets Manager for API keys
- ✅ CloudWatch logs

### Monitoring:
- ✅ Auto-scaling policies
- ✅ Health checks
- ✅ CloudWatch monitoring

## 🔄 Deployment Process

1. **Infrastructure Setup** (CloudFormation)
2. **Build & Push Image** (Automated script)
3. **Deploy Service** (ECS)
4. **Verify Health** (Load Balancer)

## 📊 Post-Deployment Verification

Check deployment status:

```bash
# Get stack outputs (includes Load Balancer URL)
aws cloudformation describe-stacks \
  --stack-name document-portal-production \
  --query 'Stacks[0].Outputs'

# Check ECS service health
aws ecs describe-services \
  --cluster document-portal-cluster-production \
  --services document-portal-service-production

# View application logs
aws logs tail /ecs/document-portal --follow
```

## 🌐 Access Your Application

After successful deployment:

1. **Get Load Balancer URL** from CloudFormation outputs
2. **Access the application** at `http://your-alb-url`
3. **Health check** available at `http://your-alb-url/health`

## 🔧 Maintenance Commands

```bash
# Update the application
./deploy-to-aws.sh

# Scale the service
aws ecs update-service \
  --cluster document-portal-cluster-production \
  --service document-portal-service-production \
  --desired-count 5

# View service metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=document-portal-service-production \
  --start-time 2025-08-22T00:00:00Z \
  --end-time 2025-08-22T23:59:59Z \
  --period 300 \
  --statistics Average
```

## 💰 Cost Optimization

- **Fargate Spot**: Use spot instances for cost savings
- **Auto Scaling**: Scales down during low usage
- **Resource Limits**: Right-sized CPU and memory
- **Log Retention**: 30-day retention to control costs

## 🔒 Security Features

- ✅ **VPC Isolation**: Private networking
- ✅ **IAM Roles**: Least privilege access
- ✅ **Secrets Management**: API keys in Secrets Manager
- ✅ **Container Security**: Non-root user execution
- ✅ **Network Security**: Security groups and NACLs

## 🐛 Troubleshooting

### Common Issues:

1. **Task fails to start**:
   ```bash
   aws ecs describe-tasks --cluster document-portal-cluster-production --tasks task-id
   ```

2. **Health check failures**:
   ```bash
   aws logs tail /ecs/document-portal --follow
   ```

3. **Load balancer issues**:
   ```bash
   aws elbv2 describe-target-health --target-group-arn your-target-group-arn
   ```

## 📈 Monitoring & Alerts

Set up CloudWatch alarms:

```bash
# CPU utilization alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "DocumentPortal-HighCPU" \
  --alarm-description "Document Portal high CPU usage" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

Your document portal is now production-ready on AWS! 🎉
