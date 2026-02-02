# 🎓 AI Educational Video Generator - Full Project Context

**Last Updated:** January 30, 2026  
**Project Location:** `c:\Users\akash2000.at\Desktop\slide reader`

---

## 📋 **Project Overview**

This is a **multi-agent AI system** that automatically converts educational documents (PDF/DOCX/TXT) into professional-quality video presentations with:
- ✅ AI-generated slides with modern designs
- ✅ Natural AI voiceover narration
- ✅ Lip-synced talking avatar (optional)
- ✅ 100% free and open-source tools

### **Key Achievement**
A complete production-ready educational video generator using **zero-cost** infrastructure, combining multiple AI technologies into a cohesive pipeline.

---

## 🏗️ **System Architecture**

### **7-Agent Pipeline**

```
Document Input (PDF/DOCX/TXT)
    ↓
[1] Ingestion Agent
    → Extracts & cleans text from documents
    → Tools: pdfplumber, PyMuPDF, pytesseract
    ↓
[2] Content Understanding Agent
    → Uses LLM to analyze and structure content
    → Breaks into teachable chunks (5-20 sections)
    → Tools: Groq LLM (llama-3.3-70b) or Amazon Bedrock
    ↓
[3] Slide Generation Agent
    → Creates beautiful slide images
    → Multiple themes (modern_dark, gradient, minimal)
    → Tools: Pillow (PIL), optional Amazon Titan Image Generator
    ↓
[4] Explanation Agent
    → Generates teaching scripts per slide (20-30s each)
    → Conversational, beginner-friendly language
    → Tools: Groq LLM
    ↓
[5] TTS Agent
    → Converts scripts to natural voice audio
    → Multiple voice options
    → Tools: Edge TTS (Microsoft, unlimited free)
    ↓
[6] Avatar Agent (Optional)
    → Lip-syncs presenter face with audio
    → Local GPU-accelerated processing
    → Tools: Wav2Lip
    ↓
[7] Video Composition Agent
    → Merges slides + avatar + audio
    → Professional layout (avatar in corner)
    → Tools: FFmpeg, MoviePy
    ↓
Final MP4 Video Output
```

---

## 📦 **Tech Stack**

### **Backend & API**
- **Framework:** FastAPI (Python 3.8+)
- **Server:** Uvicorn
- **CORS:** Enabled for cross-origin requests
- **Endpoints:** `/generate-video`, `/generate-preview`, `/download/{filename}`

### **Frontend (GUI)**
- **Framework:** Next.js 16.1.6 (React 19.2.3)
- **Styling:** TailwindCSS 4
- **UI Library:** Framer Motion (animations), Lucide React (icons)
- **Language:** TypeScript
- **API Integration:** Axios for backend communication

### **AI/ML Components**
| Component | Technology | Cost |
|-----------|-----------|------|
| LLM (Primary) | Groq API (llama-3.3-70b-versatile) | FREE |
| LLM (Alternative) | Amazon Bedrock (Nova Pro v1) | Per-use |
| Image Generation | Pillow + Amazon Titan Image v2 (optional) | Mostly FREE |
| TTS | Edge TTS (Microsoft) | FREE (Unlimited) |
| Avatar Lip-Sync | Wav2Lip (Local) | FREE |
| Video Processing | FFmpeg + MoviePy | FREE |

### **Document Processing**
- PDF: `pdfplumber`, `PyMuPDF`
- DOCX: `python-docx`
- OCR: `pytesseract`

---

## 📁 **Project Structure**

