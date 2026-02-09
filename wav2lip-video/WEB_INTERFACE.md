# Wav2Lip Web Interface 🎬

A beautiful, modern web interface for the Wav2Lip video processing module. Upload your video and audio files, select quality, and generate lip-synced videos directly from your browser!

## ✨ Features

- **Simple Upload**: Drag & drop or browse for video and audio files
- **Quality Presets**: Choose from Low, Medium, or High quality
- **Real-time Progress**: Visual progress tracking during processing
- **Video Preview**: Watch your generated video directly in the browser
- **Download**: Download your lip-synced videos instantly
- **Recent Outputs**: View and download all previously generated videos

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Model Checkpoint

Place your Wav2Lip model checkpoint at:
```
models/wav2lip_gan.pth
```

Or create a symlink to an existing checkpoint:
```bash
ln -s /path/to/your/wav2lip_gan.pth models/wav2lip_gan.pth
```

### 3. Start the Web Server

```bash
./start_web.sh
```

Or manually:
```bash
python3 app.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5000**

## 📖 Usage

1. **Upload Files**
   - Click "Browse" or drag & drop your video file
   - Click "Browse" or drag & drop your audio file
   - Supported formats:
     - Video: MP4, AVI, MOV, MKV, WebM
     - Audio: WAV, MP3, MP4, M4A, AAC

2. **Select Quality**
   - **Low**: Fast processing, lower quality (good for testing)
   - **Medium**: Balanced speed and quality (recommended)
   - **High**: Best quality, slower processing

3. **Generate**
   - Click "Generate Lip-Synced Video"
   - Wait for processing (progress shown in real-time)
   - Preview and download your result!

## 🎨 Interface Preview

The interface features:
- Modern dark theme with gradient accents
- Smooth animations and transitions
- Responsive design (works on mobile too!)
- Real-time progress tracking
- Video player for instant preview
- Recent outputs gallery

## 🔧 Configuration

### Port Configuration

Edit `app.py` to change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change 5000 to your port
```

### File Size Limit

Edit `app.py` to change max upload size:
```python
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
```

### Quality Presets

Quality presets are defined in `config.py`:
- Low: 0.5x resolution, faster processing
- Medium: 1x resolution, balanced
- High: 1x resolution, best quality

## 📁 Project Structure

```
wav2lip-video/
├── app.py                    # Flask application
├── templates/
│   └── index.html           # Web interface
├── static/
│   ├── css/
│   │   └── style.css        # Styling
│   └── js/
│       └── main.js          # JavaScript logic
├── uploads/                 # Uploaded files (auto-created)
├── outputs/                 # Generated videos
├── models/                  # Model checkpoints
└── start_web.sh            # Startup script
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Model Not Found
Make sure `wav2lip_gan.pth` is in the `models/` directory.

### Upload Fails
Check file size limits and ensure FFmpeg is installed:
```bash
brew install ffmpeg  # macOS
apt-get install ffmpeg  # Linux
```

### Processing Errors
- Ensure face is visible in all video frames
- Check that audio file is valid
- Try using a lower quality preset

## 🌐 API Endpoints

The web interface uses these endpoints:

- `GET /` - Main interface
- `POST /upload` - Upload video and audio files
- `POST /process` - Process uploaded files
- `GET /download/<filename>` - Download processed video
- `GET /view/<filename>` - View processed video
- `GET /outputs` - List all processed videos
- `GET /health` - Health check

## 💡 Tips

1. **First Time**: Start with Low quality to test the setup
2. **Best Results**: Use high-quality input videos with clear faces
3. **Performance**: High quality takes longer but produces better results
4. **Storage**: Processed videos are saved in `outputs/` directory
5. **Cleanup**: Periodically clean `uploads/` and `outputs/` folders

## 🔒 Security Notes

This is a development server. For production:
- Use a production WSGI server (gunicorn, uWSGI)
- Add authentication
- Implement file size validation
- Add rate limiting
- Use HTTPS

## 📝 License

Part of the Wav2Lip Video Processing Module

---

**Enjoy creating lip-synced videos! 🎥✨**
