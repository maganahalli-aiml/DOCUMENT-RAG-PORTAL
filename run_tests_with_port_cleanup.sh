#!/bin/bash

# Comprehensive Test Script with Port Management
# This script kills processes on specified ports before running tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

# Function to kill processes on a specific port
kill_port_processes() {
    local port=$1
    local service_name=${2:-"process"}
    
    print_info "Checking for processes on port $port..."
    
    # Find processes using the specified port
    local pids=$(lsof -t -i:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        print_warning "Found $service_name running on port $port. Terminating..."
        
        # Try graceful termination first
        echo "$pids" | xargs -r kill -TERM 2>/dev/null || true
        
        # Wait for graceful shutdown
        sleep 3
        
        # Check if processes are still running
        local remaining_pids=$(lsof -t -i:$port 2>/dev/null || true)
        
        if [ -n "$remaining_pids" ]; then
            print_warning "Force killing remaining processes on port $port..."
            echo "$remaining_pids" | xargs -r kill -KILL 2>/dev/null || true
            sleep 1
        fi
        
        # Final check
        local final_pids=$(lsof -t -i:$port 2>/dev/null || true)
        if [ -z "$final_pids" ]; then
            print_status "Port $port is now available"
        else
            print_error "Could not clear port $port completely"
        fi
    else
        print_status "Port $port is already available"
    fi
}

# Function to run tests with timeout
run_test_with_timeout() {
    local test_command="$1"
    local timeout_seconds=${2:-30}
    local test_name=${3:-"test"}
    
    print_info "Running $test_name with ${timeout_seconds}s timeout..."
    
    # Run the command in background
    timeout $timeout_seconds bash -c "$test_command" &
    local test_pid=$!
    
    # Wait for the process to complete
    if wait $test_pid; then
        print_status "$test_name completed successfully"
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            print_error "$test_name timed out after ${timeout_seconds} seconds"
        else
            print_error "$test_name failed with exit code $exit_code"
        fi
        return $exit_code
    fi
}

# Main test execution
echo "🧪 Comprehensive Test Runner with Port Management"
echo "================================================="

# Kill processes on common development ports
kill_port_processes 8080 "Development API server"
kill_port_processes 8081 "Test API server" 
kill_port_processes 3000 "Frontend development server"
kill_port_processes 3001 "Frontend production server"

echo ""
print_info "Running pre-commit style validation..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    print_error "Python is not installed or not in PATH"
    exit 1
fi

# Install testing dependencies if needed
if ! python -c "import pytest" &> /dev/null; then
    print_info "Installing required testing packages..."
    pip install pytest pytest-cov flake8 black isort
fi

# Run code formatting check
print_info "Checking code formatting..."
if command -v black &> /dev/null; then
    if black --check . --quiet; then
        print_status "Code formatting is correct"
    else
        print_warning "Code formatting issues found. Auto-fixing..."
        black .
        print_status "Code formatting fixed"
    fi
fi

# Run import sorting check
print_info "Checking import sorting..."
if command -v isort &> /dev/null; then
    if isort --check-only . --quiet; then
        print_status "Import sorting is correct"
    else
        print_warning "Import sorting issues found. Auto-fixing..."
        isort .
        print_status "Import sorting fixed"
    fi
fi

# Run linting
print_info "Running code linting..."
if command -v flake8 &> /dev/null; then
    if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --quiet; then
        print_status "No critical linting issues found"
    else
        print_error "Critical linting issues found. Please fix before proceeding."
        exit 1
    fi
fi

# Run unit tests
print_info "Running unit tests..."
if [ -f "tests/test_unit_cases.py" ]; then
    if run_test_with_timeout "python -m pytest tests/test_unit_cases.py -v --tb=short" 60 "unit tests"; then
        print_status "Unit tests passed"
    else
        print_error "Unit tests failed"
        exit 1
    fi
else
    print_warning "No unit test file found (tests/test_unit_cases.py)"
fi

# Run API tests with port management
if [ -f "test_api.py" ]; then
    print_info "Running API tests..."
    
    # The test_api.py now handles port cleanup internally
    if run_test_with_timeout "python test_api.py" 30 "API tests"; then
        print_status "API tests passed"
    else
        print_error "API tests failed"
        exit 1
    fi
else
    print_warning "No API test file found (test_api.py)"
fi

# Clean up any remaining test processes
print_info "Cleaning up test processes..."
kill_port_processes 8081 "Test API server"

print_status "All tests completed successfully!"
echo ""
echo "🎉 Test suite passed with port management!"
echo "   Development environment is clean and ready."
