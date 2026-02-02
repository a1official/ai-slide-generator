"""
Avatar Agent
Responsibility: Generate lip-synced talking head using Wav2Lip (Local & FREE)
"""

import subprocess
import os
from typing import List, Dict, Any
from pathlib import Path
import shutil
import json
import time
import boto3
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv


class AvatarAgent:
    """Generates lip-synced talking avatar using Wav2Lip"""
    
    def __init__(self, output_dir: str = "./outputs/avatars"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Wav2Lip configuration
        self.wav2lip_path = Path(os.getenv("WAV2LIP_PATH", "./Wav2Lip")).absolute()
        self.checkpoint_path = (self.wav2lip_path / os.getenv("WAV2LIP_CHECKPOINT", "checkpoints/wav2lip_gan.pth")).absolute()

        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.endpoint_name = os.getenv("SAGEMAKER_ENDPOINT_NAME")
        
        # Bedrock/AWS config
        self.sagemaker_client = boto3.client(
            service_name="sagemaker-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.s3_client = boto3.client(
            service_name="s3",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

        self._sagemaker_unavailable = False  # Track if SageMaker fails for this session
        
        # Only verify local installation if we don't have a SageMaker endpoint configured
        # Or if the user explicitly wants to use 'local'
        if not self.endpoint_name:
            try:
                self._verify_installation()
            except Exception as e:
                print(f"  ⚠ Local Wav2Lip not fully configured: {e}")
                print("  💡 Pipeline will require AWS SageMaker for avatar generation.")
    
    def _verify_installation(self):
        """Verify Wav2Lip is properly installed"""
        if not self.wav2lip_path.exists():
            raise FileNotFoundError(
                f"Wav2Lip not found at {self.wav2lip_path}. "
                "Please run: git clone https://github.com/Rudrabha/Wav2Lip.git"
            )
        
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(
                f"Wav2Lip checkpoint not found at {self.checkpoint_path}. "
                "Please download from: https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth"
            )
            
        # Also check for face detection model (common issue)
        face_detector_pth = self.wav2lip_path / "face_detection" / "detection" / "sfd" / "s3fd.pth"
        if not face_detector_pth.exists():
            print(f"  ⚠ Face detector model missing: {face_detector_pth}")
            print("  💡 It will attempt to download on first run, which might be slow.")
    
    def generate_avatars(
        self, 
        audio_files: List[Dict[str, Any]], 
        face_image: str,
        provider: str = "local"
    ) -> List[Dict[str, Any]]:
        """
        Generate lip-synced avatar videos for all audio files
        
        Args:
            audio_files: Output from TTSAgent
            face_image: Path to presenter's face image (JPG/PNG)
            
        Returns:
            [
                {
                    "slide_id": 1,
                    "audio_path": "...",
                    "avatar_video": "outputs/avatars/avatar_001.mp4",
                    "duration": 18.4
                }
            ]
        """
        face_image = Path(face_image)
        
        if not face_image.exists():
            raise FileNotFoundError(f"Face image not found: {face_image}")
        
        results = []
        is_aws = provider in ["bedrock", "aws", "amazon_bedrock"]
        
        # Only use SageMaker if we are in AWS mode AND an endpoint is actually configured
        if is_aws and self.endpoint_name:
            print("\n" + "="*60)
            print("🌩️  SHIFTING TO AWS SAGEMAKER (Avatar Generation)")
            print("="*60)
            print(f"[*] Endpoint: {self.endpoint_name}")
            print(f"[*] Bucket: {self.s3_bucket}")
            print("="*60 + "\n")
            
            for audio_data in audio_files:
                if not self._sagemaker_unavailable:
                    try:
                        result = self._generate_with_sagemaker(audio_data, face_image)
                        results.append(result)
                        continue # Success, move to next audio file
                    except Exception as e:
                        print(f"  [-] SageMaker failed: {e}. Falling back to local.")
                        if "not found" in str(e).lower() or "validationerror" in str(e).lower():
                            print("  💡 Endpoint not found. Disabling SageMaker for this run.")
                            self._sagemaker_unavailable = True
                
                # Default to local if SageMaker failed or is known to be unavailable
                result = self._generate_single_avatar(audio_data, face_image)
                results.append(result)
        else:
            if is_aws:
                print("\n" + "-"*60)
                print("💻 AWS Provider active, but no SageMaker Endpoint found.")
                print("💻 Falling back to LOCAL AVATAR GENERATION (Wav2Lip)")
                print("-"*60 + "\n")
            else:
                print("\n" + "-"*60)
                print("💻 LOCAL AVATAR GENERATION (Wav2Lip)")
                print("-"*60 + "\n")
            
            # Verify local setup explicitly before starting local batch
            self._verify_installation()
            
            for audio_data in audio_files:
                result = self._generate_single_avatar(audio_data, face_image)
                results.append(result)
        
        return results

    def _generate_with_sagemaker(self, audio_data: Dict[str, Any], face_image: Path) -> Dict[str, Any]:
        """Generate avatar using AWS SageMaker Endpoint"""
        slide_id = audio_data["slide_id"]
        audio_path = Path(audio_data["audio_path"])
        output_filename = f"avatar_{slide_id:03d}.mp4"
        output_path = self.output_dir / output_filename

        if not self.s3_bucket:
            raise Exception("S3_BUCKET_NAME is required for SageMaker avatar generation")

        # 1. Upload assets to S3
        print(f"[*] [Slide {slide_id}] Uploading assets to S3...")
        s3_face_key = f"avatars/inputs/face_{slide_id}.jpg"
        s3_audio_key = f"avatars/inputs/audio_{slide_id}.mp3"
        s3_output_key = f"avatars/outputs/{output_filename}"

        self.s3_client.upload_file(str(face_image), self.s3_bucket, s3_face_key)
        self.s3_client.upload_file(str(audio_path), self.s3_bucket, s3_audio_key)

        # 2. Invoke SageMaker Endpoint
        payload = {
            "face_s3": f"s3://{self.s3_bucket}/{s3_face_key}",
            "audio_s3": f"s3://{self.s3_bucket}/{s3_audio_key}",
            "output_s3": f"s3://{self.s3_bucket}/{s3_output_key}"
        }

        print(f"[*] [Slide {slide_id}] Invoking SageMaker Endpoint: {self.endpoint_name}...")
        import json
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload)
        )

        # 3. Wait/Download result from S3
        print(f"[*] [Slide {slide_id}] Waiting for animation...")
        max_retries = 60 # Increased to 10 minutes max for long scripts
        found = False
        for i in range(max_retries):
            try:
                self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_output_key)
                print(f"  ✓ Animation complete! Downloading...")
                self.s3_client.download_file(self.s3_bucket, s3_output_key, str(output_path))
                found = True
                break
            except Exception:
                if i % 10 == 0: print(f"    ... pooling S3 for result ({i*5}s)")
                time.sleep(5)
        
        if not found:
            raise Exception(f"SageMaker timed out while generating avatar for slide {slide_id}")
            
        return {
            "slide_id": slide_id,
            "audio_path": str(audio_path),
            "avatar_video": str(output_path),
            "duration": audio_data.get("duration", 0)
        }
    
    def _generate_single_avatar(
        self, 
        audio_data: Dict[str, Any], 
        face_image: Path
    ) -> Dict[str, Any]:
        """Generate avatar for a single audio file using Wav2Lip"""
        
        slide_id = audio_data["slide_id"]
        audio_path = Path(audio_data["audio_path"])
        
        # Output path
        output_filename = f"avatar_{slide_id:03d}.mp4"
        output_path = self.output_dir / output_filename
        
        # Wav2Lip inference script (absolute)
        inference_script = (self.wav2lip_path / "inference.py").absolute()
        
        # Ensure image and audio are absolute for the subprocess
        face_image_abs = face_image.absolute()
        audio_path_abs = audio_path.absolute()
        output_path_abs = output_path.absolute()
        
        # Build command
        import sys
        
        # Add FFmpeg to path if possible (to help librosa/audioread)
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        env = os.environ.copy()
        if ffmpeg_path:
            ffmpeg_dir = str(Path(ffmpeg_path).parent)
            if ffmpeg_dir not in env.get("PATH", ""):
                env["PATH"] = f"{ffmpeg_dir};" + env.get("PATH", "")

        cmd = [
            sys.executable,
            "inference.py",
            "--checkpoint_path", str(self.checkpoint_path),
            "--face", str(face_image_abs),
            "--audio", str(audio_path_abs),
            "--outfile", str(output_path_abs),
            "--resize_factor", "1",
            "--wav2lip_batch_size", "16",
            "--nosmooth"
        ]
        
        try:
            # Run Wav2Lip
            print(f"Generating avatar for slide {slide_id}...")
            
            result = subprocess.run(
                cmd,
                cwd=str(inference_script.parent),
                capture_output=True,
                text=True,
                env=env,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"Wav2Lip failed: {result.stderr}")
            
            if not output_path.exists():
                raise FileNotFoundError(f"Output video not created: {output_path}")
            
            print(f"✓ Avatar generated for slide {slide_id}")
            
            return {
                "slide_id": slide_id,
                "audio_path": str(audio_path),
                "avatar_video": str(output_path),
                "duration": audio_data.get("duration", 0)
            }
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Wav2Lip timed out for slide {slide_id}")
        except Exception as e:
            raise Exception(f"Error generating avatar for slide {slide_id}: {str(e)}")
    
    def check_gpu_available(self) -> bool:
        """Check if CUDA GPU is available for faster processing"""
        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


# Example usage
if __name__ == "__main__":
    agent = AvatarAgent()
    
    # Check GPU
    has_gpu = agent.check_gpu_available()
    print(f"GPU Available: {has_gpu}")
    
    sample_audio = [
        {
            "slide_id": 1,
            "audio_path": "outputs/audio/slide_001.mp3",
            "duration": 18.4
        }
    ]
    
    # avatar_videos = agent.generate_avatars(sample_audio, "presenter.jpg")
    # print(avatar_videos)
