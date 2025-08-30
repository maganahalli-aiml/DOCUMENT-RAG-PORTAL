# Document RAG Portal - Docker Deployment Guide

This document provides comprehensive instructions for deploying the Document RAG Portal using Docker Compose in a production environment.

## 🏗️ Architecture Overview

The application consists of the following services:

- **document-portal-api**: FastAPI backend with document processing and RAG capabilities
- **document-portal-frontend**: React frontend with authentication and document management
- **redis**: In-memory cache for LangChain and application data
- **postgres**: Primary database for document metadata and user sessions
- **nginx**: Reverse proxy and load balancer
- **prometheus**: Metrics collection (optional)
- **grafana**: Monitoring dashboard (optional)

## 📋 Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- At least 4GB RAM available
- 10GB free disk space

## 🚀 Quick Start

1. **Clone and navigate to the project directory**
   ```bash
   cd /path/to/DOCUMENT-RAG-PORTAL
   ```

2. **Configure environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   nano .env
   ```

3. **Deploy the application**
   ```bash
   ./deploy.sh deploy
   ```

4. **Check health status**
   ```bash
   ./health-check.sh
   ```

5. **Access the application**
   - Frontend: http://localhost
   - API Documentation: http://localhost/api/docs
   - Admin Login: admin / RagPortal092025
   - Guest Login: guest / guestRagPortal092025

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Security
SECRET_KEY=your-secret-key-here-change-in-production

# API Keys (required)
GROQ_API_KEY=your-groq-api-key-here
GOOGLE_API_KEY=your-google-api-key-here

# Database
DATABASE_URL=postgresql://portal_user:portal_password@postgres:5432/document_portal

# Cache
REDIS_URL=redis://redis:6379/0
CACHE_TTL_SECONDS=3600

# File Upload
MAX_FILE_SIZE_MB=50
UPLOAD_TIMEOUT_SECONDS=300
```

### Service Configuration

Individual service configurations:

- **API**: `config/config.yaml`
- **Frontend**: `frontend/document-rag-portal/nginx.conf`
- **Reverse Proxy**: `nginx/nginx.conf`
- **Redis**: `redis/redis.conf`
- **Database**: `postgres/init.sql`
- **Monitoring**: `monitoring/prometheus.yml`

## 📝 Deployment Commands

### Full Deployment
```bash
./deploy.sh deploy                    # Deploy all services
./deploy.sh deploy --with-monitoring  # Deploy with monitoring stack
```

### Service Management
```bash
./deploy.sh start     # Start services (without rebuilding)
./deploy.sh stop      # Stop all services
./deploy.sh restart   # Restart all services
./deploy.sh status    # Show service status
```

### Monitoring and Debugging
```bash
./deploy.sh logs                     # Show all logs
./deploy.sh logs document-portal-api # Show specific service logs
./health-check.sh                    # Run health checks
```

### Maintenance
```bash
./deploy.sh build    # Rebuild Docker images
./deploy.sh cleanup  # Stop services and clean up resources
```

## 🔍 Monitoring

### Health Checks

The application includes comprehensive health monitoring:

- **Application Health**: `http://localhost/api/health`
- **Service Status**: `./health-check.sh`
- **Container Status**: `docker-compose ps`

### Metrics (Optional)

When deployed with monitoring:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

Default Grafana credentials:
- Username: admin
- Password: admin (change on first login)

## 🚨 Troubleshooting

### Common Issues

**Services not starting:**
```bash
# Check Docker resources
docker system df
docker system prune -f

# Check logs
./deploy.sh logs
```

**Database connection errors:**
```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U portal_user

# Reset database
docker-compose down -v
./deploy.sh deploy
```

**Cache issues:**
```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

**File upload failures:**
```bash
# Check disk space
df -h

# Check file permissions
ls -la data/uploads/
```

### Performance Optimization

**For high-load environments:**

1. **Increase API workers** in `.env`:
   ```bash
   API_WORKERS=8
   ```

2. **Optimize Redis memory** in `redis/redis.conf`:
   ```
   maxmemory 512mb
   ```

3. **Scale services** in `docker-compose.yml`:
   ```yaml
   document-portal-api:
     deploy:
       replicas: 3
   ```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set strong database passwords
- [ ] Configure Redis authentication
- [ ] Enable HTTPS with SSL certificates
- [ ] Restrict CORS origins
- [ ] Set up firewall rules
- [ ] Regular security updates

### SSL/TLS Configuration

To enable HTTPS, update `nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    # ... rest of configuration
}
```

## 📊 Scaling

### Horizontal Scaling

Scale individual services:

```bash
docker-compose up -d --scale document-portal-api=3
```

### Load Balancing

NGINX automatically load balances between multiple API instances.

### Database Scaling

For high-load scenarios:
- Enable PostgreSQL read replicas
- Use connection pooling
- Consider database sharding

## 🔄 Backup and Recovery

### Database Backup
```bash
docker-compose exec postgres pg_dump -U portal_user document_portal > backup.sql
```

### Volume Backup
```bash
docker run --rm -v document-rag-portal_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Recovery
```bash
docker-compose exec postgres psql -U portal_user document_portal < backup.sql
```

## 🧪 Testing

### Integration Testing
```bash
# Test API endpoints
curl http://localhost/api/health
curl http://localhost/api/docs

# Test file upload
curl -X POST -F "file=@test_doc.pdf" http://localhost/api/upload

# Test authentication
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"RagPortal092025"}' \
  http://localhost/api/auth/login
```

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API performance
ab -n 1000 -c 10 http://localhost/api/health
```

## 📈 Monitoring Alerts

The monitoring stack includes alerts for:

- High API response times (>500ms)
- High error rates (>10%)
- Memory usage (>500MB)
- Low cache hit rates (<70%)
- Service availability

## 🔄 Updates and Maintenance

### Application Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./deploy.sh deploy
```

### System Maintenance
```bash
# Clean up Docker resources
docker system prune -f

# Update base images
docker-compose pull

# Restart with latest images
./deploy.sh restart
```

## 📞 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review service logs: `./deploy.sh logs`
3. Run health checks: `./health-check.sh`
4. Check system resources: `docker system df`

## 📄 License

This deployment configuration is part of the Document RAG Portal project.
