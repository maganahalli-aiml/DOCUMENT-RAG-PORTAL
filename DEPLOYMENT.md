# Deployment Guide

## 🚀 Quick Deployment

### Option 1: Docker Compose (Recommended)

#### Development Environment:
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

#### Production Environment with Nginx:
```bash
# Start with nginx reverse proxy
docker-compose --profile production up -d

# Scale the application
docker-compose up -d --scale document-portal=3
```

### Option 2: Direct Docker Run

#### Development:
```bash
# Build the optimized image
docker build -t document-portal-system:optimized .

# Run with volume mounts for data persistence
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/faiss_index:/app/faiss_index \
  -v $(pwd)/logs:/app/logs \
  --name document-portal \
  document-portal-system:optimized
```

#### Production:
```bash
# Run with environment variables and restart policy
docker run -d \
  -p 8080:8080 \
  -v /opt/document-portal/data:/app/data \
  -v /opt/document-portal/faiss_index:/app/faiss_index \
  -v /opt/document-portal/logs:/app/logs \
  -e ENVIRONMENT=production \
  --restart unless-stopped \
  --name document-portal \
  document-portal-system:optimized
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# API Keys (Required)
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_FILE_TYPES=pdf,docx,txt
```

### Volume Mounts

For data persistence, mount these directories:

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./data` | `/app/data` | Uploaded documents and session data |
| `./faiss_index` | `/app/faiss_index` | Vector database indices |
| `./logs` | `/app/logs` | Application logs |

## 🏥 Health Monitoring

### Health Check Endpoint:
```bash
curl http://localhost:8080/health
# Expected response: {"status":"ok","service":"document-portal"}
```

### Container Health:
```bash
# Check container status
docker ps

# View container logs
docker logs document-portal

# Check resource usage
docker stats document-portal
```

## 🔒 Security Considerations

### Production Checklist:

- [ ] **Environment Variables**: Store sensitive keys in secure environment variables
- [ ] **HTTPS**: Enable SSL/TLS with proper certificates
- [ ] **Firewall**: Configure firewall rules for port access
- [ ] **User Permissions**: Run containers as non-root user
- [ ] **File Uploads**: Implement virus scanning for uploaded documents
- [ ] **Rate Limiting**: Configure nginx rate limiting for API endpoints
- [ ] **Backup Strategy**: Regular backups of data and indices

### Security Headers:
The included nginx configuration adds security headers:
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Content-Security-Policy

## 📊 Performance Optimization

### Resource Limits:
```yaml
# Add to docker-compose.yml under services.document-portal
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

### Scaling:
```bash
# Scale horizontally with load balancer
docker-compose up -d --scale document-portal=3

# Update nginx upstream configuration for load balancing
```

## 🔄 Updates and Maintenance

### Updating the Application:
```bash
# Pull latest changes
git pull origin dev

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Data:
```bash
# Backup data directories
tar -czf backup-$(date +%Y%m%d).tar.gz data/ faiss_index/ logs/

# Restore from backup
tar -xzf backup-20250816.tar.gz
```

### Log Rotation:
```bash
# Set up log rotation for container logs
docker logs document-portal 2>&1 | logrotate -s /var/log/docker-portal.state /etc/logrotate.d/docker-portal
```

## 🐛 Troubleshooting

### Common Issues:

1. **Port Already in Use**:
   ```bash
   # Find process using port 8080
   lsof -i :8080
   # Kill the process or use different port
   docker run -p 8081:8080 ...
   ```

2. **Permission Denied on Volume Mounts**:
   ```bash
   # Fix directory permissions
   sudo chown -R 1000:1000 data/ faiss_index/ logs/
   ```

3. **Out of Memory**:
   ```bash
   # Check memory usage
   docker stats
   # Increase Docker memory limit or system resources
   ```

4. **API Key Issues**:
   ```bash
   # Verify environment variables are set
   docker exec document-portal env | grep API_KEY
   ```

### Debug Mode:
```bash
# Run with debug output
docker run -it --rm \
  -p 8080:8080 \
  -e LOG_LEVEL=DEBUG \
  document-portal-system:optimized
```

## 📈 Monitoring

### Application Metrics:
- Health endpoint: `/health`
- Application logs in `/app/logs/`
- Container resource usage with `docker stats`

### Production Monitoring:
Consider integrating with:
- Prometheus + Grafana for metrics
- ELK Stack for centralized logging
- Uptime monitoring services

## 🌐 Production Deployment

### Cloud Deployment Options:

1. **AWS ECS/Fargate** (See detailed guide below)
2. **Google Cloud Run**
3. **Azure Container Instances**
4. **Kubernetes clusters**
5. **Digital Ocean App Platform**

## 🔥 AWS ECS/Fargate Deployment Guide

### Prerequisites:
- AWS CLI installed and configured
- Docker installed locally
- AWS account with appropriate permissions

### Step 1: Install and Configure AWS CLI

```bash
# Install AWS CLI (if not already installed)
brew install awscli

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter default output format (json)

# Verify configuration
aws sts get-caller-identity
```

### Step 2: Create ECR Repository

```bash
# Create ECR repository for your Docker image
aws ecr create-repository \
    --repository-name document-portal-system \
    --region us-east-1

# Get ECR login token and login to Docker
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Note: Replace 123456789012 with your actual AWS account ID
```

### Step 3: Build and Push Docker Image to ECR

```bash
# Build the optimized image
docker build -t document-portal-system:optimized .

