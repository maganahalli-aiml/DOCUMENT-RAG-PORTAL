#!/bin/bash

# Local Development Deployment Script
# Deploy the RAG Document Portal application locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="Document RAG Portal"
PYTHON_ENV=".venv/bin/python"
FASTAPI_PORT=8080
STREAMLIT_PORT=8501

echo -e "${BLUE}🚀 LOCAL DEPLOYMENT: ${APP_NAME}${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pids=$(lsof -ti :$port)
    if [ ! -z "$pids" ]; then
        print_warning "Killing existing processes on port $port"
        echo $pids | xargs kill -9
        sleep 2
    fi
}

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_error "Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Check if required packages are installed
print_status "Checking dependencies..."
if ! $PYTHON_ENV -c "import fastapi, streamlit" >/dev/null 2>&1; then
    print_warning "Installing missing dependencies..."
    $PYTHON_ENV -m pip install -r requirements.txt
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/uploaded_files
mkdir -p faiss_index
mkdir -p logs
mkdir -p evaluation_results

# Check environment variables
print_status "Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_warning "Creating default .env file..."
    cat > .env << EOF
# API Keys
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Database Configuration
FAISS_BASE=faiss_index
UPLOAD_BASE=data

# Application Settings
ENVIRONMENT=development
PYTHONPATH=.
EOF
    print_warning "Please update .env file with your API keys"
fi

# Check if API keys are set
if ! grep -q "GROQ_API_KEY=gsk_" .env 2>/dev/null && ! grep -q "GOOGLE_API_KEY=AIza" .env 2>/dev/null; then
    print_warning "API keys not configured in .env file"
    print_warning "Please update .env with your GROQ_API_KEY and/or GOOGLE_API_KEY"
fi

# Function to start FastAPI server
start_fastapi() {
    print_status "Starting FastAPI server on port $FASTAPI_PORT..."
    
    # Kill existing process if any
    kill_port $FASTAPI_PORT
    
    # Start FastAPI with uvicorn
    PYTHONPATH=. $PYTHON_ENV -m uvicorn api.main_simple:app \
        --host 0.0.0.0 \
        --port $FASTAPI_PORT \
        --reload \
        --log-level info &
    
    local fastapi_pid=$!
    echo $fastapi_pid > .fastapi_pid
    
    # Wait for server to start
    sleep 3
    
    if check_port $FASTAPI_PORT; then
        print_error "Failed to start FastAPI server"
        return 1
    else
        print_status "FastAPI server started successfully (PID: $fastapi_pid)"
        print_status "API documentation available at: http://localhost:$FASTAPI_PORT/docs"
        return 0
    fi
}

