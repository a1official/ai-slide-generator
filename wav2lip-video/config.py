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
    'resize_factor': 1,  # Reduce resolution by this factor (1 = no resize)
    'fps': None,  # Use source video FPS if None
    'rotate': False,  # Rotate video 90 degrees clockwise
    
    # Face detection
    'face_det_batch_size': 16,
    'pads': [0, 10, 0, 0],  # Padding (top, bottom, left, right)
    'nosmooth': False,  # Enable face detection smoothing
    'box': [-1, -1, -1, -1],  # Manual bounding box (disabled by default)
    
    # Cropping
    'crop': [0, -1, 0, -1],  # Crop region (top, bottom, left, right)
    
    # Wav2Lip model
    'wav2lip_batch_size': 128,
    'img_size': 96,
    
    # Audio
    'sample_rate': 16000,
    'mel_step_size': 16,
    
    # Output
    'output_quality': 1,  # FFmpeg quality (1 = best, 31 = worst)
    'output_codec': 'DIVX',  # Video codec for intermediate file
}

# Quality presets
QUALITY_PRESETS = {
    'low': {
        'resize_factor': 2,
        'face_det_batch_size': 8,
        'wav2lip_batch_size': 64,
        'output_quality': 10,
    },
    'medium': {
        'resize_factor': 1,
        'face_det_batch_size': 16,
        'wav2lip_batch_size': 128,
        'output_quality': 5,
    },
    'high': {
        'resize_factor': 1,
        'face_det_batch_size': 32,
        'wav2lip_batch_size': 128,
        'output_quality': 1,
    },
}

# Device configuration
DEVICE = 'cuda'  # Will auto-detect in code

# Create necessary directories
for directory in [MODELS_DIR, OUTPUTS_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)