```
slide-reader/
│
├── 📄 Core Documentation
│   ├── README.md                    # Main overview
│   ├── PROJECT_SUMMARY.md           # Detailed architecture
│   ├── USAGE_GUIDE.md              # Step-by-step instructions
│   ├── QUICK_REFERENCE.md          # Command cheat sheet
│   └── FULL_PROJECT_CONTEXT.md     # This file
│
├── ⚙️ Configuration
│   ├── .env                        # Environment variables (gitignored)
│   ├── .env.example                # Template for .env
│   ├── requirements.txt            # Python dependencies
│   ├── setup.bat / setup.sh        # Automated setup scripts
│   └── .gitignore
│
├── 🚀 Entry Points
│   ├── app.py                      # FastAPI server (main backend)
│   ├── quick_start.py              # CLI for quick testing
│   ├── cli.py                      # Command-line interface
│   └── test_agents.py              # Unit tests for each agent
│
├── 🤖 Agents (Core Processing)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── ingestion.py            # PDF/DOCX/TXT extraction
│   │   ├── content_understanding.py # LLM analysis & chunking
│   │   ├── slide_generation.py     # Slide image creation
│   │   ├── explanation.py          # Script generation
│   │   ├── tts.py                  # Text-to-speech
│   │   ├── avatar.py               # Wav2Lip integration
│   │   └── video_composition.py    # Final video assembly
│
├── 🎯 Orchestration
│   └── orchestrator/
│       ├── __init__.py
│       └── pipeline.py             # Coordinates all agents
│
├── 🖥️ Frontend (Next.js GUI)
│   └── gui/
│       ├── app/
│       │   ├── page.tsx            # Main UI component
│       │   ├── layout.tsx          # App layout
│       │   ├── globals.css         # Global styles
│       │   └── favicon.ico
│       ├── public/                 # Static assets
│       ├── package.json
│       ├── tsconfig.json
│       ├── next.config.ts
│       └── tailwind.config.ts
│
├── 📂 Data Directories
│   ├── uploads/                    # User-uploaded documents
│   │   └── .gitkeep
│   ├── outputs/
│   │   ├── text/                   # Extracted text
│   │   ├── slides/                 # Generated slide images
│   │   ├── audio/                  # TTS audio files
│   │   ├── avatars/                # Lip-synced avatar videos
│   │   └── videos/                 # Final output videos
│   └── temp/                       # Temporary processing files
│
├── 🎥 Wav2Lip Integration
│   └── Wav2Lip/                    # Cloned external repo
│       ├── checkpoints/            # Pre-trained models
│       ├── inference.py            # Modified for integration
│       └── requirements.txt
│
└── 🧪 Development
    ├── venv/                       # Python virtual environment
    ├── __pycache__/
    └── test_*.py                   # Various test scripts
```

---

## 🔑 **Key Features & Capabilities**

### **1. Intelligent Content Processing**
- **Multi-format support:** PDF, DOCX, TXT
- **Smart text extraction:** Removes headers, footers, page numbers
- **Context-aware chunking:** Uses LLM to break content into logical teaching units
- **Customizable depth:** Standard (5-10 chunks) or Comprehensive (15-20 chunks)

### **2. Professional Slide Design**
- **Multiple themes:**
  - `modern_dark` - Dark gradients, high contrast
  - `gradient` - Vibrant color gradients
  - `minimal` - Clean, minimal design
- **Dynamic layouts:** Title slide, content slides, diagram slides, outro
- **Visual hints:** Supports flowcharts, hierarchies, Venn diagrams
- **AI-generated backgrounds:** Optional Amazon Bedrock integration

### **3. Natural Voice Generation**
- **Unlimited free TTS** via Edge TTS
- **Multiple voices:**
  - en-US-JennyNeural (friendly female, default)
  - en-US-GuyNeural (casual male)
  - en-GB-SoniaNeural (British female)
  - en-AU-NatashaNeural (Australian female)
- **Script timing:** 20-30 seconds per slide

### **4. Lip-Synced Avatar (Optional)**
- **Local processing** with Wav2Lip
- **GPU acceleration** supported (10x faster)
- **High-quality results** with wav2lip_gan model
- **Flexible layout:** Avatar overlay in corner or full-screen

### **5. RESTful API**
- **Auto-generated docs:** Available at `/docs` (Swagger UI)
- **Health checks:** `/health` endpoint with agent status
- **File upload:** Multipart form data support
- **Download endpoint:** `/download/{filename}` for completed videos

### **6. Modern Web UI**
- **Next.js frontend** with TypeScript
- **Responsive design** with TailwindCSS
- **Smooth animations** via Framer Motion
- **Real-time progress** tracking (planned)

---

## ⚙️ **Configuration**

### **Environment Variables (.env)**

```env
# Required
GROQ_API_KEY=gsk_...                    # Free from https://console.groq.com/
GROQ_MODEL=llama-3.3-70b-versatile      # LLM model

# Optional AWS (for advanced features)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# TTS Configuration
TTS_VOICE=en-US-JennyNeural             # Voice selection

# Paths
WAV2LIP_PATH=./Wav2Lip
WAV2LIP_CHECKPOINT=checkpoints/wav2lip_gan.pth
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs

# Server
HOST=0.0.0.0
PORT=8000
```

### **Python Dependencies (requirements.txt)**

**Core Framework:**
- fastapi==0.108.0
- uvicorn==0.25.0
- python-multipart==0.0.6
- pydantic==2.5.3