# Function to start Streamlit UI
start_streamlit() {
    # Check if streamlit_ui.py exists and has content
    if [ ! -s "streamlit_ui.py" ]; then
        print_warning "streamlit_ui.py is empty. Creating a basic Streamlit interface..."
        cat > streamlit_ui.py << 'EOF'
import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="Document RAG Portal",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Document RAG Portal")
st.markdown("---")

# Configuration
FASTAPI_URL = "http://localhost:8080"

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Upload & Chat", "Document Analysis", "System Status"])

if page == "Upload & Chat":
    st.header("Document Upload & Chat")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=['pdf', 'txt', 'docx', 'pptx', 'xlsx', 'md'],
        help="Upload documents in supported formats"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        # Display file details
        file_details = {
            "filename": uploaded_file.name,
            "file_size": len(uploaded_file.getvalue()),
            "file_type": uploaded_file.type
        }
        st.json(file_details)
        
        # Process document button
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{FASTAPI_URL}/analyze-document", files=files)
                    
                    if response.status_code == 200:
                        st.success("Document processed successfully!")
                        result = response.json()
                        st.json(result)
                    else:
                        st.error(f"Error processing document: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
                    st.info("Make sure the FastAPI server is running on port 8080")
    
    # Chat interface
    st.subheader("Chat with your documents")
    
    user_question = st.text_input("Ask a question about your documents:")
    
    if user_question and st.button("Send"):
        with st.spinner("Generating response..."):
            try:
                chat_data = {"message": user_question}
                response = requests.post(f"{FASTAPI_URL}/chat", json=chat_data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.write("**Response:**")
                    st.write(result.get("response", "No response received"))
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

elif page == "Document Analysis":
    st.header("Document Analysis")
    st.info("Upload documents to see detailed analysis and insights")
    
    # Recent uploads (mock data)
    st.subheader("Recent Documents")
    st.write("No documents uploaded yet. Use the Upload & Chat page to get started.")

elif page == "System Status":
    st.header("System Status")
    
    # API Health Check
    try:
        response = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ FastAPI Server: Online")
            health_data = response.json()
            st.json(health_data)
        else:
            st.error("❌ FastAPI Server: Error")
    except Exception as e:
        st.error("❌ FastAPI Server: Offline")
        st.error(f"Error: {str(e)}")
    
    # System Information
    st.subheader("System Information")
    system_info = {
        "FastAPI URL": FASTAPI_URL,
        "Streamlit Port": 8501,
        "Current Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Status": "Development Mode"
    }
    st.json(system_info)

# Footer
st.markdown("---")
st.markdown("**Document RAG Portal** - Enhanced with multi-format support and advanced evaluation")
EOF
    fi
    
    print_status "Starting Streamlit UI on port $STREAMLIT_PORT..."
    
    # Kill existing process if any
    kill_port $STREAMLIT_PORT
    
    # Start Streamlit
    PYTHONPATH=. $PYTHON_ENV -m streamlit run streamlit_ui.py \
        --server.port $STREAMLIT_PORT \
        --server.address 0.0.0.0 \
        --server.headless true \
        --browser.gatherUsageStats false &
    
    local streamlit_pid=$!
    echo $streamlit_pid > .streamlit_pid
    
    # Wait for server to start
    sleep 5
    
    if check_port $STREAMLIT_PORT; then
        print_error "Failed to start Streamlit server"
        return 1
    else
        print_status "Streamlit UI started successfully (PID: $streamlit_pid)"
        print_status "Web interface available at: http://localhost:$STREAMLIT_PORT"
        return 0
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop FastAPI
    if [ -f ".fastapi_pid" ]; then
        local fastapi_pid=$(cat .fastapi_pid)
        if kill $fastapi_pid 2>/dev/null; then
            print_status "FastAPI server stopped"
        fi
        rm -f .fastapi_pid
    fi
    
    # Stop Streamlit
    if [ -f ".streamlit_pid" ]; then
        local streamlit_pid=$(cat .streamlit_pid)
        if kill $streamlit_pid 2>/dev/null; then
            print_status "Streamlit server stopped"
        fi
        rm -f .streamlit_pid
    fi
    
    # Kill any remaining processes on our ports
    kill_port $FASTAPI_PORT
    kill_port $STREAMLIT_PORT
}

# Function to show status
show_status() {
    echo -e "${BLUE}Service Status:${NC}"
    echo "==================="
    
    if check_port $FASTAPI_PORT; then
        echo -e "FastAPI Server (port $FASTAPI_PORT): ${RED}❌ Offline${NC}"
    else
        echo -e "FastAPI Server (port $FASTAPI_PORT): ${GREEN}✅ Online${NC}"
        echo "  📋 API Documentation: http://localhost:$FASTAPI_PORT/docs"
    fi
    
    if check_port $STREAMLIT_PORT; then
        echo -e "Streamlit UI (port $STREAMLIT_PORT): ${RED}❌ Offline${NC}"
    else
        echo -e "Streamlit UI (port $STREAMLIT_PORT): ${GREEN}✅ Online${NC}"
        echo "  🌐 Web Interface: http://localhost:$STREAMLIT_PORT"
    fi
}

# Function to run tests
run_tests() {
    print_status "Running evaluation tests..."
    PYTHONPATH=. $PYTHON_ENV quick_rag_evaluation.py
}

# Main deployment logic
case "${1:-start}" in
    "start")
        print_status "Starting local deployment..."
        
        # Start FastAPI server
        if start_fastapi; then
            sleep 2
            
            # Start Streamlit UI
            if start_streamlit; then
                echo ""
                echo -e "${GREEN}🎉 Deployment successful!${NC}"
                echo "==============================="
                echo -e "🌐 Web Interface: ${BLUE}http://localhost:$STREAMLIT_PORT${NC}"
                echo -e "📋 API Documentation: ${BLUE}http://localhost:$FASTAPI_PORT/docs${NC}"
                echo -e "🔍 Health Check: ${BLUE}http://localhost:$FASTAPI_PORT/health${NC}"
                echo ""
                echo -e "${YELLOW}💡 Tip: Use 'bash run_local.sh stop' to stop all services${NC}"
                echo -e "${YELLOW}💡 Tip: Use 'bash run_local.sh status' to check service status${NC}"
                echo -e "${YELLOW}💡 Tip: Use 'bash run_local.sh test' to run evaluation tests${NC}"
                echo ""
                echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"
                
                # Wait for interrupt
                trap stop_services INT
                wait
            else
                print_error "Failed to start Streamlit UI"
                stop_services
                exit 1
            fi
        else
            print_error "Failed to start FastAPI server"
            exit 1
        fi
        ;;
    "stop")
        stop_services
        print_status "All services stopped"
        ;;
    "status")
        show_status
        ;;
    "test")
        run_tests
        ;;
    "restart")
        print_status "Restarting services..."
        stop_services
        sleep 2
        $0 start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|test|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start FastAPI and Streamlit servers"
        echo "  stop    - Stop all running services"
        echo "  status  - Show service status"
        echo "  test    - Run evaluation tests"
        echo "  restart - Restart all services"
        exit 1
        ;;
esac
