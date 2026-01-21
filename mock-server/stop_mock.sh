#!/bin/bash

# WorkOn RBGA Mock Server Stop Script
# This script stops the mock server and deactivates virtual environment

echo "🛑 Stopping WorkOn RBGA Mock Server..."

# Find and kill Flask processes running on port 5000
FLASK_PID=$(lsof -ti:5000)

if [ ! -z "$FLASK_PID" ]; then
    echo "🔍 Found Flask process on port 5000 (PID: $FLASK_PID)"
    echo "💀 Killing Flask process..."
    kill -TERM $FLASK_PID
    sleep 2

    # Check if process is still running and force kill if needed
    if kill -0 $FLASK_PID 2>/dev/null; then
        echo "⚡ Force killing Flask process..."
        kill -9 $FLASK_PID
    fi

    echo "✅ Flask process stopped"
else
    echo "ℹ️  No Flask process found on port 5000"
fi

# Deactivate virtual environment if active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "🔧 Deactivating virtual environment..."
    deactivate
    echo "✅ Virtual environment deactivated"
else
    echo "ℹ️  No active virtual environment found"
fi

echo "🎯 Mock server stopped successfully!"
echo "💡 You can restart it with: ./start_mock.sh"