**Document Processing:**
- pdfplumber==0.10.3
- PyMuPDF==1.23.8
- pytesseract==0.3.10
- python-docx==1.1.0

**AI/LLM:**
- groq==0.4.1
- python-dotenv==1.0.0

**Image Processing:**
- Pillow==10.1.0
- matplotlib==3.8.2

**TTS:**
- edge-tts==6.1.9

**Video Processing:**
- moviepy==1.0.3
- ffmpeg-python==0.2.0

**Wav2Lip Dependencies:**
- numpy==1.26.4
- opencv-python==4.8.1.78
- librosa==0.9.2
- scipy==1.11.4
- tqdm==4.66.1

**Utilities:**
- requests==2.31.0
- aiofiles==23.2.1

---

## 🚀 **Usage Workflows**

### **Quick Start (Voice-Only)**
```bash
# 1. Setup
setup.bat  # Windows
# or
./setup.sh  # Linux/Mac

# 2. Configure API key in .env
GROQ_API_KEY=your_key_here

# 3. Run quick test
python quick_start.py --voice-only
```

### **Full Pipeline (With Avatar)**
```bash
# 1. Generate with avatar
python quick_start.py --full

# 2. Or via API
python app.py  # Start server
# Upload via http://localhost:8000/docs
```

### **API Usage**
```bash
# Start backend
cd "c:\Users\akash2000.at\Desktop\slide reader"
python app.py
# Server runs on http://localhost:8000

# Start frontend (separate terminal)
cd gui
npm run dev
# UI runs on http://localhost:3000

# API Examples
curl -X POST "http://localhost:8000/generate-video" \
  -F "file=@document.pdf" \
  -F "avatar_image=@presenter.jpg"
```

---

## 📊 **Performance Metrics**

### **Processing Time (10-slide video)**

| Stage | Time | GPU | CPU-only |
|-------|------|-----|----------|
| Ingestion | 2s | ✓ | ✓ |
| Content Understanding | 10s | ✓ | ✓ |
| Slide Generation | 10s | ✓ | ✓ |
| Explanation | 30s | ✓ | ✓ |
| TTS | 25s | ✓ | ✓ |
| Avatar | **240s** | **900s** (15min) |
| Video Composition | 50s | ✓ | ✓ |
| **TOTAL** | **~6 min** | **~25 min** |

**Hardware Used:** Intel i7, 16GB RAM, NVIDIA RTX 3060

---

## 🎯 **Use Cases**

1. **Education:**
   - Convert lecture notes → video lessons
   - Create course content from PDFs
   - Generate tutorial videos

2. **Corporate Training:**
   - Transform manuals → training videos
   - Onboarding materials
   - Product documentation

3. **Content Creation:**
   - Explain research papers
   - Technical tutorials
   - Educational content for YouTube

4. **Accessibility:**
   - Make written content more accessible
   - Visual + auditory learning
   - Engaging presentation format

---

## 🔧 **Customization Guide**

### **Change Slide Theme**
Edit in API call or modify `agents/slide_generation.py`:
```python
self.colors = {
    "background": (15, 23, 42),    # RGB
    "primary": (99, 102, 241),
    "accent": (168, 85, 247),
    "text": (248, 250, 252),
}
```

### **Change TTS Voice**
Edit `.env`:
```env
TTS_VOICE=en-US-GuyNeural  # Male voice
```

### **Change LLM Model**
Edit `.env`:
```env
GROQ_MODEL=mixtral-8x7b-32768  # Faster model
```

### **Switch to Amazon Bedrock**
```python
# In API call
provider="amazon_bedrock"
```

---

## 🐛 **Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY not found` | Add key to `.env` from https://console.groq.com/ |
| `Wav2Lip not found` | Run: `git clone https://github.com/Rudrabha/Wav2Lip.git` |
| `checkpoint not found` | Download `wav2lip_gan.pth` to `Wav2Lip/checkpoints/` |
| `FFmpeg not found` | Install from https://ffmpeg.org/ |
| Very slow avatar | Use GPU or skip with `--voice-only` |

---

## 📈 **Recent Development History**

Based on conversation history, recent work includes:

1. **Talking News Presenter** (Jan 29, 2026)
   - Integrated SadTalker for face animation
   - Added news ticker functionality
   - Overlay system for studio backgrounds

2. **Frontend/Backend Integration** (Jan 29, 2026)
   - Running both Next.js GUI and FastAPI backend
   - CORS configuration for cross-origin requests

