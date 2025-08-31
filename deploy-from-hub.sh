#!/bin/bash

# Document RAG Portal - Docker Hub Deployment Script
# This script searches, downloads, and deploys the RAG application from Docker Hub

set -e  # Exit on any error

# Configuration
DOCKER_HUB_REPO="dockermaganhalli/document-rag-portal"
COMPOSE_FILE="docker-compose.hub.yml"
ENV_FILE=".env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check if Docker is installed and running
check_docker() {
    print_step "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed and running"
}

# Function to search for the application on Docker Hub
search_docker_hub() {
    print_step "Searching for RAG application on Docker Hub..."
    
    echo "Searching for: $DOCKER_HUB_REPO"
    docker search $DOCKER_HUB_REPO | head -5
    
    if [ $? -eq 0 ]; then
        print_status "Found RAG application on Docker Hub"
    else
        print_error "Could not find the application on Docker Hub"
        exit 1
    fi
}

# Function to download all required images
download_images() {
    print_step "Downloading RAG application images from Docker Hub..."
    
    local images=(
        "$DOCKER_HUB_REPO:latest"
        "$DOCKER_HUB_REPO:api-latest"
        "$DOCKER_HUB_REPO:frontend-latest"
        "$DOCKER_HUB_REPO:redis-latest"
    )
    
    for image in "${images[@]}"; do
        print_status "Pulling $image..."
        docker pull "$image"
    done
    
    # Also pull standard PostgreSQL image
    print_status "Pulling postgres:16-alpine..."
    docker pull postgres:16-alpine
    
    print_status "All images downloaded successfully"
}

# Function to create docker-compose file if not exists
create_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_step "Creating docker-compose.hub.yml file..."
        
        cat > "$COMPOSE_FILE" << 'EOF'
# Docker Compose for Production Deployment from Docker Hub
version: '3.8'

services:
  # Backend API Service - From Docker Hub
  document-portal-api:
    image: dockermaganhalli/document-rag-portal:api-latest
    container_name: document-portal-api
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./faiss_index:/app/faiss_index
      - ./logs:/app/logs
      - ./cache:/app/cache
    environment:
      - PYTHONPATH=/app
      - ENVIRONMENT=production
      - GOOGLE_API_KEY=${GOOGLE_API_KEY:-}
      - GROQ_API_KEY=${GROQ_API_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - CACHE_TYPE=memory
      - CACHE_SIZE_LIMIT=1000
      - CACHE_TTL=3600
      - MAX_FILE_SIZE=52428800
      - MAX_TEXT_LENGTH=500000
      - REQUEST_TIMEOUT=120
      - CORS_ORIGINS=http://localhost:3002,http://localhost:80
      - API_RATE_LIMIT=100
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - document-portal-network
    depends_on:
      - redis
      - postgres
    
  # Frontend Service - From Docker Hub
  document-portal-frontend:
    image: dockermaganhalli/document-rag-portal:frontend-latest
    container_name: document-portal-frontend
    ports:
      - "3002:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8080
      - REACT_APP_ENVIRONMENT=production
    restart: unless-stopped
    networks:
      - document-portal-network
    depends_on:
      - document-portal-api

  # Optimized Redis Cache Service - From Docker Hub
  redis:
    image: dockermaganhalli/document-rag-portal:redis-latest
    container_name: document-portal-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - document-portal-network
    deploy:
      resources:
        limits:
          memory: 300M
          cpus: '0.5'

  # PostgreSQL Database - Standard Image for Compatibility
  postgres:
    image: postgres:16-alpine
    container_name: document-portal-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=document_portal
      - POSTGRES_USER=portal_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-portal_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    command: >
      postgres
      -c shared_buffers=64MB
      -c effective_cache_size=192MB
      -c work_mem=4MB
      -c max_connections=50
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U portal_user -d document_portal"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - document-portal-network
    deploy:
      resources:
        limits:
          memory: 300M
          cpus: '1.0'

volumes:
  redis_data:
    driver: local
  postgres_data:
    driver: local

networks:
  document-portal-network:
    driver: bridge
EOF
        
        print_status "Docker Compose file created: $COMPOSE_FILE"
    else
        print_status "Using existing $COMPOSE_FILE"
    fi
}

# Function to create environment file
create_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_step "Creating environment file..."
        
        cat > "$ENV_FILE" << 'EOF'
