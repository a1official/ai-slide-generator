"""
Configuration file for Wav2Lip video processing
"""
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

# Model paths
WAV2LIP_CHECKPOINT = os.path.join(MODELS_DIR, 'wav2lip_gan.pth')
FACE_DETECTION_MODEL = 'face_detection'

# Default processing parameters
DEFAULT_PARAMS = {
    # Video processing
    'resize_factor': 1,  # Keep original resolution (1 = no resize)
    'fps': None,  # Use source video FPS if None
    'rotate': False,  # Rotate video 90 degrees clockwise
    
    # Face detection - QUALITY IMPROVEMENTS
    'face_det_batch_size': 16,
    'pads': [0, 20, 0, 0],  # Increased bottom padding for better chin/neck quality
    'nosmooth': False,  # Enable face detection smoothing
    'box': [-1, -1, -1, -1],  # Manual bounding box (disabled by default)
    'static': False,  # OPTIMIZATION: Detect face once and reuse (100x-1000x faster!)
    'detect_every_n': 1,  # OPTIMIZATION: Detect every N frames (1 = all frames)
    
    # Cropping
    'crop': [0, -1, 0, -1],  # Crop region (top, bottom, left, right)
    
    # Wav2Lip model
    'wav2lip_batch_size': 128,
    'img_size': 96,  # Wav2Lip model requires 96x96 (fixed by architecture)
    
    # Audio
    'sample_rate': 16000,
    'mel_step_size': 16,
    
    # Output - QUALITY IMPROVEMENTS
    'output_quality': 1,  # FFmpeg quality (1 = best, 31 = worst)
    'output_codec': 'DIVX',  # Video codec for intermediate file
}

# Quality presets
QUALITY_PRESETS = {
    'low': {
        'resize_factor': 2,
        'face_det_batch_size': 8,
        'wav2lip_batch_size': 64,
        'output_quality': 15,  # Lower quality for speed
        'static': True,  # Enable optimization
    },
    'medium': {
        'resize_factor': 1,
        'face_det_batch_size': 16,
        'wav2lip_batch_size': 128,
        'output_quality': 3,  # Good quality
        'static': True,  # Enable optimization
    },
    'high': {
        'resize_factor': 1,
        'face_det_batch_size': 32,
        'wav2lip_batch_size': 128,
        'output_quality': 1,  # Best quality
        'static': True,  # Enable optimization
    },
}

# Device configuration
DEVICE = 'cuda'  # Will auto-detect in code

# Create necessary directories
for directory in [MODELS_DIR, OUTPUTS_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)