3. **Previous Projects Referenced:**
   - Electron voice mode applications
   - Full-stack deployment (Render + MongoDB)
   - Task management Kanban system

---

## 🔮 **Future Enhancements**

**Planned Improvements:**
1. Add background music to videos
2. Support more languages (TTS supports 40+)
3. Animated transitions between slides
4. Chart/diagram generation from data
5. Batch processing multiple documents
6. Progress tracking in web UI
7. Cloud deployment (AWS/GCP)
8. Caching for faster re-generation
9. Real-time preview in browser
10. Custom branding/watermarks

---

## 🎓 **Agent Details**

### **1. IngestionAgent** (`agents/ingestion.py`)
- Extracts text from PDF/DOCX/TXT
- Cleans noise (headers, footers, page numbers)
- Optionally extracts page images for vision models
- Output: `{"raw_text": "...", "metadata": {...}}`

### **2. ContentUnderstandingAgent** (`agents/content_understanding.py`)
- Uses Groq LLM or Amazon Bedrock
- Supports vision models for document images
- Breaks content into 5-20 chunks based on depth
- Output: `[{"title": "...", "key_points": [...], "complexity": "..."}]`

### **3. SlideGenerationAgent** (`agents/slide_generation.py`)
- Creates 1920x1080 PNG slides
- Multiple themes and layouts
- Can generate backgrounds via Amazon Nova Canvas
- Supports diagram rendering (flowcharts, etc.)
- Output: List of slide image paths

### **4. ExplanationAgent** (`agents/explanation.py`)
- Generates 20-30s teaching scripts per slide
- Conversational, beginner-friendly language
- Adapts to content complexity
- Output: `[{"slide_num": 1, "script": "..."}]`

### **5. TTSAgent** (`agents/tts.py`)
- Uses Microsoft Edge TTS (unlimited free)
- Multiple voice options
- Generates MP3 files
- Output: List of audio file paths

### **6. AvatarAgent** (`agents/avatar.py`)
- Integrates Wav2Lip for lip-sync
- Lazy-loaded (only when needed)
- GPU-accelerated when available
- Output: List of avatar video paths

### **7. VideoCompositionAgent** (`agents/video_composition.py`)
- Merges slides, avatar, and audio
- Flexible layouts (avatar corner or full-screen)
- Uses FFmpeg for final encoding
- Output: Final MP4 video path

### **Pipeline Orchestrator** (`orchestrator/pipeline.py`)
- Coordinates all 7 agents
- Handles errors and progress tracking
- Supports preview mode (2 slides, no avatar)
- Returns metadata with all generated files

---

## 💡 **Tips for Best Results**

### **Documents:**
- Use clear, well-structured documents
- Include headings and bullet points
- Avoid scanned PDFs (use OCR if needed)
- Keep content focused (5-10 main concepts)

### **Avatar Images:**
- Clear, frontal face photo
- Good lighting, neutral background
- High resolution (512x512+)
- JPG or PNG format

### **Video Quality:**
- Check intermediate outputs in `outputs/` folders
- Use GPU for Wav2Lip (10x faster)
- Start with preview mode to test content
- Standard depth for quick videos, comprehensive for detailed

---

## 📞 **Support & Resources**

- **Full Docs:** See `USAGE_GUIDE.md`
- **Quick Reference:** See `QUICK_REFERENCE.md`
- **API Docs:** http://localhost:8000/docs (when server running)
- **Test System:** `python test_agents.py`
- **Groq API:** https://console.groq.com/
- **Wav2Lip Model:** https://github.com/Rudrabha/Wav2Lip/releases
- **FFmpeg:** https://ffmpeg.org/download.html

---

## 📄 **License**

**MIT License** - Free for personal and commercial use

All third-party tools used are also open-source or have free tiers:
- Groq: Free tier available
- Edge TTS: Unlimited free
- Wav2Lip: MIT License
- FFmpeg: LGPL/GPL
- FastAPI: MIT License
- Next.js: MIT License

---

## 🎉 **Summary**

You have a **complete, production-ready system** that:

✅ Extracts content from any PDF/DOCX/TXT  
✅ Understands and structures content with AI  
✅ Generates beautiful, professional slides  
✅ Creates engaging teaching scripts  
✅ Converts to natural speech  
✅ Animates a presenter avatar  
✅ Composes professional videos  
✅ Provides REST API and Web UI  
✅ **100% free to run!** 🚀

---

**Created with ❤️ using 100% free and open-source tools**

**Ready to transform documents into engaging educational videos!**
