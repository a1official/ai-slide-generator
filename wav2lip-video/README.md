# Wav2Lip Video Processing Module

A comprehensive toolkit for video-to-video lip synchronization using Wav2Lip. This module provides easy-to-use scripts for processing single videos or batch processing multiple videos with customizable quality settings.

## 📁 Directory Structure

```
wav2lip-video/
├── config.py                 # Configuration and quality presets
├── utils.py                  # Utility functions for video/audio processing
├── video_inference.py        # Main video processing script
├── batch_process.py          # Batch processing script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── models/                   # Place Wav2Lip model checkpoints here
├── outputs/                  # Generated videos will be saved here
├── temp/                     # Temporary files during processing
└── examples/                 # Example scripts and configs
    ├── usage_examples.py     # Example usage code
    └── batch_config.json     # Example batch config
```

## 🚀 Features

- **Video-to-Video Lip Sync**: Process videos with audio to generate lip-synced output
- **Flexible Input**: Accept video or audio files as audio source
- **Quality Presets**: Low, medium, and high quality presets for different use cases
- **Batch Processing**: Process multiple videos efficiently
- **Custom Parameters**: Fine-tune processing with custom parameters
- **Progress Tracking**: Real-time progress bars and detailed logging
- **Error Handling**: Comprehensive error handling and validation
- **Automatic Audio Extraction**: Automatically extract audio from video files

## 📋 Prerequisites

1. **Wav2Lip Model Checkpoint**: Download the Wav2Lip model checkpoint
   - Place it in the `models/` directory
   - Recommended: `wav2lip_gan.pth` for best quality

2. **Python Dependencies**: Install required packages (see Installation)

3. **FFmpeg**: Required for audio/video processing
   - Install via: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)

## 🔧 Installation

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Download Wav2Lip checkpoint**:
```bash
# Download from the official repository or your checkpoint location
# Place in models/ directory
```

3. **Verify installation**:
```bash
python video_inference.py --help
```

## 📖 Usage

### Single Video Processing

**Basic usage**:
```bash
python video_inference.py \
  --checkpoint models/wav2lip_gan.pth \
  --face_video path/to/video.mp4 \
  --audio path/to/audio.wav \
  --output outputs/result.mp4
```

**With quality preset**:
```bash
python video_inference.py \
  --checkpoint models/wav2lip_gan.pth \
  --face_video path/to/video.mp4 \
  --audio path/to/audio.wav \
  --output outputs/result.mp4 \
  --quality high
```

**With custom parameters**:
```bash
python video_inference.py \
  --checkpoint models/wav2lip_gan.pth \
  --face_video path/to/video.mp4 \
  --audio path/to/audio.wav \
  --output outputs/result.mp4 \
  --resize_factor 2 \
  --face_det_batch_size 32 \
  --wav2lip_batch_size 256
```

**Video-to-Video (extract audio from video)**:
```bash
python video_inference.py \
  --checkpoint models/wav2lip_gan.pth \
  --face_video path/to/face_video.mp4 \
  --audio path/to/audio_video.mp4 \
  --output outputs/result.mp4
```

### Batch Processing

**From config file**:
```bash
python batch_process.py \
  --checkpoint models/wav2lip_gan.pth \
  --config examples/batch_config.json
```

**Process entire directory**:
```bash
python batch_process.py \
  --checkpoint models/wav2lip_gan.pth \
  --directory \
  --face_videos_dir path/to/videos \
  --audio_dir path/to/audio \
  --output_dir outputs/batch \
  --quality medium
```

### Python API

```python
from video_inference import Wav2LipVideoProcessor

# Create processor
processor = Wav2LipVideoProcessor('models/wav2lip_gan.pth')

# Process video
processor.process_video(
    face_video_path='path/to/video.mp4',
    audio_source_path='path/to/audio.wav',
    output_path='outputs/result.mp4',
    resize_factor=1,
    face_det_batch_size=16,
    wav2lip_batch_size=128
)
```

## ⚙️ Configuration

### Quality Presets