# Tag image for ECR
docker tag document-portal-system:optimized \
    123456789012.dkr.ecr.us-east-1.amazonaws.com/document-portal-system:latest

# Push to ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/document-portal-system:latest
```

### Step 4: Create ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster \
    --cluster-name document-portal-cluster \
    --capacity-providers FARGATE \
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
```

### Step 5: Create Task Definition

Create a file `ecs-task-definition.json`:

```json
{
  "family": "document-portal-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "document-portal",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/document-portal-system:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "GROQ_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:document-portal/groq-api-key"
        },
        {
          "name": "GOOGLE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:document-portal/google-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/document-portal",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Step 6: Create IAM Roles and Policies

```bash
# Create ECS Task Execution Role
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
    }'

# Attach managed policy to execution role
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create ECS Task Role for application permissions
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
    }'
```

### Step 7: Create CloudWatch Log Group

```bash
# Create log group for container logs
aws logs create-log-group \
    --log-group-name /ecs/document-portal \
    --region us-east-1
```

### Step 8: Store Secrets in AWS Secrets Manager

```bash
# Store GROQ API key
aws secretsmanager create-secret \
    --name document-portal/groq-api-key \
    --description "GROQ API key for document portal" \
    --secret-string "your-actual-groq-api-key"

# Store Google API key
aws secretsmanager create-secret \
    --name document-portal/google-api-key \
    --description "Google API key for document portal" \
    --secret-string "your-actual-google-api-key"
```

### Step 9: Register Task Definition

```bash
# Register the task definition with ECS
aws ecs register-task-definition \
    --cli-input-json file://ecs-task-definition.json
```

### Step 10: Create ECS Service

```bash
# Create VPC and subnets (if you don't have them)
# Note: You'll need to replace with your actual VPC and subnet IDs

# Create security group
aws ec2 create-security-group \
    --group-name document-portal-sg \
    --description "Security group for document portal ECS service" \
    --vpc-id vpc-12345678

# Add inbound rule for HTTP traffic
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 8080 \
    --cidr 0.0.0.0/0

# Create ECS service
aws ecs create-service \
    --cluster document-portal-cluster \
    --service-name document-portal-service \
    --task-definition document-portal-task:1 \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678,subnet-87654321],securityGroups=[sg-12345678],assignPublicIp=ENABLED}" \
    --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/document-portal-tg/1234567890123456,containerName=document-portal,containerPort=8080
```

### Step 11: Create Application Load Balancer (Optional but Recommended)

```bash
# Create target group
aws elbv2 create-target-group \
    --name document-portal-tg \
    --protocol HTTP \
    --port 8080 \
    --vpc-id vpc-12345678 \
    --target-type ip \
    --health-check-path /health

# Create load balancer
aws elbv2 create-load-balancer \
    --name document-portal-lb \
    --subnets subnet-12345678 subnet-87654321 \
    --security-groups sg-12345678

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/document-portal-lb/1234567890123456 \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/document-portal-tg/1234567890123456
```

### Step 12: Configure Auto Scaling (Optional)

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/document-portal-cluster/document-portal-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 1 \
    --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --resource-id service/document-portal-cluster/document-portal-service \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-name document-portal-scaling-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
        },
        "ScaleOutCooldown": 300,
        "ScaleInCooldown": 300
    }'
```

### Step 13: Verify Deployment

```bash
# Check service status
aws ecs describe-services \
    --cluster document-portal-cluster \
    --services document-portal-service

# Check task status
aws ecs list-tasks \
    --cluster document-portal-cluster \
    --service-name document-portal-service

# View logs
aws logs tail /ecs/document-portal --follow
```

### Step 14: Update Deployment Script

Create `deploy-to-aws.sh`:

```bash
#!/bin/bash

# AWS ECS Deployment Script for Document Portal
set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="123456789012"
ECR_REPOSITORY="document-portal-system"
ECS_CLUSTER="document-portal-cluster"
ECS_SERVICE="document-portal-service"
TASK_DEFINITION="document-portal-task"

# Build and push image
echo "Building Docker image..."
docker build -t $ECR_REPOSITORY:latest .

echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "Tagging and pushing image..."
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

echo "Updating ECS service..."
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --force-new-deployment

echo "Deployment initiated. Checking status..."
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $ECS_SERVICE

echo "Deployment completed successfully!"
```

### 💰 Cost Optimization Tips:

1. **Use Spot Instances**: Consider using Fargate Spot for cost savings
2. **Right-size Resources**: Start with smaller CPU/memory and scale as needed
3. **Schedule Scaling**: Use scheduled scaling for predictable traffic patterns
4. **Use Reserved Capacity**: For consistent workloads, consider savings plans

### 🔍 Monitoring and Debugging:

```bash
# View service events
aws ecs describe-services \
    --cluster document-portal-cluster \
    --services document-portal-service \
    --query 'services[0].events'

# View task logs
aws logs tail /ecs/document-portal --follow

# Check load balancer health
aws elbv2 describe-target-health \
    --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/document-portal-tg/1234567890123456
```

### Container Registry:
```bash
# Tag and push to registry
docker tag document-portal-system:optimized your-registry/document-portal:latest
docker push your-registry/document-portal:latest
```

This comprehensive AWS ECS/Fargate deployment guide provides a production-ready foundation with security, monitoring, auto-scaling, and cost optimization considerations built-in!
