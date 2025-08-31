# 🚀 Document RAG Portal - Deployment from Docker Hub

## Quick Deploy (One Command)

```bash
# Download and run the automated deployment script
curl -sSL https://raw.githubusercontent.com/maganahalli-aiml/DOCUMENT-RAG-PORTAL/ragEnhancement/deploy-from-hub.sh | bash
```

## Manual Deployment (3 Steps)

### 1. Search & Download
```bash
# Search on Docker Hub
docker search dockermaganhalli/document-rag-portal

# Download all images
docker pull dockermaganhalli/document-rag-portal:api-latest
docker pull dockermaganhalli/document-rag-portal:frontend-latest  
docker pull dockermaganhalli/document-rag-portal:redis-latest
docker pull postgres:16-alpine
```

### 2. Setup Configuration
```bash
# Download docker-compose file
curl -O https://raw.githubusercontent.com/maganahalli-aiml/DOCUMENT-RAG-PORTAL/ragEnhancement/docker-compose.hub.yml

# Create environment file (add your API keys)
cat > .env << 'EOF'
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
POSTGRES_PASSWORD=your_secure_password
EOF
```

### 3. Deploy
```bash
# Create directories and deploy
mkdir -p data faiss_index logs cache
docker-compose -f docker-compose.hub.yml up -d

# Check status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## Access Your Application

- **Frontend**: http://localhost:3002
- **API**: http://localhost:8080  
- **Documentation**: http://localhost:8080/docs

## What Gets Deployed

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| API Backend | dockermaganhalli/document-rag-portal:api-latest | 8080 | RAG Processing |
| Frontend | dockermaganhalli/document-rag-portal:frontend-latest | 3002 | Web UI |
| Redis Cache | dockermaganhalli/document-rag-portal:redis-latest | 6379 | Caching |
| PostgreSQL | postgres:16-alpine | 5432 | Database |

## Management Commands

```bash
# View logs
docker-compose -f docker-compose.hub.yml logs -f

# Stop services  
docker-compose -f docker-compose.hub.yml down

# Update to latest
docker-compose -f docker-compose.hub.yml pull
docker-compose -f docker-compose.hub.yml up -d
```

---

**Total Deployment Time**: ~5 minutes  
**Resource Requirements**: 3GB RAM, 8GB Storage  
**Docker Hub Repository**: https://hub.docker.com/r/dockermaganhalli/document-rag-portal