# Document RAG Portal Environment Configuration
# Please update with your actual API keys

# Required API Keys
GOOGLE_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
POSTGRES_PASSWORD=secure_database_password_123

# Frontend Authentication
REACT_APP_ADMIN_PASSWORD=RagPortal092025
REACT_APP_GUEST_PASSWORD=guestRagPortal092025

# Application Settings
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3002
API_RATE_LIMIT=100
MAX_FILE_SIZE=52428800
EOF
        
        print_warning "Created $ENV_FILE - Please update with your actual API keys!"
        print_warning "Edit $ENV_FILE and add your API keys before deployment"
        
        # Open the file in default editor if available
        if command -v code &> /dev/null; then
            print_status "Opening $ENV_FILE in VS Code for editing..."
            code "$ENV_FILE"
        elif command -v nano &> /dev/null; then
            print_status "You can edit the file with: nano $ENV_FILE"
        fi
    else
        print_status "Using existing $ENV_FILE"
    fi
}

# Function to clean up existing containers
cleanup_existing() {
    print_step "Cleaning up existing containers..."
    
    # Stop and remove containers if they exist
    docker-compose -f "$COMPOSE_FILE" down 2>/dev/null || true
    
    # Remove any existing document-portal containers
    docker ps -a --filter "name=document-portal" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true
    
    print_status "Cleanup completed"
}

# Function to deploy the application
deploy_application() {
    print_step "Deploying RAG application..."
    
    # Create necessary directories
    mkdir -p data faiss_index logs cache
    
    # Deploy the application
    docker-compose -f "$COMPOSE_FILE" up -d
    
    if [ $? -eq 0 ]; then
        print_status "Application deployed successfully!"
    else
        print_error "Deployment failed"
        exit 1
    fi
}

# Function to wait for services and check health
check_deployment() {
    print_step "Waiting for services to start..."
    
    # Wait for services to start
    sleep 30
    
    print_step "Checking service health..."
    
    # Check container status
    echo "Container Status:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=document-portal"
    
    echo ""
    
    # Test API health
    if curl -f http://localhost:8080/health &>/dev/null; then
        print_status "✅ API Backend is healthy"
    else
        print_warning "⚠️  API Backend health check failed"
    fi
    
    # Test Frontend
    if curl -I http://localhost:3002 &>/dev/null; then
        print_status "✅ Frontend is accessible"
    else
        print_warning "⚠️  Frontend accessibility check failed"
    fi
    
    # Test Redis
    if docker exec document-portal-redis redis-cli ping &>/dev/null; then
        print_status "✅ Redis Cache is running"
    else
        print_warning "⚠️  Redis Cache check failed"
    fi
}

# Function to display access information
show_access_info() {
    print_step "Deployment Complete!"
    
    echo ""
    echo "🌐 Access your Document RAG Portal:"
    echo "   Frontend UI:      http://localhost:3002"
    echo "   API Backend:      http://localhost:8080"
    echo "   API Documentation: http://localhost:8080/docs"
    echo "   Health Check:     http://localhost:8080/health"
    echo ""
    echo "📊 Manage your deployment:"
    echo "   View logs:        docker-compose -f $COMPOSE_FILE logs -f"
    echo "   Stop services:    docker-compose -f $COMPOSE_FILE down"
    echo "   Restart services: docker-compose -f $COMPOSE_FILE restart"
    echo "   Update images:    docker-compose -f $COMPOSE_FILE pull && docker-compose -f $COMPOSE_FILE up -d"
    echo ""
    echo "⚙️  Configuration:"
    echo "   Environment file: $ENV_FILE"
    echo "   Compose file:     $COMPOSE_FILE"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   Check status:     docker ps"
    echo "   View API logs:    docker logs document-portal-api"
    echo "   View all logs:    docker-compose -f $COMPOSE_FILE logs"
}

# Main execution
main() {
    echo "🐳 Document RAG Portal - Docker Hub Deployment"
    echo "=============================================="
    echo ""
    
    check_docker
    search_docker_hub
    download_images
    create_compose_file
    create_env_file
    
    # Ask for confirmation before deployment
    echo ""
    read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup_existing
        deploy_application
        check_deployment
        show_access_info
    else
        print_status "Deployment cancelled. Run this script again when ready."
        echo "To deploy manually: docker-compose -f $COMPOSE_FILE up -d"
    fi
}

# Run main function
main "$@"
