#!/bin/bash

# Quick Start Script for Wav2Lip Video Processing
# This script helps you get started quickly

echo "=================================="
echo "Wav2Lip Video Processing Setup"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed."
    echo "   Install with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)"
    exit 1
fi

echo "✓ FFmpeg found"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"

# Check for model checkpoint
echo ""
echo "Checking for Wav2Lip model checkpoint..."

if [ ! -d "models" ]; then
    mkdir -p models
fi

if [ ! -f "models/wav2lip_gan.pth" ]; then
    echo "⚠️  Model checkpoint not found in models/wav2lip_gan.pth"
    echo "   Please download the Wav2Lip checkpoint and place it in the models/ directory"
    echo ""
    echo "   You can use a checkpoint from:"
    echo "   - Official Wav2Lip repository"
    echo "   - Your existing checkpoint at: ../checkpoints/"
    echo ""
    read -p "   Do you want to create a symlink to ../checkpoints/wav2lip_gan.pth? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "../checkpoints/wav2lip_gan.pth" ]; then
            ln -s "$(pwd)/../checkpoints/wav2lip_gan.pth" models/wav2lip_gan.pth
            echo "✓ Symlink created"
        else
            echo "❌ Checkpoint not found at ../checkpoints/wav2lip_gan.pth"
        fi
    fi
else
    echo "✓ Model checkpoint found"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p outputs temp examples/videos examples/audio

echo "✓ Directories created"

# Setup complete
echo ""
echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Place your Wav2Lip checkpoint in models/ directory (if not already done)"
echo "2. Run a test with: python video_inference.py --help"
echo "3. Check examples/usage_examples.py for usage examples"
echo "4. Read README.md for detailed documentation"
echo ""
echo "Quick test command:"
echo "  python video_inference.py \\"
echo "    --checkpoint models/wav2lip_gan.pth \\"
echo "    --face_video path/to/video.mp4 \\"
echo "    --audio path/to/audio.wav \\"
echo "    --output outputs/result.mp4"
echo ""
