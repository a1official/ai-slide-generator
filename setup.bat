@echo off
REM Setup script for Windows
echo ============================================
echo AI Educational Video Generator Setup
echo ============================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo OK: Python found
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo OK: Virtual environment created
) else (
    echo OK: Virtual environment already exists
)
echo.

REM Activate and install dependencies
echo [3/5] Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo OK: Dependencies installed
echo.

REM Clone Wav2Lip
echo [4/5] Setting up Wav2Lip...
if not exist "Wav2Lip" (
    echo Cloning Wav2Lip repository...
    git clone https://github.com/Rudrabha/Wav2Lip.git
    
    echo Installing Wav2Lip dependencies...
    cd Wav2Lip
    pip install -r requirements.txt
    
    REM Create checkpoints directory
    if not exist "checkpoints" mkdir checkpoints
    
    echo.
    echo ============================================
    echo IMPORTANT: Download Wav2Lip Model
    echo ============================================
    echo Please download the Wav2Lip model file:
    echo.
    echo URL: https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth
    echo.
    echo Save it to: Wav2Lip\checkpoints\wav2lip_gan.pth
    echo.
    echo Press any key once you've downloaded the model...
    pause
    
    cd ..
) else (
    echo OK: Wav2Lip already installed
)
echo.

REM Setup environment file
echo [5/5] Setting up environment...
if not exist ".env" (
    copy .env.example .env
    echo OK: Created .env file
    echo.
    echo ============================================
    echo IMPORTANT: Configure API Keys
    echo ============================================
    echo Please edit .env file and add your Groq API key
    echo Get free API key from: https://console.groq.com/
    echo.
    pause
) else (
    echo OK: .env file already exists
)
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env and add your GROQ_API_KEY
echo 2. Download Wav2Lip model (if not done yet)
echo 3. Run: venv\Scripts\activate.bat
echo 4. Test: python quick_start.py
echo.
pause
