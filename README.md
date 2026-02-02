# 🎓 AI Educational Video Generator

A multi-agent system that converts PDF/text documents into engaging educational videos with AI-generated slides, voiceover, and talking avatar.

## 🧠 Architecture

```
User (PDF/Text) → Ingestion Agent → Content Understanding Agent → 
Slide Generation Agent → Explanation Agent → TTS Agent → 
[Optional] AI Face/Avatar Agent → Video Composition Agent → Final MP4
```

## 🛠️ Tech Stack (100% FREE)

| Component | Tool |
|-----------|------|
| **LLM** | Groq (llama-3.3-70b-versatile) |
| **PDF Processing** | pdfplumber |
| **Slide Rendering** | Pillow (PIL) |
| **TTS** | Edge TTS (Microsoft) |
| **Avatar** | Wav2Lip (Local or Optional) |
| **Video Assembly** | FFmpeg + MoviePy |
| **Backend** | FastAPI |

## 📁 Project Structure

```
slide-reader/
├── agents/                  # Individual agent modules
│   ├── ingestion.py
│   ├── content_understanding.py
│   ├── slide_generation.py
│   ├── explanation.py
│   ├── tts.py
│   ├── avatar.py
│   └── video_composition.py
├── orchestrator/            # Pipeline orchestration
│   └── pipeline.py
├── templates/               # Slide design templates
│   └── slide_template.py
├── outputs/                 # Generated files
│   ├── text/
│   ├── slides/
│   ├── audio/
│   ├── avatars/
│   └── videos/
├── uploads/                 # Input files
├── Wav2Lip/                 # Cloned Wav2Lip repo
├── app.py                   # FastAPI server
├── requirements.txt
├── setup.sh                 # Setup script
└── .env                     # API keys
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.8+
- FFmpeg installed
- NVIDIA GPU (recommended for Wav2Lip speed)
- Git

### 2. Clone and Install

```bash
# Clone this repo (if not already)
cd "c:\Users\akash2000.at\Desktop\slide reader"

# Install Python dependencies
pip install -r requirements.txt

# Clone Wav2Lip
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip
pip install -r requirements.txt

# Download Wav2Lip pretrained model
wget "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth" -O "checkpoints/wav2lip_gan.pth"
```

### 3. Configure API Keys

Create `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

Get free Groq API key: https://console.groq.com/

### 4. Run the Server

```bash
python app.py
```

Server runs on: `http://localhost:8000`

## 📖 Usage

### Command Line (Quick Start)

```bash
# Generate full video with avatar (Requires Wav2Lip)
python quick_start.py --full

# 🎙️ Generate voice-only video (No avatar setup needed!)
python quick_start.py --voice-only

# Generate quick 2-slide preview
python quick_start.py
```

### API Endpoint

**POST** `/generate-video`

The `avatar_image` is now **optional**. If omitted, the system generates a high-quality video with voiceover and slides only.

### Example with cURL

```bash
# With Avatar
curl -X POST "http://localhost:8000/generate-video" \
  -F "file=@document.pdf" \
  -F "avatar_image=@presenter.jpg"

# Voice-Only (Faster)
curl -X POST "http://localhost:8000/generate-video" \
  -F "file=@document.pdf"
```

## 🎯 Agent Details

### 1. Ingestion Agent
- Extracts text from PDF/DOCX/TXT
- Cleans headers, footers, page numbers
- Output: Clean JSON text

### 2. Content Understanding Agent
- Uses Groq LLM to understand topic
- Breaks content into teachable chunks
- Output: Structured knowledge sections

### 3. Slide Generation Agent
- Converts chunks into slide-friendly format
- Max 5 bullets per slide
- Generates visual hints
- Output: Slide JSON + rendered images

### 4. Explanation Agent
- Generates teaching scripts (20-30s per slide)
- Classroom-friendly language
- Output: Script per slide

### 5. TTS Agent
- Converts script to voice using Edge TTS
- Free unlimited usage
- Output: MP3 audio files

### 6. Avatar Agent (Wav2Lip)
- Syncs avatar face with audio
- Local processing
- Output: Talking head videos

### 7. Video Composition Agent
- Merges slides + avatar + audio
- Layout: Slide fullscreen, avatar in corner
- Output: Final MP4 video

## 🎨 Customization

### Change Slide Design
Edit `templates/slide_template.py`

### Change TTS Voice
Modify voice in `agents/tts.py`:
```python
voice = "en-US-JennyNeural"  # Change this
```

### Change Avatar Position
Modify layout in `agents/video_composition.py`

## ⚡ Performance Tips

- **GPU**: Wav2Lip is 10x faster with NVIDIA GPU
- **Batch Processing**: Process multiple slides in parallel
- **Cache**: Reuse avatar for same presenter

## 🐛 Troubleshooting

### Wav2Lip Installation Issues
```bash
cd Wav2Lip
pip install librosa==0.9.1
```

### FFmpeg Not Found
Install FFmpeg: https://ffmpeg.org/download.html

### Out of Memory
Reduce batch size in `agents/avatar.py`

## 📝 License

MIT License - Free for personal and commercial use

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

Made with ❤️ using 100% free and open-source tools
