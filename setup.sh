#!/bin/bash
# Setup script for Linux/Mac
echo "============================================"
echo "AI Educational Video Generator Setup"
echo "============================================"
echo ""

# Check Python
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found! Please install Python 3.8+"
    exit 1
fi
python3 --version
echo "✓ Python found"
echo ""

# Create virtual environment
echo "[2/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate and install dependencies
echo "[3/5] Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Clone Wav2Lip
echo "[4/5] Setting up Wav2Lip..."
if [ ! -d "Wav2Lip" ]; then
    echo "Cloning Wav2Lip repository..."
    git clone https://github.com/Rudrabha/Wav2Lip.git
    
    echo "Installing Wav2Lip dependencies..."
    cd Wav2Lip
    pip install -r requirements.txt
    
    # Create checkpoints directory
    mkdir -p checkpoints
    
    echo ""
    echo "============================================"
    echo "IMPORTANT: Download Wav2Lip Model"
    echo "============================================"
    echo "Downloading Wav2Lip model file..."
    
    # Try to download with wget or curl
    if command -v wget &> /dev/null; then
        wget "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth" -O "checkpoints/wav2lip_gan.pth"
    elif command -v curl &> /dev/null; then
        curl -L "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth" -o "checkpoints/wav2lip_gan.pth"
    else
        echo "Please download manually from:"
        echo "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth"
        echo "Save to: Wav2Lip/checkpoints/wav2lip_gan.pth"
        read -p "Press enter once downloaded..."
    fi
    
    cd ..
else
    echo "✓ Wav2Lip already installed"
fi
echo ""

# Setup environment file
echo "[5/5] Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "============================================"
    echo "IMPORTANT: Configure API Keys"
    echo "============================================"
    echo "Please edit .env file and add your Groq API key"
    echo "Get free API key from: https://console.groq.com/"
    echo ""
    read -p "Press enter to continue..."
else
    echo "✓ .env file already exists"
fi
echo ""

echo "============================================"
echo "✅ Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GROQ_API_KEY"
echo "2. Run: source venv/bin/activate"
echo "3. Test: python quick_start.py"
echo ""