Three quality presets are available in `config.py`:

| Preset | Resolution | Speed | Quality | Use Case |
|--------|-----------|-------|---------|----------|
| **low** | 0.5x | Fast | Lower | Quick previews, testing |
| **medium** | 1x | Moderate | Good | General use, balanced |
| **high** | 1x | Slower | Best | Final output, production |

### Custom Parameters

Available parameters (see `config.py` for defaults):

- `resize_factor`: Reduce resolution (1 = original, 2 = half, etc.)
- `fps`: Override video FPS (None = use source FPS)
- `rotate`: Rotate video 90° clockwise
- `face_det_batch_size`: Batch size for face detection
- `wav2lip_batch_size`: Batch size for Wav2Lip model
- `pads`: Face padding [top, bottom, left, right]
- `crop`: Crop region [top, bottom, left, right]
- `nosmooth`: Disable face detection smoothing
- `box`: Manual bounding box [y1, y2, x1, x2]
- `output_quality`: FFmpeg quality (1 = best, 31 = worst)

### Batch Config File Format

Create a JSON file for batch processing:

```json
{
  "output_dir": "outputs/batch_results",
  "quality": "medium",
  "videos": [
    {
      "face_video": "videos/person1.mp4",
      "audio": "audio/speech1.wav",
      "output_name": "person1_lipsynced.mp4"
    },
    {
      "face_video": "videos/person2.mp4",
      "audio": "audio/speech2.wav",
      "output_name": "person2_lipsynced.mp4",
      "params": {
        "resize_factor": 1,
        "face_det_batch_size": 32
      }
    }
  ]
}
```

## 🎯 Tips for Best Results

1. **Video Quality**: Use high-quality input videos with clear, well-lit faces
2. **Face Visibility**: Ensure the face is visible in all frames
3. **Audio Quality**: Use clear audio without excessive noise
4. **Resolution**: For faster processing, use `resize_factor=2` for 720p/1080p videos
5. **Padding**: Adjust `pads` parameter to include the chin if it's being cut off
6. **Batch Size**: Increase batch sizes if you have sufficient GPU memory
7. **Multiple Faces**: Use `crop` parameter to focus on a specific face region

## 🐛 Troubleshooting

### Face Not Detected
- Ensure face is visible in all frames
- Try adjusting `pads` parameter: `--pads 10 20 10 10`
- Use `--resize_factor 1` to avoid over-compression
- Check `temp/faulty_frame.jpg` to see which frame failed

### Out of Memory
- Reduce batch sizes: `--face_det_batch_size 8 --wav2lip_batch_size 64`
- Use `--resize_factor 2` to reduce resolution
- Use quality preset: `--quality low`

### Poor Lip Sync Quality
- Use higher quality checkpoint (wav2lip_gan.pth)
- Ensure audio is clear and properly aligned
- Try `--quality high` preset
- Adjust `pads` to include more of the mouth region

### Audio/Video Out of Sync
- Check that source video FPS is correct
- Ensure audio file is not corrupted
- Try re-encoding audio to WAV format

## 📊 Performance

Approximate processing times (on NVIDIA RTX 3090):

| Resolution | Quality | FPS | Time (30s video) |
|-----------|---------|-----|------------------|
| 720p | Low | ~15 | ~2 min |
| 720p | Medium | ~10 | ~3 min |
| 720p | High | ~8 | ~4 min |
| 1080p | Medium | ~6 | ~5 min |

*Times vary based on hardware and video complexity*

## 🔗 Related Files

- **Original Wav2Lip**: `../ai-slide-generator/Wav2Lip/`
- **Model Checkpoints**: `../checkpoints/`
- **Examples**: `examples/usage_examples.py`

## 📝 License

This module uses Wav2Lip. Please refer to the original Wav2Lip repository for license information.

## 🤝 Contributing

Feel free to submit issues or pull requests for improvements!

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review example usage in `examples/usage_examples.py`
3. Check Wav2Lip documentation for model-specific issues

---

**Happy Lip Syncing! 🎬**
