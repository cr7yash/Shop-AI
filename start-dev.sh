#!/bin/bash

# Start development servers for ShopAI e-commerce platform

echo "🚀 Starting ShopAI Development Servers..."

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $1 is already in use"
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

# Check if ports are available
echo "🔍 Checking ports..."
if ! check_port 3000; then
    echo "Please stop the process using port 3000 and try again"
    exit 1
fi

if ! check_port 8000; then
    echo "Please stop the process using port 8000 and try again"
    exit 1
fi

# Start backend server
echo "🐍 Starting FastAPI backend server..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Start backend in background
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "⚛️ Starting Next.js frontend server..."
cd ../ecommerce-app
npm install > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Development servers started successfully!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
