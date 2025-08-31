#!/bin/bash

# Image Size Optimization Script for Document RAG Portal
echo "🔄 Starting image size optimization..."

# Stop current containers
echo "📦 Stopping current containers..."
docker-compose down

# Remove old images to free space
echo "🗑️  Removing old images..."
docker rmi document-portal-redis:optimized 2>/dev/null || true
docker rmi document-portal-postgres:optimized 2>/dev/null || true

# Build optimized images
echo "🏗️  Building optimized Redis image..."
docker build -f Dockerfile.redis -t document-portal-redis:optimized .

echo "🏗️  Building optimized PostgreSQL image..."
docker build -f Dockerfile.postgres -t document-portal-postgres:optimized .

# Compare image sizes
echo "📊 Image Size Comparison:"
echo "==========================================="
echo "BEFORE OPTIMIZATION:"
docker images | grep -E "(postgres.*15-alpine|redis.*7-alpine)" | awk '{print $1":"$2" - "$7$8}'

echo ""
echo "AFTER OPTIMIZATION:"
docker images | grep -E "(document-portal-redis:optimized|document-portal-postgres:optimized)" | awk '{print $1":"$2" - "$7$8}'

echo ""
echo "🚀 Starting optimized containers..."
docker-compose up -d

echo ""
echo "⏱️  Waiting for services to be healthy..."
sleep 30

echo "🏥 Health check status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Size}}"

echo ""
echo "✅ Optimization complete!"
echo "💡 Tips:"
echo "   - Redis memory limit: 256MB (configurable)"
echo "   - PostgreSQL optimized for small datasets"
echo "   - Both containers use resource limits"
echo "   - Images use Alpine Linux for minimal size"
