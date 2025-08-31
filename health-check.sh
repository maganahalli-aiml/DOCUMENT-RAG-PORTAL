#!/bin/bash

# Health check script for Document RAG Portal services

set -e

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "$1"
}

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local service_name=$2
    local timeout=${3:-10}
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        print_status "${GREEN}✓${NC} $service_name is healthy"
        return 0
    else
        print_status "${RED}✗${NC} $service_name is not responding"
        return 1
    fi
}

# Function to check TCP port
check_tcp() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-5}
    
    if timeout $timeout bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
        print_status "${GREEN}✓${NC} $service_name is reachable"
        return 0
    else
        print_status "${RED}✗${NC} $service_name is not reachable"
        return 1
    fi
}

echo "Document RAG Portal - Health Check"
echo "=================================="
echo ""

# Check if Docker Compose is running
if ! docker-compose ps | grep -q "Up"; then
    print_status "${RED}✗${NC} No Docker Compose services are running"
    echo ""
    echo "To start services, run:"
    echo "  ./deploy.sh deploy"
    exit 1
fi

echo "Checking service health..."
echo ""

# Initialize counters
healthy_services=0
total_services=0

# Check Frontend (through nginx proxy)
total_services=$((total_services + 1))
if check_http "http://localhost:3002" "Frontend (via nginx)"; then
    healthy_services=$((healthy_services + 1))
fi

# Check API directly
total_services=$((total_services + 1))
if check_http "http://localhost:8080/health" "API Health Endpoint"; then
    healthy_services=$((healthy_services + 1))
fi

# Check API docs
total_services=$((total_services + 1))
if check_http "http://localhost:8080/docs" "API Documentation"; then
    healthy_services=$((healthy_services + 1))
fi

# Check Redis
total_services=$((total_services + 1))
if docker-compose exec -T redis redis-cli ping | grep -q "PONG" 2>/dev/null; then
    print_status "${GREEN}✓${NC} Redis is responding"
    healthy_services=$((healthy_services + 1))
else
    print_status "${RED}✗${NC} Redis is not responding"
fi

# Check PostgreSQL
total_services=$((total_services + 1))
if docker-compose exec -T postgres pg_isready -U portal_user 2>/dev/null | grep -q "accepting connections"; then
    print_status "${GREEN}✓${NC} PostgreSQL is accepting connections"
    healthy_services=$((healthy_services + 1))
else
    print_status "${RED}✗${NC} PostgreSQL is not accepting connections"
fi

# Check monitoring services if they exist
if docker-compose ps | grep -q prometheus; then
    total_services=$((total_services + 1))
    if check_http "http://localhost:9090/-/healthy" "Prometheus"; then
        healthy_services=$((healthy_services + 1))
    fi
fi

if docker-compose ps | grep -q grafana; then
    total_services=$((total_services + 1))
    if check_http "http://localhost:3001/api/health" "Grafana"; then
        healthy_services=$((healthy_services + 1))
    fi
fi

echo ""
echo "Health Check Summary"
echo "===================="

if [ $healthy_services -eq $total_services ]; then
    print_status "${GREEN}All services are healthy ($healthy_services/$total_services)${NC}"
    echo ""
    echo "Application URLs:"
    echo "  Frontend: http://localhost:3002"
    echo "  API Docs: http://localhost:8080/docs"
    echo "  API Health: http://localhost:8080/health"
    
    if docker-compose ps | grep -q prometheus; then
        echo "  Prometheus: http://localhost:9090"
    fi
    
    if docker-compose ps | grep -q grafana; then
        echo "  Grafana: http://localhost:3001"
    fi
    
    exit 0
else
    print_status "${RED}Some services are unhealthy ($healthy_services/$total_services)${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check service logs: ./deploy.sh logs"
    echo "  2. Check specific service: ./deploy.sh logs [service-name]"
    echo "  3. Restart services: ./deploy.sh restart"
    echo "  4. Check Docker resources: docker system df"
    
    exit 1
fi
