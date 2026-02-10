"""
Utility functions for Wav2Lip video processing
"""
import os
import cv2
import numpy as np
import subprocess
import shutil
from typing import List, Tuple, Optional

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"


def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """
    Extract audio from video file and save as WAV
    
    Args:
        video_path: Path to input video
        output_audio_path: Path to save extracted audio
        
    Returns:
        True if successful, False otherwise
    """
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
    command = f'"{FFMPEG_PATH}" -y -i "{video_path}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{output_audio_path}"'
    
    print(f"Extracting audio: {command}")
    ret = subprocess.call(command, shell=True)
    
    if ret != 0:
        print(f"Warning: FFmpeg audio extraction failed with code {ret}")
        return False
    return True


def load_video_frames(video_path: str, 
                     resize_factor: int = 1,
                     rotate: bool = False,
                     crop: List[int] = [0, -1, 0, -1]) -> Tuple[List[np.ndarray], float]:
    """
    Load all frames from a video file
    
    Args:
        video_path: Path to video file
        resize_factor: Factor to resize frames (1 = no resize)
        rotate: Whether to rotate frames 90 degrees clockwise
        crop: Crop region [top, bottom, left, right]
        
    Returns:
        Tuple of (list of frames, fps)
    """
    video_stream = cv2.VideoCapture(video_path)
    fps = video_stream.get(cv2.CAP_PROP_FPS)
    
    print(f'Reading video frames from {video_path}...')
    print(f'Video FPS: {fps}')
    
    frames = []
    frame_count = 0
    
    while True:
        still_reading, frame = video_stream.read()
        if not still_reading:
            video_stream.release()
            break
            
        # Resize if needed
        if resize_factor > 1:
            new_width = frame.shape[1] // resize_factor
            new_height = frame.shape[0] // resize_factor
            frame = cv2.resize(frame, (new_width, new_height))
        
        # Rotate if needed
        if rotate:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        # Crop if needed
        y1, y2, x1, x2 = crop
        if x2 == -1:
            x2 = frame.shape[1]
        if y2 == -1:
            y2 = frame.shape[0]
        frame = frame[y1:y2, x1:x2]
        
        frames.append(frame)
        frame_count += 1
    
    print(f"Loaded {frame_count} frames")
    return frames, fps


def get_smoothened_boxes(boxes: np.ndarray, T: int = 5) -> np.ndarray:
    """
    Smooth bounding boxes over a temporal window
    
    Args:
        boxes: Array of bounding boxes
        T: Temporal window size
        
    Returns:
        Smoothed bounding boxes
    """
    for i in range(len(boxes)):
        if i + T > len(boxes):
            window = boxes[len(boxes) - T:]
        else:
            window = boxes[i : i + T]
        boxes[i] = np.mean(window, axis=0)
    return boxes


def merge_audio_video(video_path: str, audio_path: str, output_path: str, quality: int = 1) -> bool:
    """
    Merge audio and video files using FFmpeg with HD quality settings
    
    Args:
        video_path: Path to video file
        audio_path: Path to audio file
        output_path: Path to save output
        quality: Output quality (1 = best, 31 = worst)
        
    Returns:
        True if successful, False otherwise
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # HD Quality FFmpeg settings
    # -c:v libx264: Use H.264 codec (better quality than default)
    # -preset slow: Better compression (slower but higher quality)
    # -crf 18: Constant Rate Factor (18 = visually lossless, 23 = default)
    # -pix_fmt yuv420p: Pixel format for compatibility
    # -c:a aac: AAC audio codec
    # -b:a 192k: Audio bitrate
    command = (
        f'"{FFMPEG_PATH}" -y '
        f'-i "{audio_path}" '
        f'-i "{video_path}" '
        f'-c:v libx264 '
        f'-preset slow '
        f'-crf 18 '
        f'-pix_fmt yuv420p '
        f'-c:a aac '
        f'-b:a 192k '
        f'-movflags +faststart '
        f'"{output_path}"'
    )
    
    print(f"Merging audio and video with HD settings...")
    ret = subprocess.call(command, shell=True)
    
    if ret != 0:
        print(f"Warning: FFmpeg merge failed with code {ret}")
        return False
    return True


def validate_video_file(video_path: str) -> bool:
    """
    Validate that a video file exists and can be opened
    
    Args:
        video_path: Path to video file
        
    Returns:
        True if valid, False otherwise
    """
    if not os.path.isfile(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False
    
    # Try to open with OpenCV
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file: {video_path}")
        return False
    
    # Check if we can read at least one frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"Error: Cannot read frames from video: {video_path}")
        return False
    
    return True


def validate_audio_file(audio_path: str) -> bool:
    """
    Validate that an audio file exists
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        True if valid, False otherwise
    """
    if not os.path.isfile(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        return False
    return True


def get_video_info(video_path: str) -> dict:
    """
    Get information about a video file
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video information
    """
    cap = cv2.VideoCapture(video_path)
    
    info = {
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
    }
    
    cap.release()
    return info


def create_video_writer(output_path: str, fps: float, frame_size: Tuple[int, int], codec: str = 'DIVX') -> cv2.VideoWriter:
    """
    Create a video writer object
    
    Args:
        output_path: Path to save video
        fps: Frames per second
        frame_size: (width, height) of frames
        codec: Video codec fourcc code
        
    Returns:
        VideoWriter object
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*codec)
    return cv2.VideoWriter(output_path, fourcc, fps, frame_size)


def cleanup_temp_files(temp_dir: str, keep_patterns: Optional[List[str]] = None):
    """
    Clean up temporary files
    
    Args:
        temp_dir: Directory containing temporary files
        keep_patterns: List of filename patterns to keep (optional)
    """
    if not os.path.exists(temp_dir):
        return
    
    for filename in os.listdir(temp_dir):
        filepath = os.path.join(temp_dir, filename)
        
        # Check if we should keep this file
        if keep_patterns:
            should_keep = any(pattern in filename for pattern in keep_patterns)
            if should_keep:
                continue
        
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
                print(f"Removed temp file: {filename}")
        except Exception as e:
            print(f"Error removing {filename}: {e}")
