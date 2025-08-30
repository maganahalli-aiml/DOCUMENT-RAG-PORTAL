#!/bin/bash

# Document RAG Portal - Production Deployment Script
# This script helps deploy the application using Docker Compose

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required files exist
check_requirements() {
    print_status "Checking deployment requirements..."
    
    local missing_files=()
    
    # Check for required files
    if [ ! -f "docker-compose.yml" ]; then
        missing_files+=("docker-compose.yml")
    fi
    
    if [ ! -f "Dockerfile" ]; then
        missing_files+=("Dockerfile")
    fi
    
    if [ ! -f "frontend/document-rag-portal/Dockerfile.frontend" ]; then
        missing_files+=("frontend/document-rag-portal/Dockerfile.frontend")
    fi
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.template" ]; then
            print_warning ".env file not found. Please copy .env.template to .env and configure it."
            echo "  cp .env.template .env"
            echo "  # Then edit .env with your configuration"
        else
            missing_files+=(".env or .env.template")
        fi
    fi
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        print_error "Missing required files:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
    
    print_success "All required files found"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    local directories=(
        "logs"
        "data/uploads"
        "data/faiss_index"
        "data/postgres"
        "data/redis"
        "monitoring/data"
        "nginx/logs"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
    
    # Set appropriate permissions
    chmod 755 logs data
    chmod -R 755 data/
    
    print_success "Directories created and configured"
}

# Function to build images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    docker build -t document-portal-api:latest .
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -f frontend/document-rag-portal/Dockerfile.frontend -t document-portal-frontend:latest frontend/document-rag-portal/
    
    print_success "Docker images built successfully"
}

# Function to start services
start_services() {
    print_status "Starting Docker Compose services..."
    
    # Start infrastructure services first
    print_status "Starting infrastructure services (Redis, PostgreSQL)..."
    docker-compose up -d redis postgres
    
    # Wait a bit for services to initialize
    sleep 10
    
    # Start application services
    print_status "Starting application services..."
    docker-compose up -d document-portal-api document-portal-frontend
    
    # Start reverse proxy
    print_status "Starting reverse proxy..."
    docker-compose up -d nginx
    
    # Start monitoring (optional)
    if [ "$1" = "--with-monitoring" ]; then
        print_status "Starting monitoring services..."
        docker-compose up -d prometheus grafana
    fi
    
    print_success "All services started"
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_status "Application URLs:"
    echo "  Frontend: http://localhost"
    echo "  API Documentation: http://localhost/api/docs"
    echo "  Health Check: http://localhost/api/health"
    
    if docker-compose ps | grep -q prometheus; then
        echo "  Prometheus: http://localhost:9090"
        echo "  Grafana: http://localhost:3001"
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "All services stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show logs
show_logs() {
    if [ -n "$2" ]; then
        docker-compose logs -f "$2"
    else
        docker-compose logs -f
    fi
}

# Function to show help
show_help() {
    echo "Document RAG Portal - Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  deploy              Full deployment (build + start)"
    echo "  deploy --with-monitoring  Deploy with monitoring stack"
    echo "  start               Start services (without building)"
    echo "  stop                Stop all services"
    echo "  restart             Restart all services"
    echo "  status              Show service status"
    echo "  logs [service]      Show logs (optionally for specific service)"
    echo "  build               Build Docker images only"
    echo "  cleanup             Stop services and clean up resources"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy                    # Full deployment"
    echo "  $0 deploy --with-monitoring  # Deploy with Prometheus/Grafana"
    echo "  $0 logs document-portal-api  # Show API logs"
    echo "  $0 status                    # Check service status"
}

# Main script logic
case "$1" in
    "deploy")
        check_requirements
        create_directories
        build_images
        start_services "$2"
        show_status
        ;;
    "start")
        check_requirements
        create_directories
        start_services "$2"
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 5
        start_services "$2"
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$@"
        ;;
    "build")
        check_requirements
        build_images
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        print_error "No command specified"
        show_help
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
