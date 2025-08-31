# 🐳 Docker Hub Deployment Guide - Document RAG Portal

## ✅ **Successfully Published to Docker Hub!**

### 📦 **Your Public Docker Images**

| Component | Docker Hub Image | Size | Status |
|-----------|------------------|------|--------|
| **Main App** | `dockermaganhalli/document-rag-portal:latest` | 2.03GB | ✅ Published |
| **API Backend** | `dockermaganhalli/document-rag-portal:api-latest` | 2.03GB | ✅ Published |
| **Frontend** | `dockermaganhalli/document-rag-portal:frontend-latest` | 93.9MB | ✅ Published |
| **Redis Cache** | `dockermaganhalli/document-rag-portal:redis-latest` | 61.5MB | ✅ Published |
| **PostgreSQL DB** | `dockermaganhalli/document-rag-portal:postgres-latest` | 396MB | ✅ Published |

### 🔗 **Docker Hub Repository**
**URL**: https://hub.docker.com/r/dockermaganhalli/document-rag-portal

### 🚀 **One-Command Deployment**

Anyone can now deploy your complete RAG application with:

```bash
# Option 1: Use the hub-optimized docker-compose
curl -O https://raw.githubusercontent.com/maganahalli-aiml/DOCUMENT-RAG-PORTAL/ragEnhancement/docker-compose.hub.yml
docker-compose -f docker-compose.hub.yml up -d
```

```bash
# Option 2: Direct deployment (requires .env file)
git clone https://github.com/maganahalli-aiml/DOCUMENT-RAG-PORTAL.git
cd DOCUMENT-RAG-PORTAL
cp .env.template .env  # Edit with your API keys
docker-compose -f docker-compose.hub.yml up -d
```

### 💡 **Usage Examples for Others**

```bash
# Pull and run just the main application
docker pull dockermaganhalli/document-rag-portal:latest
docker run -p 8080:8080 dockermaganhalli/document-rag-portal:latest

# Pull individual components
docker pull dockermaganhalli/document-rag-portal:frontend-latest
docker pull dockermaganhalli/document-rag-portal:redis-latest
docker pull dockermaganhalli/document-rag-portal:postgres-latest
```

### 🏷️ **Available Tags**

- `latest` - Latest stable version (main app)
- `v2.0` - Version 2.0 with optimizations
- `api-latest` / `api-v2.0` - Backend API service
- `frontend-latest` / `frontend-v2.0` - React frontend
- `redis-latest` / `redis-v2.0` - Optimized Redis cache
- `postgres-latest` / `postgres-v2.0` - Optimized PostgreSQL

### 📊 **Image Statistics**

```
Total Images Pushed: 10
Registry: Docker Hub (Public)
Total Size: ~2.6GB (compressed)
Pull Command: docker pull dockermaganhalli/document-rag-portal:latest
```

### 🔄 **Update Instructions**

When you release new versions:

```bash
# Tag new version
./docker-hub-push.sh  # Update VERSION in script

# Or manually tag and push
docker tag document-portal-system:enhanced-rag-v1.0 dockermaganhalli/document-rag-portal:v2.1
docker push dockermaganhalli/document-rag-portal:v2.1
```

### 🌐 **Access After Deployment**

- **Frontend**: http://localhost:3002
- **API Backend**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

### 📞 **Sharing Your Application**

You can now share your Document RAG Portal with:

1. **Docker Hub Link**: https://hub.docker.com/r/dockermaganhalli/document-rag-portal
2. **Quick Deploy Command**: `docker-compose -f docker-compose.hub.yml up -d`
3. **GitHub Repository**: https://github.com/maganahalli-aiml/DOCUMENT-RAG-PORTAL

---

🎉 **Congratulations!** Your Document RAG Portal is now publicly available on Docker Hub for anyone to deploy and use!
