# Development Mode Deployment Guide

## 🚀 Quick Start

The Document Portal is now deployed in **cost-optimized development mode**!

### Current Status
- **Service URL**: http://3.234.251.124:8080
- **Health Check**: http://3.234.251.124:8080/health  
- **API Documentation**: http://3.234.251.124:8080/docs
- **Configuration**: 0.5 vCPU, 1GB RAM (Cost-optimized)
- **Monthly Cost**: ~$17 (50% savings vs standard)

## 🛠️ Development Scripts

### 1. Deploy Development Mode
```bash
./deploy-dev-mode.sh
```

**Available Options:**
- **Option 1**: 💰 Cost-Optimized (0.5 vCPU, 1GB) - ~$17/month
- **Option 2**: 🕐 Schedule-Based (8h/day) - ~$8/month  
- **Option 3**: 💸 Fargate Spot (70% savings) - ~$10/month
- **Option 4**: 🛑 Shutdown Service - $0/month
- **Option 5**: 📊 Check Current Status
- **Option 6**: 🔄 Standard Restart

### 2. Test Development Service
```bash
./test-dev-service.sh
```

Runs comprehensive tests on your development deployment.

## 💰 Cost Management

### Current Costs (Development Mode)
| Mode | CPU | Memory | Monthly Cost | Savings |
|------|-----|--------|-------------|---------|
| **Current (Cost-Optimized)** | 0.5 vCPU | 1GB | **~$17** | **50%** |
| Standard | 1 vCPU | 2GB | ~$35 | 0% |
| Fargate Spot | 0.5 vCPU | 1GB | ~$10 | 70% |
| Shutdown | - | - | ~$1 | 97% |

### Cost Optimization Tips

#### For Active Development:
```bash
# Use Fargate Spot for maximum savings
./deploy-dev-mode.sh
# Choose option 3
```

#### When Not Developing:
```bash
# Shutdown to stop all compute costs
./deploy-dev-mode.sh  
# Choose option 4
```

#### To Restart:
```bash
# Quick restart
./deploy-dev-mode.sh
# Choose option 6
```

## 🔧 Development Workflow

### 1. Daily Development
1. **Start Service**: `./deploy-dev-mode.sh` → Option 1 or 3
2. **Test Changes**: `./test-dev-service.sh`
3. **Stop When Done**: `./deploy-dev-mode.sh` → Option 4

### 2. Code Updates
1. **Build New Image**: Update your code and rebuild Docker image
2. **Push to ECR**: Push updated image to AWS ECR
3. **Deploy**: `./deploy-dev-mode.sh` → Option 6 (force new deployment)

### 3. Resource Monitoring
```bash
# Check current status
./deploy-dev-mode.sh  # Option 5

# View AWS costs
aws ce get-cost-and-usage \
  --time-period Start=2025-08-01,End=2025-08-31 \
  --granularity DAILY \
  --metrics BlendedCost
```

## 🌐 Service Endpoints

### Base URL: http://3.234.251.124:8080

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `/health` | Health check | `curl http://3.234.251.124:8080/health` |
| `/docs` | API documentation | Open in browser |
| `/` | API root | API status |

### Testing Commands
```bash
# Health check
curl http://3.234.251.124:8080/health

# Test with data (example)
curl -X POST http://3.234.251.124:8080/upload \
  -F "file=@test-document.pdf"

# Check API docs
open http://3.234.251.124:8080/docs
```

## 🚨 Important Notes

### Security
- Service runs in public subnet with direct internet access
- API keys stored securely in AWS Secrets Manager
- Consider VPN or IP restrictions for production

### Resource Limits
- **Current**: 0.5 vCPU, 1GB RAM
- **Good for**: Light development, testing, small documents
- **Upgrade if**: Processing large files or high concurrency needed

### Availability
- **Single task**: No redundancy in dev mode
- **Fargate Spot**: May experience interruptions (2-min notice)
- **Use standard Fargate** for production reliability

## 📊 Monitoring & Troubleshooting

### Check Service Health
```bash
# Quick status
./test-dev-service.sh

# Detailed ECS status  
aws ecs describe-services \
  --cluster document-portal-cluster \
  --services document-portal-service \
  --region us-east-1
```

### View Logs
```bash
# CloudWatch logs
aws logs describe-log-streams \
  --log-group-name /ecs/document-portal \
  --region us-east-1

# Get recent logs
aws logs get-log-events \
  --log-group-name /ecs/document-portal \
  --log-stream-name <stream-name> \
  --region us-east-1
```

### Common Issues

#### Service Not Starting
1. Check task definition: Resource limits too low
2. Check secrets: API keys configured correctly
3. Check logs: Application startup errors

#### High Costs
1. Use `./deploy-dev-mode.sh` Option 4 to shutdown
2. Enable Fargate Spot with Option 3
3. Monitor with AWS Cost Explorer

#### Performance Issues
1. Upgrade resources: Use standard mode (Option 6)
2. Check CloudWatch metrics
3. Consider scaling up CPU/memory

## 🎯 Next Steps

### For Production Deployment
1. **Set up Load Balancer**: Application Load Balancer
2. **Enable Auto Scaling**: Scale based on demand
3. **Private Networking**: VPC with private subnets
4. **Monitoring**: CloudWatch alarms and dashboards
5. **CI/CD Pipeline**: Automated deployments

### Development Best Practices
1. **Cost Awareness**: Shutdown when not needed
2. **Testing**: Use test script before major changes
3. **Resource Monitoring**: Track performance vs cost
4. **Security**: Regular secret rotation

---

## 💡 Quick Reference

```bash
# Most common commands
./deploy-dev-mode.sh    # Main deployment script
./test-dev-service.sh   # Test current deployment

# Current service
curl http://3.234.251.124:8080/health

# Stop costs when done
./deploy-dev-mode.sh # → Option 4
```

**Happy Development! 🚀**
