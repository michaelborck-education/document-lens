#!/bin/bash

# DocumentLens Microservice Startup Script

echo "🚀 Starting DocumentLens Microservice..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    uv sync
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOL'
DEBUG=true
MAX_FILE_SIZE=10485760
MAX_FILES_PER_REQUEST=5
RATE_LIMIT=10/minute
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
SECRET_KEY=development-secret-key-change-in-production
EOL
fi

# Start the backend server
echo "✅ Starting DocumentLens server on http://localhost:8000"
echo "📚 API Documentation available at http://localhost:8000/api/docs"
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000