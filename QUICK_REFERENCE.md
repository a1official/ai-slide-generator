# 🚀 QUICK REFERENCE CARD

## 📦 Installation (First Time Only)

```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

**Then edit `.env` and add your Groq API key:** https://console.groq.com/

---

## ⚡ Quick Commands

### Generate Video (Full Pipeline)
```bash
# Option 1: Using CLI
python cli.py generate document.pdf presenter.jpg -o my_video.mp4

# Option 2: Using quick start
python quick_start.py --full

# Option 3: Using API
python app.py  # Start server
# Then upload via http://localhost:8000/docs
```

### Quick Preview (No Avatar, 30 seconds)
```bash
python quick_start.py
# or
python cli.py preview document.pdf
```

### Test System
```bash
# Test all agents
python test_agents.py

# Test specific agent
python test_agents.py slides
python test_agents.py tts
```

### Start API Server
```bash
python app.py
# Visit: http://localhost:8000/docs
```

---

## 📂 Where Files Go

| Type | Location |
|------|----------|
| **Input PDFs** | `uploads/` |
| **Avatar Image** | `uploads/avatar.jpg` |
| **Generated Slides** | `outputs/slides/` |
| **Audio Files** | `outputs/audio/` |
| **Avatar Videos** | `outputs/avatars/` |
| **Final Videos** | `outputs/videos/` |

---

## 🎨 Customization

### Change TTS Voice
Edit `.env`:
```env
TTS_VOICE=en-US-GuyNeural        # Male
TTS_VOICE=en-GB-SoniaNeural      # British Female
TTS_VOICE=en-AU-NatashaNeural    # Australian Female
```

List all voices:
```bash
python cli.py voices
```

### Change Slide Colors
Edit `agents/slide_generation.py` line 31:
```python
self.colors = {
    "background": (15, 23, 42),   # RGB values
    "primary": (99, 102, 241),
    "accent": (168, 85, 247),
}
```

### Change LLM Model
Edit `.env`:
```env
GROQ_MODEL=llama-3.3-70b-versatile  # Best quality (default)
GROQ_MODEL=mixtral-8x7b-32768       # Faster
GROQ_MODEL=llama-3.1-8b-instant     # Fastest
```

---

## 🐛 Common Errors & Fixes

| Error | Solution |
|-------|----------|
| `GROQ_API_KEY not found` | Edit `.env`, add key from https://console.groq.com/ |
| `Wav2Lip not found` | Run: `git clone https://github.com/Rudrabha/Wav2Lip.git` |
| `checkpoint not found` | Download model to `Wav2Lip/checkpoints/wav2lip_gan.pth` |
| `FFmpeg not found` | Install from https://ffmpeg.org/ |
| Very slow avatar | Use GPU or skip avatar with preview mode |

---

## 📊 Typical Processing Time

| Slides | With GPU | Without GPU |
|--------|----------|-------------|
| 2 slides | 1 min | 5 min |
| 5 slides | 3 min | 12 min |
| 10 slides | 6 min | 25 min |

---

## 🎯 Best Practices

### For Best Quality:
1. **Documents**: Use well-structured PDFs with clear headings
2. **Avatar**: Use frontal face photo, good lighting, 512x512+
3. **Content**: Limit to 5-10 main concepts per document
4. **GPU**: Use NVIDIA GPU for 10x faster avatar generation

### Troubleshooting Steps:
1. Test with `python test_agents.py`
2. Check `.env` has correct API key
3. Verify Wav2Lip model downloaded
4. Try preview mode first (faster, no avatar)
5. Check `outputs/` folders for intermediate files

---

## 🔗 Helpful Links

- **Groq API Key**: https://console.groq.com/
- **Wav2Lip Model**: https://github.com/Rudrabha/Wav2Lip/releases
- **FFmpeg Download**: https://ffmpeg.org/download.html
- **Full Documentation**: See `USAGE_GUIDE.md`
- **Project Summary**: See `PROJECT_SUMMARY.md`

---

## 🆘 Help

**Read detailed docs:**
- `README.md` - Overview
- `USAGE_GUIDE.md` - Step-by-step guide
- `PROJECT_SUMMARY.md` - Architecture details

**Test components:**
```bash
python test_agents.py
```

**Check API health:**
```bash
python app.py
# Visit: http://localhost:8000/health
```

---

**Made with ❤️ - 100% FREE Tools**

Groq | Edge TTS | Wav2Lip | FFmpeg | MoviePy | FastAPI
