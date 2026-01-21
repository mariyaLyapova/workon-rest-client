#!/bin/bash

# WorkOn RBGA Mock Server Startup Script
# This script handles virtual environment setup and starts the mock server

set -e  # Exit on any error

PROJECT_DIR="/Users/bam1sf3/work/personal/workon-rest-client/mock-server"
VENV_DIR="$PROJECT_DIR/venv"
MOCK_SERVER="$PROJECT_DIR/mock_workon_server.py"

echo "🚀 Starting WorkOn RBGA Mock Server..."
echo "📁 Project directory: $PROJECT_DIR"

# Navigate to project directory
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📥 Installing Flask..."
    pip install flask
    echo "✅ Flask installed"
else
    echo "✅ Flask already installed"
fi

# Check if mock server file exists
if [ ! -f "$MOCK_SERVER" ]; then
    echo "❌ Error: mock_workon_server.py not found at $MOCK_SERVER"
    exit 1
fi

echo "🎯 Starting mock server..."
echo "💡 Use Ctrl+C to stop the server"
echo "💡 Run 'deactivate' after stopping to exit virtual environment"
echo ""

# Start the mock server
python3 mock_workon_server.py