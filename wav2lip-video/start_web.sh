#!/bin/bash

# Start Wav2Lip Web Interface
# This script starts the Flask web server

echo "=================================="
echo "Wav2Lip Video Processing Web UI"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if in correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the wav2lip-video directory."
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask not installed. Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo "✓ Dependencies OK"
echo ""

# Check for model checkpoint
if [ ! -f "models/wav2lip_gan.pth" ]; then
    echo "⚠️  Warning: Model checkpoint not found at models/wav2lip_gan.pth"
    echo "   The application may not work without a valid checkpoint."
    echo ""
fi

# Start the server
echo "Starting web server..."
echo ""
echo "=================================="
echo "🌐 Server starting at:"
echo "   http://localhost:5000"
echo "=================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
