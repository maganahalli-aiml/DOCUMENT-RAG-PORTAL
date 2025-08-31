#!/bin/bash

# Docker Hub Push Script for Document RAG Portal
# Repository: dockermaganhalli/document-rag-portal

DOCKER_HUB_REPO="dockermaganhalli/document-rag-portal"
VERSION="v2.0"  # Update this for new releases

echo "🐳 Pushing Document RAG Portal to Docker Hub"
echo "Repository: $DOCKER_HUB_REPO"
echo "Version: $VERSION"
echo "=================================="

# Function to tag and push image
tag_and_push() {
    local local_image=$1
    local tag_suffix=$2
    local hub_tag="$DOCKER_HUB_REPO:$tag_suffix"
    
    echo "📦 Processing: $local_image -> $hub_tag"
    
    # Tag the image
    docker tag "$local_image" "$hub_tag"
    
    # Push to Docker Hub
    echo "⬆️  Pushing $hub_tag..."
    docker push "$hub_tag"
    
    echo "✅ Successfully pushed $hub_tag"
    echo ""
}

# 1. API Backend (Main Application)
echo "1️⃣  Pushing API Backend..."
tag_and_push "document-portal-system:enhanced-rag-v1.0" "api-$VERSION"
tag_and_push "document-portal-system:enhanced-rag-v1.0" "api-latest"

# 2. Frontend Application
echo "2️⃣  Pushing Frontend..."
tag_and_push "document-portal-frontend:v1.0" "frontend-$VERSION"
tag_and_push "document-portal-frontend:v1.0" "frontend-latest"

# 3. Optimized Redis Cache
echo "3️⃣  Pushing Optimized Redis..."
tag_and_push "document-portal-redis:optimized" "redis-$VERSION"
tag_and_push "document-portal-redis:optimized" "redis-latest"

# 4. Optimized PostgreSQL Database
echo "4️⃣  Pushing Optimized PostgreSQL..."
tag_and_push "document-portal-postgres:optimized" "postgres-$VERSION"
tag_and_push "document-portal-postgres:optimized" "postgres-latest"

# 5. Create and push complete application bundle
echo "5️⃣  Creating complete application tag..."
tag_and_push "document-portal-system:enhanced-rag-v1.0" "$VERSION"
tag_and_push "document-portal-system:enhanced-rag-v1.0" "latest"

echo "🎉 All images pushed successfully!"
echo ""
echo "📋 Your Docker Hub images:"
echo "├── $DOCKER_HUB_REPO:latest (main application)"
echo "├── $DOCKER_HUB_REPO:$VERSION (main application)"
echo "├── $DOCKER_HUB_REPO:api-latest"
echo "├── $DOCKER_HUB_REPO:api-$VERSION"
echo "├── $DOCKER_HUB_REPO:frontend-latest"
echo "├── $DOCKER_HUB_REPO:frontend-$VERSION"
echo "├── $DOCKER_HUB_REPO:redis-latest"
echo "├── $DOCKER_HUB_REPO:redis-$VERSION"
echo "├── $DOCKER_HUB_REPO:postgres-latest"
echo "└── $DOCKER_HUB_REPO:postgres-$VERSION"
echo ""
echo "🔗 View on Docker Hub: https://hub.docker.com/r/dockermaganhalli/document-rag-portal"
echo ""
echo "📖 Usage Examples:"
echo "docker pull $DOCKER_HUB_REPO:latest"
echo "docker pull $DOCKER_HUB_REPO:api-latest"
echo "docker pull $DOCKER_HUB_REPO:frontend-latest"
echo "docker pull $DOCKER_HUB_REPO:redis-latest"
echo "docker pull $DOCKER_HUB_REPO:postgres-latest"
