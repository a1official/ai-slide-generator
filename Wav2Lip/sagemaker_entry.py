import os
import torch
import json
import base64
import subprocess
import shutil
from pathlib import Path
import numpy as np
import cv2

# Set up paths relative to the model directory
MODEL_DIR = "/opt/ml/model"
WAV2LIP_PATH = Path(MODEL_DIR)
CHECKPOINT_PATH = WAV2LIP_PATH / "checkpoints" / "wav2lip_gan.pth"

def model_fn(model_dir):
    """Load the model (not actually used since we run a subprocess, but required by SageMaker)"""
    return {"loaded": True}

def input_fn(request_body, request_content_type):
    """Parse input request"""
    if request_content_type == "application/json":
        return json.loads(request_body)
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """Run lip-sync inference using a subprocess call to Wav2Lip's inference.py"""
    
    # Extract S3 paths from input_data
    face_s3 = input_data.get("face_s3")
    audio_s3 = input_data.get("audio_s3")
    output_s3 = input_data.get("output_s3")
    
    if not all([face_s3, audio_s3, output_s3]):
        raise ValueError("Missing required S3 paths: face_s3, audio_s3, output_s3")
        
    # Set up temporary working directory
    tmp_dir = Path("/tmp/wav2lip")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    local_face = tmp_dir / "face.jpg"
    local_audio = tmp_dir / "audio.mp3"
    local_output = tmp_dir / "output.mp4"
    
    import boto3
    s3 = boto3.client("s3")
    
    # Helper to parse s3://bucket/key
    def parse_s3(uri):
        parts = uri.replace("s3://", "").split("/", 1)
        return parts[0], parts[1]

    # 1. Download assets
    print(f"Downloading {face_s3}...")
    b, k = parse_s3(face_s3)
    s3.download_file(b, k, str(local_face))
    
    print(f"Downloading {audio_s3}...")
    b, k = parse_s3(audio_s3)
    s3.download_file(b, k, str(local_audio))
    
    # 2. Run inference.py locally
    print("Starting Wav2Lip inference...")
    inference_script = WAV2LIP_PATH / "inference.py"
    
    cmd = [
        "python3",
        str(inference_script),
        "--checkpoint_path", str(CHECKPOINT_PATH),
        "--face", str(local_face),
        "--audio", str(local_audio),
        "--outfile", str(local_output),
        "--resize_factor", "1",
        "--nosmooth"
    ]
    
    result = subprocess.run(cmd, cwd=str(WAV2LIP_PATH), capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Inference failed: {result.stderr}")
        return {"error": result.stderr}
        
    # 3. Upload result to S3
    print(f"Uploading result to {output_s3}...")
    b, k = parse_s3(output_s3)
    s3.upload_file(str(local_output), b, k)
    
    return {"status": "success", "output_s3": output_s3}

def output_fn(prediction, content_type):
    """Return response"""
    return json.dumps(prediction)
