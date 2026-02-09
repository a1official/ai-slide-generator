"""
Video Composition Agent
Responsibility: Assemble final video with slides, avatar, and audio
"""

from moviepy.editor import (
    ImageClip, VideoFileClip, AudioFileClip, 
    CompositeVideoClip, concatenate_videoclips
)
from typing import List, Dict, Any
from pathlib import Path
import os
import asyncio
import json


class VideoCompositionAgent:
    """Composes final educational video with all elements"""
    def __init__(self, output_dir: str = "./outputs/videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.width = 1920
        self.height = 1080
        self.fps = 30
        
        # Avatar settings
        self.avatar_size = 300
        self.avatar_margin = 50
        
        # AWS Clients
        import boto3
        self.s3_client = boto3.client(
            service_name="s3",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.mc_client = boto3.client(
            service_name="mediaconvert",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.mc_role_arn = os.getenv("MEDIACONVERT_ROLE_ARN")
        self._mc_endpoint = None
    
    async def compose_video(
        self,
        slides: List[Dict[str, Any]],
        audio_files: List[Dict[str, Any]],
        avatar_videos: List[Dict[str, Any]],
        output_filename: str = "final_video.mp4",
        provider: str = "local"
    ) -> str:
        """
        Compose final video
        
        Args:
            slides: Output from SlideGenerationAgent
            audio_files: Output from TTSAgent
            avatar_videos: Output from AvatarAgent
            output_filename: Name of output video
            provider: Cloud provider
            
        Returns:
            Path to final video file
        """
        
        # Get corresponding audio and avatar
        audio_map = {a["slide_id"]: a for a in audio_files}
        avatar_map = {a["slide_id"]: a for a in avatar_videos}
        
        # Check if we should use AWS MediaConvert (Cloud Rendering)
        is_aws = provider in ["bedrock", "aws", "amazon_bedrock"]
        
        if is_aws and self.s3_bucket and self.mc_role_arn:
            print("\n" + "="*60)
            print("🌩️  SHIFTING TO AWS MEDIACONVERT (Cloud Rendering)")
            print("="*60)
            print("[*] Status: Full Cloud Pipeline Active")
            print("[*] Agent: Video Composition Agent -> AWS MediaConvert")
            print(f"[*] Bucket: {self.s3_bucket}")
            print("="*60 + "\n")
            
            # Replaced try/except with direct call to prevent hidden local fallback
            return await self._compose_with_mediaconvert(
                slides, audio_map, avatar_map, output_filename
            )
        
        # Use FFmpeg-based composition (fast local)
        print("[*] Using FFmpeg for fast video composition...")
        try:
            return await self._compose_with_ffmpeg(
                slides, audio_map, avatar_map, output_filename, upload_to_s3=is_aws
            )
        except Exception as e:
            print(f"[!] FFmpeg composition failed: {e}")
            print("[*] Falling back to MoviePy composition...")
            return self._compose_local(slides, audio_map, avatar_map, output_filename)

    async def _compose_with_ffmpeg(
        self, slides, audio_map, avatar_map, output_filename, upload_to_s3=False
    ) -> str:
        """
        Fast video composition using FFmpeg concat
        10-20x faster than MoviePy, with optional S3 upload for cloud storage
        """
        import subprocess
        import tempfile
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        print("[1/3] Creating individual slide clips with FFmpeg...")
        slide_video_paths = []
        
        for i, slide in enumerate(slides, 1):
            slide_id = slide["slide_id"]
            audio = audio_map.get(slide_id)
            avatar = avatar_map.get(slide_id)
            if not audio:
                continue
            
            print(f"  [{i}/{len(slides)}] Encoding slide {slide_id}...")
            
            # Get paths
            image_path = slide["image_path"]
            audio_path = audio["audio_path"]
            temp_path = self.output_dir / f"temp_slide_{slide_id:03d}.mp4"
            
            # Get audio duration
            from mutagen.mp3 import MP3
            try:
                audio_file = MP3(audio_path)
                duration = audio_file.info.length
            except:
                duration = 5.0  # Default fallback
            
            # Check if avatar exists
            avatar = avatar_map.get(slide_id)
            has_avatar = avatar and Path(avatar["avatar_video"]).exists()
            
            if has_avatar:
                avatar_path = avatar["avatar_video"]
                # Position calculation
                x_pos = self.width - self.avatar_size - self.avatar_margin
                y_pos = self.height - self.avatar_size - self.avatar_margin
                
                # Filter notes: 
                # [1:v] is avatar. scale it.
                # [0:v] is slide image.
                # Use shortest=1 in overlay to match audio/image length
                filter_complex = (
                    f"[1:v]scale={self.avatar_size}:{self.avatar_size}[av]; "
                    f"[0:v][av]overlay={x_pos}:{y_pos}:shortest=1"
                )
                
                ffmpeg_cmd = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-framerate', '25', '-i', str(image_path),
                    '-stream_loop', '-1', '-i', str(avatar_path), # Loop avatar if shorter
                    '-i', str(audio_path),
                    '-filter_complex', filter_complex,
                    '-c:v', 'libx264',
                    '-profile:v', 'high',
                    '-level', '4.0',
                    '-pix_fmt', 'yuv420p',
                    '-r', '25',
                    '-tune', 'stillimage',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-ar', '48000',
                    '-ac', '2',
                    '-shortest',
                    '-t', str(duration),
                    '-movflags', '+faststart',
                    '-preset', 'fast',
                    str(temp_path)
                ]
            else:
                # Original logic for image + audio only
                ffmpeg_cmd = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-framerate', '25', '-i', str(image_path),
                    '-i', str(audio_path),
                    '-c:v', 'libx264',
                    '-profile:v', 'high',
                    '-level', '4.0',
                    '-pix_fmt', 'yuv420p',
                    '-r', '25',
                    '-tune', 'stillimage',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-ar', '48000',
                    '-ac', '2',
                    '-shortest',
                    '-t', str(duration),
                    '-movflags', '+faststart',
                    '-preset', 'fast',
                    str(temp_path)
                ]
            
            # Run FFmpeg
            try:
                result = subprocess.run(
                    ffmpeg_cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    check=True,
                    text=True
                )
                slide_video_paths.append(str(temp_path))
            except subprocess.CalledProcessError as e:
                print(f"  ✗ FFmpeg error for slide {slide_id}: {e.stderr[:200]}")
                raise
        
        print(f"[OK] Created {len(slide_video_paths)} slide videos")
        
        # 2. Concatenate all videos using FFmpeg (re-encode for reliability)
        print("[2/3] Concatenating videos with FFmpeg...")
        
        # Output path
        output_path = self.output_dir / output_filename
        
        # Build FFmpeg concat command using filter_complex (more reliable than concat demuxer)
        # This method works better with heterogeneous inputs
        if len(slide_video_paths) == 1:
            # Single video, just copy
            concat_cmd = [
                ffmpeg_exe, '-y',
                '-i', slide_video_paths[0],
                '-c', 'copy',
                str(output_path)
            ]
        else:
            # Multiple videos - use filter_complex concat
            # Build input arguments
            input_args = []
            for video_path in slide_video_paths:
                input_args.extend(['-i', video_path])
            
            # Build filter_complex argument
            # Format: [0:v][0:a][1:v][1:a]...[N:v][N:a]concat=n=N:v=1:a=1[outv][outa]
            filter_parts = []
            for i in range(len(slide_video_paths)):
                filter_parts.append(f'[{i}:v][{i}:a]')
            filter_str = f"{''.join(filter_parts)}concat=n={len(slide_video_paths)}:v=1:a=1[outv][outa]"
            
            concat_cmd = [
                ffmpeg_exe, '-y',
                *input_args,
                '-filter_complex', filter_str,
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-c:a', 'aac',
                str(output_path)
            ]
        
        try:
            result = subprocess.run(
                concat_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            print(f"[OK] Video concatenation complete!")
        except subprocess.CalledProcessError as e:
            print(f"[-] FFmpeg concat failed!")
            print(f"    Error: {e.stderr[:500]}")
            print("[-] Falling back to MoviePy composition...")
            return self._compose_local(slides, audio_map, avatar_map, output_filename)
        
        # 3. Optional: Upload to S3 for cloud storage
        if upload_to_s3:
            print("[3/3] Uploading final video to S3...")
            try:
                s3_key = f"videos/{output_filename}"
                self.s3_client.upload_file(str(output_path), self.s3_bucket, s3_key)
                print(f"[OK] Uploaded to s3://{self.s3_bucket}/{s3_key}")
            except Exception as e:
                print(f"[!] S3 upload failed (video saved locally): {e}")
        
        # Cleanup temp files
        print("[*] Cleaning up temporary files...")
        for temp_path in slide_video_paths:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass
        print(f"[OK] ✓ Video composition complete: {output_path}")
        print(f"     Using FFmpeg filter_complex (reliable and fast!)")
        return str(output_path)
    
    async def _compose_with_mediaconvert(
        self, slides, audio_map, avatar_map, output_filename
    ) -> str:
        """
        Full cloud video composition using AWS MediaConvert
        """
        import time
        import asyncio
        from pathlib import Path
        
        # 1. Get regional endpoint
        endpoint = await self._get_mc_endpoint()
        
        # 2. Upload assets to S3 and prepare MediaConvert inputs
        print("[1/4] Uploading assets to S3 for cloud composition...")
        inputs = []
        for slide in slides:
            slide_id = slide["slide_id"]
            audio = audio_map.get(slide_id)
            if not audio: continue
            
            # Define local segment path
            local_segment = self.output_dir / f"segment_{slide_id:03d}.mp4"
            
            # Check if avatar exists
            avatar = avatar_map.get(slide_id)
            has_avatar = avatar and Path(avatar["avatar_video"]).exists()
            
            import subprocess
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            if has_avatar:
                avatar_path = avatar["avatar_video"]
                x_pos = self.width - self.avatar_size - self.avatar_margin
                y_pos = self.height - self.avatar_size - self.avatar_margin
                
                filter_complex = (
                    f"[1:v]scale={self.avatar_size}:{self.avatar_size}[av]; "
                    f"[0:v][av]overlay={x_pos}:{y_pos}:shortest=1"
                )
                
                cmd = [
                    ffmpeg_exe, '-y', '-loop', '1', '-i', slide["image_path"],
                    '-stream_loop', '-1', '-i', str(avatar_path),
                    '-i', audio["audio_path"], 
                    '-filter_complex', filter_complex,
                    '-c:v', 'libx264', '-t', str(audio["duration"]),
                    '-pix_fmt', 'yuv420p', '-shortest', str(local_segment)
                ]
            else:
                cmd = [
                    ffmpeg_exe, '-y', '-loop', '1', '-i', slide["image_path"],
                    '-i', audio["audio_path"], '-c:v', 'libx264', '-t', str(audio["duration"]),
                    '-pix_fmt', 'yuv420p', '-shortest', str(local_segment)
                ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Upload segment to S3
            s3_key = f"segments/{Path(local_segment).name}"
            self.s3_client.upload_file(str(local_segment), self.s3_bucket, s3_key)
            s3_path = f"s3://{self.s3_bucket}/{s3_key}"
            
            inputs.append({
                "AudioSelectors": {"Audio Selector 1": {"DefaultSelection": "DEFAULT"}},
                "VideoSelector": {},
                "FileInput": s3_path
            })
            
            # Cleanup local segment
            local_segment.unlink()

        # 3. Create MediaConvert Job
        print(f"[2/4] Submitting cloud rendering job to AWS MediaConvert...")
        output_s3_prefix = f"s3://{self.s3_bucket}/outputs/"
        
        job_settings = {
            "Role": self.mc_role_arn,
            "Settings": {
                "Inputs": inputs,
                "OutputGroups": [
                    {
                        "Name": "File Group",
                        "OutputGroupSettings": {
                            "Type": "FILE_GROUP_SETTINGS",
                            "FileGroupSettings": {"Destination": output_s3_prefix}
                        },
                        "Outputs": [
                            {
                                "VideoDescription": {
                                    "CodecSettings": {
                                        "Codec": "H_264",
                                        "H264Settings": {
                                            "Bitrate": 5000000,
                                            "RateControlMode": "CBR",
                                            "QualityTuningLevel": "SINGLE_PASS_HQ",
                                            "FramerateControl": "SPECIFIED",
                                            "FramerateNumerator": 30,
                                            "FramerateDenominator": 1,
                                            "GopSize": 60,
                                            "GopSizeUnits": "FRAMES",
                                            "SceneChangeDetect": "ENABLED",
                                            "InterlaceMode": "PROGRESSIVE"
                                        }
                                    }
                                },
                                "AudioDescriptions": [
                                    {
                                        "CodecSettings": {
                                            "Codec": "AAC",
                                            "AacSettings": {
                                                "Bitrate": 128000, 
                                                "SampleRate": 48000,
                                                "CodingMode": "CODING_MODE_2_0"
                                            }
                                        }
                                    }
                                ],
                                "ContainerSettings": {"Container": "MP4"},
                                "NameModifier": output_filename.split('.')[0]
                            }
                        ]
                    }
                ]
            }
        }
        
        response = self.mc_client.create_job(**job_settings)
        job_id = response["Job"]["Id"]
        print(f"  ✓ Job created: {job_id}")
        
        # 4. Wait for job completion
        print("[3/4] Waiting for cloud rendering to complete...")
        final_s3_uri = None
        while True:
            job_status = self.mc_client.get_job(Id=job_id)
            status = job_status["Job"]["Status"]
            if status == "COMPLETE":
                print("  ✅ Cloud rendering COMPLETE!")
                # Get the actual output path from MediaConvert metadata
                try:
                    print("  [*] Debug: Examining OutputGroupDetails...")
                    if "OutputGroupDetails" in job_status["Job"]:
                        ogd = job_status["Job"]["OutputGroupDetails"]
                        print(f"  [*] Debug: Found {len(ogd)} output groups")
                        for i, group in enumerate(ogd):
                            if "OutputDetails" in group:
                                od = group["OutputDetails"]
                                print(f"  [*] Debug: Group {i} has {len(od)} outputs")
                                for j, output in enumerate(od):
                                    if "OutputFilePaths" in output and output["OutputFilePaths"]:
                                        final_s3_uri = output["OutputFilePaths"][0]
                                        print(f"  ✅ SUCCESS: Found cloud output URI: {final_s3_uri}")
                                        break
                                if final_s3_uri: break
                    
                    if not final_s3_uri:
                        print("  ⚠ WARNING: OutputFilePaths not found in metadata. Searching S3 bucket directly...")
                        # modifier used in job
                        modifier = output_filename.split('.')[0]
                        print(f"  [*] Searching for files containing: {modifier}")
                        
                        s3_objects = self.s3_client.list_objects_v2(
                            Bucket=self.s3_bucket,
                            Prefix="outputs/"
                        )
                        
                        if "Contents" in s3_objects:
                            # Sort by last modified to get the latest one
                            files = sorted(s3_objects["Contents"], key=lambda x: x["LastModified"], reverse=True)
                            for obj in files:
                                if modifier in obj["Key"]:
                                    final_s3_uri = f"s3://{self.s3_bucket}/{obj['Key']}"
                                    print(f"  ✅ SUCCESS: Found output file via S3 search: {final_s3_uri}")
                                    break
                except Exception as e:
                    print(f"  ⚠ Error while searching for output: {e}")
                break
            elif status == "ERROR":
                raise Exception(f"MediaConvert Job Failed: {job_status['Job'].get('ErrorMessage')}")
            
            print(f"  ... status: {status}")
            await asyncio.sleep(5)
            
        # 5. Download final result
        print(f"[4/4] Downloading final video from S3...")
        local_output_path = self.output_dir / output_filename
        
        if not final_s3_uri:
            print("  ❌ ERROR: Could not find the generated video in S3!")
            raise Exception("MediaConvert output not found after searching S3")

        try:
            # Parse s3://bucket/key
            path_parts = final_s3_uri.replace("s3://", "").split("/", 1)
            bucket = path_parts[0]
            key = path_parts[1]
            
            print(f"  [*] Downloading from: {final_s3_uri}")
            print(f"  [*] Saving to: {local_output_path}")
            
            self.s3_client.download_file(bucket, key, str(local_output_path))
            print(f"✓ Cloud video successfully downloaded to {local_output_path}")
            return str(local_output_path)
            
        except Exception as e:
            print(f"  ❌ FAILED to download cloud video: {e}")
            raise  # No fallback allowed

    async def _get_mc_endpoint(self):
        """Get or refresh MediaConvert regional endpoint"""
        import os
        import boto3
        if not self._mc_endpoint:
            response = self.mc_client.describe_endpoints(MaxResults=1)
            self._mc_endpoint = response['Endpoints'][0]['Url']
            # Re-initialize client with regional endpoint
            self.mc_client = boto3.client(
                service_name="mediaconvert",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                endpoint_url=self._mc_endpoint,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
        return self._mc_endpoint

    def _compose_local(self, slides, audio_map, avatar_map, output_filename) -> str:
        """Original local MoviePy composition logic"""
        from moviepy.editor import concatenate_videoclips
        slide_clips = []
        for slide in slides:
            audio = audio_map.get(slide["slide_id"])
            avatar = avatar_map.get(slide["slide_id"])
            if not audio: continue
            clip = self._create_slide_clip(slide, audio, avatar)
            slide_clips.append(clip)
            
        print("Concatenating slide videos with MoviePy (slow fallback)...")
        final_video = concatenate_videoclips(slide_clips, method="compose")
        output_path = self.output_dir / output_filename
        
        final_video.write_videofile(
            str(output_path), 
            fps=self.fps, 
            codec='libx264', 
            audio_codec='aac', 
            threads=4,
            preset='ultrafast'
        )
        final_video.close()
        for clip in slide_clips: clip.close()
        return str(output_path)
    
    def _create_slide_clip(
        self,
        slide: Dict[str, Any],
        audio: Dict[str, Any],
        avatar: Dict[str, Any] = None
    ) -> CompositeVideoClip:
        """Create a single slide video clip with overlay"""
        
        # Load slide image
        slide_image = ImageClip(slide["image_path"])
        slide_image = slide_image.resize((self.width, self.height))
        
        # Load audio
        audio_clip = AudioFileClip(audio["audio_path"])
        audio_duration = audio_clip.duration
        
        # Set slide duration to match audio
        slide_image = slide_image.set_duration(audio_duration)
        
        # If avatar exists, overlay it
        if avatar and Path(avatar["avatar_video"]).exists():
            # Load avatar video
            avatar_clip = VideoFileClip(avatar["avatar_video"])
            
            # Resize avatar to circular size
            avatar_clip = avatar_clip.resize(
                (self.avatar_size, self.avatar_size)
            )
            
            # Match duration
            if avatar_clip.duration < audio_duration:
                # Loop if avatar is shorter
                avatar_clip = avatar_clip.loop(duration=audio_duration)
            else:
                # Trim if avatar is longer
                avatar_clip = avatar_clip.subclip(0, audio_duration)
            
            # Position in bottom-right corner
            avatar_x = self.width - self.avatar_size - self.avatar_margin
            avatar_y = self.height - self.avatar_size - self.avatar_margin
            
            avatar_clip = avatar_clip.set_position((avatar_x, avatar_y))
            
            # Add circular mask (optional - requires additional setup)
            # For now, we'll use square avatar
            
            # Composite: slide + avatar
            composite = CompositeVideoClip([slide_image, avatar_clip])
        else:
            # No avatar, just slide
            composite = slide_image
        
        # Add audio
        composite = composite.set_audio(audio_clip)
        
        return composite
    
    def create_preview(
        self,
        slides: List[Dict[str, Any]],
        audio_files: List[Dict[str, Any]],
        slide_id: int,
        output_filename: str = "preview.mp4"
    ) -> str:
        """
        Create a preview of a single slide (for testing)
        
        Args:
            slides: All slides
            audio_files: All audio files
            slide_id: Which slide to preview
            output_filename: Preview filename
            
        Returns:
            Path to preview video
        """
        
        # Find the slide and audio
        slide = next((s for s in slides if s["slide_id"] == slide_id), None)
        audio = next((a for a in audio_files if a["slide_id"] == slide_id), None)
        
        if not slide or not audio:
            raise ValueError(f"Slide {slide_id} not found")
        
        # Create clip (without avatar for quick preview)
        clip = self._create_slide_clip(slide, audio)
        
        # Output path
        output_path = self.output_dir / output_filename
        
        # Write preview
        clip.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac'
        )
        
        clip.close()
        
        return str(output_path)


# Example usage
if __name__ == "__main__":
    agent = VideoCompositionAgent()
    
    # Sample data
    sample_slides = [
        {
            "slide_id": 1,
            "image_path": "outputs/slides/slide_001.png"
        }
    ]
    
    sample_audio = [
        {
            "slide_id": 1,
            "audio_path": "outputs/audio/slide_001.mp3"
        }
    ]
    
    sample_avatars = [
        {
            "slide_id": 1,
            "avatar_video": "outputs/avatars/avatar_001.mp4"
        }
    ]
    
    # final_video = agent.compose_video(sample_slides, sample_audio, sample_avatars)
    # print(f"Final video: {final_video}")
