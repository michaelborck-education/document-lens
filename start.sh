#!/bin/bash

# CiteSight Full Stack Startup Script

echo "🚀 Starting CiteSight Application..."
echo "===================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down CiteSight..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set trap to cleanup on Ctrl+C
trap cleanup INT

# Start backend in background
echo "📦 Starting backend server..."
./start-backend.sh &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
echo ""
echo "📦 Starting frontend server..."
./start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "===================================="
echo "✅ CiteSight is starting up!"
echo ""
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo "🌐 Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "===================================="

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID