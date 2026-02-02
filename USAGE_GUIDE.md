# 🎓 AI Educational Video Generator - Step by Step Guide

This guide will walk you through setting up and using the system.

---

## 📋 Prerequisites

Before you begin, make sure you have:

1. **Python 3.8 or higher** installed
   - Check with: `python --version`
   - Download from: https://www.python.org/downloads/

2. **Git** installed (for cloning Wav2Lip)
   - Check with: `git --version`
   - Download from: https://git-scm.com/downloads

3. **FFmpeg** installed (for video processing)
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: `sudo apt install ffmpeg`
   - Mac: `brew install ffmpeg`

4. **(Optional) NVIDIA GPU** for faster Wav2Lip processing
   - Check with: `nvidia-smi`
   - Not required but highly recommended

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Run Setup Script

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Clone Wav2Lip repository
- Download Wav2Lip model (Linux/Mac only)
- Create `.env` configuration file

### Step 2: Get FREE Groq API Key

1. Visit: https://console.groq.com/
2. Sign up (free)
3. Create an API key
4. Copy the key

### Step 3: Configure Environment

Edit the `.env` file and add your API key:

```env
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### Step 4: Activate Environment

**Windows:**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 5: Test the System

Run a quick test:
```bash
python test_agents.py
```

This will test each component individually.

### Step 6: Generate Your First Video

**Quick Preview (No Avatar):**
```bash
python quick_start.py
```

This generates a 2-slide preview video in ~30 seconds.

**Full Video (With Avatar):**
1. Add your presenter image to `uploads/avatar.jpg`
2. Run:
```bash
python quick_start.py --full
```

---

## 📚 Detailed Usage

### Using the API Server

Start the server:
```bash
python app.py
```

The server will run at: http://localhost:8000

**API Documentation:** http://localhost:8000/docs

### Generate Video via API

```bash
curl -X POST "http://localhost:8000/generate-video" \
  -F "file=@your_document.pdf" \
  -F "avatar_image=@your_photo.jpg"
```

### Generate Preview via API

```bash
curl -X POST "http://localhost:8000/generate-preview" \
  -F "file=@your_document.pdf"
```

---

## 🎨 Customization

### Change TTS Voice

Edit `.env`:
```env
TTS_VOICE=en-US-GuyNeural  # Male voice
```

Available voices:
- `en-US-JennyNeural` - Friendly female (default)
- `en-US-GuyNeural` - Casual male
- `en-US-AriaNeural` - Professional female
- `en-GB-SoniaNeural` - British female
- `en-AU-NatashaNeural` - Australian female

### Customize Slide Design

Edit `agents/slide_generation.py` and modify the `colors` dictionary:

```python
self.colors = {
    "background": (15, 23, 42),    # Dark blue
    "primary": (99, 102, 241),     # Indigo
    "accent": (168, 85, 247),      # Purple
    "text": (248, 250, 252),       # White
}
```

### Change LLM Model

Edit `.env`:
```env
GROQ_MODEL=mixtral-8x7b-32768
```

Available free models:
- `llama-3.3-70b-versatile` (default, best quality)
- `mixtral-8x7b-32768` (faster)
- `llama-3.1-8b-instant` (fastest)

---

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not found"

**Solution:** Make sure you:
1. Created `.env` file (copy from `.env.example`)
2. Added your API key to `.env`
3. Restarted the application

### Issue: "Wav2Lip not found"

**Solution:**
```bash
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip
pip install -r requirements.txt
```

### Issue: "Wav2Lip checkpoint not found"

**Solution:** Download the model file:

**Windows:**
```powershell
Invoke-WebRequest -Uri "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth" -OutFile "Wav2Lip\checkpoints\wav2lip_gan.pth"
```

**Linux/Mac:**
```bash
wget "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth" -O "Wav2Lip/checkpoints/wav2lip_gan.pth"
```

### Issue: "FFmpeg not found"

**Solution:** Install FFmpeg:
- Windows: Download from https://ffmpeg.org/ and add to PATH
- Linux: `sudo apt install ffmpeg`
- Mac: `brew install ffmpeg`

### Issue: Wav2Lip is very slow

**Cause:** No GPU available

**Solutions:**
1. Use a machine with NVIDIA GPU
2. Reduce video resolution in `agents/avatar.py`
3. Generate fewer slides for faster processing
4. Skip avatar generation for faster previews

---

## 📊 Project Structure

```
slide-reader/
├── agents/              # Individual processing agents
│   ├── ingestion.py            # PDF/DOCX/TXT extraction
│   ├── content_understanding.py # LLM content analysis
│   ├── slide_generation.py     # Slide image creation
│   ├── explanation.py          # Script generation
│   ├── tts.py                  # Text-to-speech
│   ├── avatar.py               # Wav2Lip lip-sync
│   └── video_composition.py    # Final video assembly
│
├── orchestrator/        # Pipeline coordination
│   └── pipeline.py             # Main orchestrator
│
├── outputs/             # Generated files
│   ├── slides/                 # Slide images
│   ├── audio/                  # Audio files
│   ├── avatars/                # Avatar videos
│   └── videos/                 # Final videos
│
├── uploads/             # Input files
├── Wav2Lip/             # Lip-sync repository
├── app.py               # FastAPI server
├── quick_start.py       # Quick test script
├── test_agents.py       # Unit tests
└── requirements.txt     # Python dependencies
```

---

## 💡 Tips for Best Results

### For Documents:
- Use clear, well-structured documents
- Include headings and bullet points
- Avoid scanned PDFs (use OCR if needed)
- Keep content focused (5-10 main concepts)

### For Avatar Images:
- Use a clear, frontal face photo
- Good lighting
- Neutral background
- High resolution (at least 512x512)
- JPG or PNG format

### For Video Quality:
- Let each agent complete before using output
- Check intermediate outputs in `outputs/` folders
- Use GPU for Wav2Lip (10x faster)
- Start with preview mode to test content

---

## 🔧 Advanced Usage

### Custom Pipeline

Create your own pipeline script:

```python
from orchestrator.pipeline import VideoGenerationPipeline

pipeline = VideoGenerationPipeline()

result = pipeline.generate_video(
    document_path="my_document.pdf",
    avatar_image_path="my_avatar.jpg",
    output_name="my_lesson.mp4"
)

print(f"Video created: {result['video_path']}")
```

### Individual Agent Usage

Use agents separately:

```python
from agents.ingestion import IngestionAgent

agent = IngestionAgent()
data = agent.process_file("document.pdf")
print(data["raw_text"])
```

---

## 📈 Performance Benchmarks

Approximate processing times (Intel i7, 16GB RAM, RTX 3060):

| Pipeline Stage | Time per Slide | Total (10 slides) |
|---------------|---------------|-------------------|
| Ingestion | 1-2s | 2s |
| Content Understanding | 2-5s | 10s |
| Slide Generation | 1s | 10s |
| Explanation | 2-4s | 30s |
| TTS | 2-3s | 25s |
| Avatar (GPU) | 15-30s | 240s |
| Video Composition | 5s | 50s |
| **Total** | - | **~6 minutes** |

*Without GPU, avatar generation can take 2-5 minutes per slide.*

---

## 🤝 Contributing

Found a bug or want to add a feature? Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - Free for personal and commercial use

---

## 🆘 Getting Help

If you encounter issues:

1. Check this guide
2. Review error messages carefully
3. Test individual agents with `test_agents.py`
4. Check GitHub issues
5. Create a new issue with details

---

## 🎉 What You Can Build

With this system, you can create:

- **Educational videos** from lecture notes
- **Tutorial videos** from documentation
- **Training materials** from company guides
- **Explainer videos** from research papers
- **Course content** from textbooks

All 100% free and customizable!

---

**Happy video creating! 🚀**
