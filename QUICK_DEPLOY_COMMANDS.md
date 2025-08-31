# Document RAG Portal - Quick Deployment Commands

## 🚀 One-Line Deployment (Automated)

```bash
curl -sSL https://raw.githubusercontent.com/maganahalli-aiml/DOCUMENT-RAG-PORTAL/ragEnhancement/deploy-from-hub.sh | bash
```

## 📋 Manual Step-by-Step Commands

### Step 1: Search and Verify on Docker Hub
```bash
# Search for the application
docker search dockermaganhalli/document-rag-portal

# Verify the repository exists
curl -s https://hub.docker.com/v2/repositories/dockermaganhalli/document-rag-portal/ | grep name
```

### Step 2: Download All Required Images
```bash
# Download main application components
docker pull dockermaganhalli/document-rag-portal:latest
docker pull dockermaganhalli/document-rag-portal:api-latest
docker pull dockermaganhalli/document-rag-portal:frontend-latest
docker pull dockermaganhalli/document-rag-portal:redis-latest

# Download database (standard image for compatibility)
docker pull postgres:16-alpine

# Verify images are downloaded
docker images | grep -E "(dockermaganhalli|postgres)"
```

### Step 3: Create Environment Configuration
```bash
# Create environment file
cat > .env << 'EOF'
# Document RAG Portal Environment Configuration
GOOGLE_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
POSTGRES_PASSWORD=secure_database_password_123
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3002
API_RATE_LIMIT=100
MAX_FILE_SIZE=52428800
EOF

# Edit with your actual API keys
nano .env  # or code .env or vim .env
```

### Step 4: Download Docker Compose Configuration
```bash
# Download the production docker-compose file
curl -O https://raw.githubusercontent.com/maganahalli-aiml/DOCUMENT-RAG-PORTAL/ragEnhancement/docker-compose.hub.yml

# Or create it manually (see the compose file content below)
```

### Step 5: Deploy the Application
```bash
# Create necessary directories
mkdir -p data faiss_index logs cache

# Stop any existing containers
docker-compose -f docker-compose.hub.yml down 2>/dev/null || true

# Deploy the application
docker-compose -f docker-compose.hub.yml up -d

# Check deployment status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Step 6: Verify Deployment
```bash
# Wait for services to start
sleep 30

# Check API health
curl http://localhost:8080/health

# Check frontend accessibility
curl -I http://localhost:3002

# View logs if needed
docker-compose -f docker-compose.hub.yml logs -f
```

## 🔧 Management Commands

### View Application Status
```bash
docker ps --filter "name=document-portal"
```

### Check Logs
```bash
# All services
docker-compose -f docker-compose.hub.yml logs -f

# Specific service
docker logs document-portal-api
docker logs document-portal-frontend
docker logs document-portal-redis
docker logs document-portal-postgres
```

### Update Application
```bash
# Pull latest images
docker-compose -f docker-compose.hub.yml pull

# Restart with latest images
docker-compose -f docker-compose.hub.yml up -d
```

### Stop/Start Services
```bash
# Stop all services
docker-compose -f docker-compose.hub.yml down

# Start all services
docker-compose -f docker-compose.hub.yml up -d

# Restart specific service
docker-compose -f docker-compose.hub.yml restart document-portal-api
```

### Clean Up
```bash
# Remove all containers and volumes
docker-compose -f docker-compose.hub.yml down -v

# Remove downloaded images
docker rmi dockermaganhalli/document-rag-portal:latest
docker rmi dockermaganhalli/document-rag-portal:api-latest
docker rmi dockermaganhalli/document-rag-portal:frontend-latest
docker rmi dockermaganhalli/document-rag-portal:redis-latest
```

## 🌐 Access URLs

Once deployed, access your application at:

- **Frontend UI**: http://localhost:3002
- **API Backend**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## 📊 Resource Requirements

- **CPU**: 3-4 cores recommended
- **Memory**: 2-3 GB RAM
- **Storage**: 8 GB free space
- **Network**: Internet connection for initial download

## 🔐 Security Notes

1. Update the `.env` file with your actual API keys
2. Change the default PostgreSQL password
3. Consider using a reverse proxy (nginx/traefik) for production
4. Ensure Docker daemon is secure in production environments

## 🆘 Troubleshooting

### Common Issues:

1. **Port conflicts**: Change ports in docker-compose.hub.yml if needed
2. **API keys missing**: Ensure .env file has valid API keys
3. **Insufficient resources**: Check Docker Desktop resource allocation
4. **Permission issues**: Ensure Docker has proper permissions

### Getting Help:

```bash
# Check container logs
docker logs document-portal-api --tail 50

# Check resource usage
docker stats

# Test individual components
docker exec document-portal-redis redis-cli ping
docker exec document-portal-postgres pg_isready -U portal_user
```
