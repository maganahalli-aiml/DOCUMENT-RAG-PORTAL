#!/bin/bash

# Quick Service Restart Script for Document RAG Portal
echo "🔄 Restarting Document RAG Portal Services..."

# Kill existing processes
echo "🛑 Stopping existing services..."
pkill -f "serve.*build"
pkill -f "uvicorn.*api"

# Wait a moment
sleep 2

# Start backend API
echo "🚀 Starting backend API..."
cd /Users/alampata/Desktop/LLMOPS/DOCUMENT-RAG-PORTAL
source .venv/bin/activate
nohup python -m uvicorn api.main_simple:app --host localhost --port 8080 > api.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "🌐 Starting frontend..."
cd /Users/alampata/Desktop/LLMOPS/DOCUMENT-RAG-PORTAL/frontend/document-rag-portal
nohup npx serve -s build -l 3001 > serve.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

# Check if services are running
echo "✅ Checking service status..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Backend API: Running on http://localhost:8080"
else
    echo "❌ Backend API: Failed to start"
fi

if curl -s -I http://localhost:3001 > /dev/null; then
    echo "✅ Frontend: Running on http://localhost:3001"
else
    echo "❌ Frontend: Failed to start"
fi

echo "🎉 Service restart complete!"
echo "📱 Access the app at: http://localhost:3001"
echo "📊 Evaluation page: http://localhost:3001/evaluation"
echo "🔧 API health: http://localhost:8080/health"
