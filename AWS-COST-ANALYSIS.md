# AWS Cost Analysis - Document Portal Deployment

## 💰 **Current Resources & Costs (Account: 484907489651)**

### 🔥 **PAID RESOURCES (Actively Costing Money)**

#### 1. **ECS Fargate Tasks** 💸 **HIGH COST**
- **Configuration**: 1 vCPU (1024 CPU units), 2GB RAM
- **Running**: 1 task continuously (24/7)
- **Cost Breakdown**:
  - **vCPU**: $0.04048 per vCPU per hour
  - **Memory**: $0.004445 per GB per hour
  - **Calculation**:
    - CPU Cost: 1 vCPU × $0.04048 × 24 hours = **$0.97/day**
    - Memory Cost: 2GB × $0.004445 × 24 hours = **$0.21/day**
    - **Total Daily**: ~**$1.18/day**
    - **Monthly**: ~**$35.40/month**
    - **Annual**: ~**$424.80/year**

#### 2. **Elastic Container Registry (ECR)** 💸 **LOW COST**
- **Storage**: ~1.37GB Docker image
- **Cost**: $0.10 per GB per month
- **Monthly**: ~**$0.14/month**
- **Annual**: ~**$1.68/year**

#### 3. **CloudWatch Logs** 💸 **LOW COST**
- **Log Ingestion**: $0.50 per GB ingested
- **Log Storage**: $0.03 per GB per month
- **Estimated**: ~**$1-5/month** (depending on log volume)

#### 4. **Data Transfer** 💸 **VARIABLE COST**
- **Outbound Data**: $0.09 per GB (first 1GB free monthly)
- **Estimated**: ~**$0-10/month** (depending on usage)

#### 5. **Application Load Balancer** 💸 **NOT DEPLOYED**
- **Note**: We're using direct task access, so no ALB costs

#### 6. **NAT Gateway** 💸 **NOT REQUIRED**
- **Note**: Tasks have public IPs, so no NAT Gateway needed

### ✅ **FREE RESOURCES (No Direct Cost)**

#### 1. **VPC and Networking**
- Default VPC usage: **FREE**
- Security Groups: **FREE**
- Subnets: **FREE**
- Route Tables: **FREE**

#### 2. **ECS Cluster**
- ECS Control Plane: **FREE**
- Service definitions: **FREE**

#### 3. **Secrets Manager** 💸 **MINIMAL COST**
- **Cost**: $0.40 per secret per month + API calls
- **Current**: 2 secrets = **$0.80/month**
- **API Calls**: ~$0.05 per 10,000 requests

#### 4. **IAM Roles and Policies**
- Role creation and usage: **FREE**

## 📊 **TOTAL ESTIMATED MONTHLY COST**

| Resource | Monthly Cost |
|----------|-------------|
| **ECS Fargate (1 task)** | **$35.40** |
| ECR Storage | $0.14 |
| CloudWatch Logs | $2.00 |
| Secrets Manager | $0.80 |
| Data Transfer | $2.00 |
| **TOTAL** | **~$40.34/month** |

## 💡 **COST OPTIMIZATION STRATEGIES**

### 🚀 **Immediate Savings (Can Reduce Costs by 60-80%)**

#### 1. **Use Fargate Spot** (Save ~70%)
```bash
# Update service to use Spot instances
aws ecs put-cluster-capacity-providers \
  --cluster document-portal-cluster \
  --capacity-providers FARGATE_SPOT FARGATE \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE_SPOT,weight=3 \
    capacityProvider=FARGATE,weight=1
```
**Savings**: ~$25/month → **New cost: ~$15/month**

#### 2. **Right-Size Resources** (Save ~30-50%)
```bash
# Reduce to 0.5 vCPU and 1GB RAM if sufficient
# Edit task definition with:
# CPU: 512 (0.5 vCPU)
# Memory: 1024 (1GB)
```
**Savings**: ~$17/month → **New cost: ~$18/month**

#### 3. **Schedule-Based Scaling** (Save ~50-90%)
```bash
# Scale down during off-hours (e.g., nights/weekends)
# 8 hours/day instead of 24/7
```
**Savings**: ~$27/month → **New cost: ~$8/month**

### 🛠️ **Advanced Optimizations**

#### 1. **Implement Auto-Scaling**
- Scale based on CPU utilization
- Scale to 0 during no-usage periods
- Use Application Auto Scaling

#### 2. **Use Reserved Capacity** (Save ~30%)
- For predictable workloads
- 1-year or 3-year commitments

#### 3. **Optimize Logging**
- Reduce log retention period
- Filter out unnecessary logs
- Use log groups with shorter retention

#### 4. **Bundle Multiple Services**
- Run multiple containers in one task
- Share resources more efficiently

## ⚠️ **COST MONITORING ALERTS**

### Set up billing alerts:
```bash
# Create billing alarm for $50/month
aws cloudwatch put-metric-alarm \
  --alarm-name "DocumentPortal-BillingAlarm" \
  --alarm-description "Alert when monthly bill exceeds $50" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=Currency,Value=USD \
  --evaluation-periods 1
```

## 🎯 **RECOMMENDED IMMEDIATE ACTIONS**

### For Development/Testing:
1. **Enable Fargate Spot**: Reduce costs by 70%
2. **Scale down resources**: Use 0.5 vCPU, 1GB RAM
3. **Set up auto-scaling**: Scale to 0 during off-hours
4. **Expected Monthly Cost**: **$5-10/month**

### For Production:
1. **Use mixed capacity**: 70% Spot, 30% On-Demand
2. **Implement auto-scaling**: 1-5 tasks based on demand
3. **Add Application Load Balancer**: For high availability
4. **Expected Monthly Cost**: **$20-40/month**

## 🛑 **HOW TO STOP ALL COSTS**

### Complete Shutdown:
```bash
# Delete ECS service (stops all tasks)
aws ecs delete-service \
  --cluster document-portal-cluster \
  --service document-portal-service \
  --force

# Delete ECR images
aws ecr batch-delete-image \
  --repository-name document-portal-system \
  --image-ids imageTag=latest

# Delete secrets
aws secretsmanager delete-secret \
  --secret-id document-portal/groq-api-key \
  --force-delete-without-recovery

aws secretsmanager delete-secret \
  --secret-id document-portal/google-api-key \
  --force-delete-without-recovery
```

## 📈 **Cost Tracking Commands**

```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=2025-08-01,End=2025-08-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Get ECS-specific costs
aws ce get-cost-and-usage \
  --time-period Start=2025-08-01,End=2025-08-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## 🎉 **Summary**

- **Current Monthly Cost**: ~$40
- **With Spot Instances**: ~$15/month
- **With Right-Sizing**: ~$8/month  
- **Development Mode**: ~$5/month
- **Complete Shutdown**: $0/month

The Document Portal is currently in **always-on production mode**. Consider implementing the optimization strategies based on your usage patterns!
