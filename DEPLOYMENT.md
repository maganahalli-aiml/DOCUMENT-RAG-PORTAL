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

1. **AWS ECS/Fargate**
2. **Google Cloud Run**
3. **Azure Container Instances**
4. **Kubernetes clusters**
5. **Digital Ocean App Platform**

### Container Registry:
```bash
# Tag and push to registry
docker tag document-portal-system:optimized your-registry/document-portal:latest
docker push your-registry/document-portal:latest
```

This optimized deployment setup provides a production-ready foundation with security, monitoring, and scalability considerations built-in!
