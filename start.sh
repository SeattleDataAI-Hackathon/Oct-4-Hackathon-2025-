#!/bin/bash

echo "============================================"
echo "     CarePath - Starting Application"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js 18 or higher"
    exit 1
fi

echo "[1/4] Checking Python dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi

echo "[2/4] Checking Node.js dependencies..."
cd carepath-ui
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install Node.js dependencies"
        exit 1
    fi
fi
cd ..

echo "[3/4] Starting Backend Server..."
python3 backend.py &
BACKEND_PID=$!
sleep 3

echo "[4/4] Starting Frontend..."
cd carepath-ui
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "============================================"
echo "CarePath is running!"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services..."
echo "============================================"

# Trap Ctrl+C and kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for processes
wait
