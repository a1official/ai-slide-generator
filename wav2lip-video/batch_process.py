"""
Batch processing script for multiple videos
"""
import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from video_inference import Wav2LipVideoProcessor
import config


class BatchProcessor:
    """Process multiple videos in batch"""
    
    def __init__(self, checkpoint_path: str):
        """
        Initialize batch processor
        
        Args:
            checkpoint_path: Path to Wav2Lip checkpoint
        """
        self.processor = Wav2LipVideoProcessor(checkpoint_path)
        self.results = []
    
    def process_batch_from_config(self, config_file: str):
        """
        Process batch from a JSON configuration file
        
        Config file format:
        {
            "output_dir": "path/to/output",
            "quality": "medium",
            "videos": [
                {
                    "face_video": "path/to/video1.mp4",
                    "audio": "path/to/audio1.wav",
                    "output_name": "output1.mp4"
                },
                ...
            ]
        }
        
        Args:
            config_file: Path to JSON config file
        """
        with open(config_file, 'r') as f:
            batch_config = json.load(f)
        
        output_dir = batch_config.get('output_dir', config.OUTPUTS_DIR)
        quality = batch_config.get('quality', 'medium')
        videos = batch_config['videos']
        
        print(f"\n{'='*60}")
        print(f"Batch Processing: {len(videos)} videos")
        print(f"Output directory: {output_dir}")
        print(f"Quality preset: {quality}")
        print(f"{'='*60}\n")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Get quality params
        params = config.QUALITY_PRESETS[quality].copy()
        
        for i, video_config in enumerate(videos, 1):
            print(f"\n[{i}/{len(videos)}] Processing: {video_config.get('output_name', 'video')}")
            print("-" * 60)
            
            face_video = video_config['face_video']
            audio = video_config['audio']
            output_name = video_config.get('output_name', f'output_{i}.mp4')
            output_path = os.path.join(output_dir, output_name)
            
            # Override params if specified
            video_params = params.copy()
            if 'params' in video_config:
                video_params.update(video_config['params'])
            
            try:
                start_time = datetime.now()
                
                self.processor.process_video(
                    face_video,
                    audio,
                    output_path,
                    **video_params
                )
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                result = {
                    'index': i,
                    'output_name': output_name,
                    'status': 'success',
                    'duration': duration,
                    'output_path': output_path
                }
                
                print(f"✓ Completed in {duration:.2f}s")
                
            except Exception as e:
                print(f"✗ Failed: {str(e)}")
                result = {
                    'index': i,
                    'output_name': output_name,
                    'status': 'failed',
                    'error': str(e)
                }
            
            self.results.append(result)
        
        # Print summary
        self.print_summary()
        
        # Save results
        results_file = os.path.join(output_dir, 'batch_results.json')
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {results_file}")
    
    def process_directory(self, face_videos_dir: str, audio_dir: str,
                         output_dir: str, quality: str = 'medium'):
        """
        Process all videos in a directory
        Matches videos with audio files by name
        
        Args:
            face_videos_dir: Directory containing face videos
            audio_dir: Directory containing audio files
            output_dir: Directory to save outputs
            quality: Quality preset
        """
        face_videos = sorted(Path(face_videos_dir).glob('*.mp4'))
        
        print(f"\n{'='*60}")
        print(f"Batch Processing Directory")
        print(f"Face videos: {face_videos_dir}")
        print(f"Audio files: {audio_dir}")
        print(f"Output: {output_dir}")
        print(f"Found {len(face_videos)} videos")
        print(f"{'='*60}\n")
        
        os.makedirs(output_dir, exist_ok=True)
        params = config.QUALITY_PRESETS[quality].copy()
        
        for i, face_video_path in enumerate(face_videos, 1):
            video_name = face_video_path.stem
            
            # Look for matching audio file
            audio_path = None
            for ext in ['.wav', '.mp3', '.mp4', '.m4a']:
                potential_audio = Path(audio_dir) / f"{video_name}{ext}"
                if potential_audio.exists():
                    audio_path = str(potential_audio)
                    break
            
            if not audio_path:
                print(f"[{i}/{len(face_videos)}] Skipping {video_name}: No matching audio found")
                continue
            
            print(f"\n[{i}/{len(face_videos)}] Processing: {video_name}")
            print("-" * 60)
            
            output_path = os.path.join(output_dir, f"{video_name}_lipsynced.mp4")
            
            try:
                start_time = datetime.now()
                
                self.processor.process_video(
                    str(face_video_path),
                    audio_path,
                    output_path,
                    **params
                )
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                result = {
                    'index': i,
                    'video_name': video_name,
                    'status': 'success',
                    'duration': duration,
                    'output_path': output_path
                }
                
                print(f"✓ Completed in {duration:.2f}s")
                
            except Exception as e:
                print(f"✗ Failed: {str(e)}")
                result = {
                    'index': i,
                    'video_name': video_name,
                    'status': 'failed',
                    'error': str(e)
                }
            
            self.results.append(result)
        
        self.print_summary()
    
    def print_summary(self):
        """Print batch processing summary"""
        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] == 'success')
        failed = total - successful
        
        print(f"\n{'='*60}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total videos: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if successful > 0:
            total_time = sum(r.get('duration', 0) for r in self.results if r['status'] == 'success')
            avg_time = total_time / successful
            print(f"Average time: {avg_time:.2f}s per video")
            print(f"Total time: {total_time:.2f}s")
        
        if failed > 0:
            print("\nFailed videos:")
            for r in self.results:
                if r['status'] == 'failed':
                    print(f"  - {r.get('output_name', r.get('video_name', 'unknown'))}: {r.get('error', 'Unknown error')}")
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Batch process multiple videos with Wav2Lip'
    )
    
    parser.add_argument('--checkpoint', type=str, required=True,
                       help='Path to Wav2Lip checkpoint')
    
    # Mode selection
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--config', type=str,
                      help='Path to batch config JSON file')
    group.add_argument('--directory', action='store_true',
                      help='Process all videos in a directory')
    
    # Directory mode arguments
    parser.add_argument('--face_videos_dir', type=str,
                       help='Directory containing face videos (for --directory mode)')
    parser.add_argument('--audio_dir', type=str,
                       help='Directory containing audio files (for --directory mode)')
    parser.add_argument('--output_dir', type=str,
                       help='Output directory')
    
    parser.add_argument('--quality', type=str, default='medium',
                       choices=['low', 'medium', 'high'],
                       help='Quality preset')
    
    args = parser.parse_args()
    
    # Create batch processor
    processor = BatchProcessor(args.checkpoint)
    
    if args.config:
        # Process from config file
        processor.process_batch_from_config(args.config)
    
    elif args.directory:
        # Process directory
        if not args.face_videos_dir or not args.audio_dir or not args.output_dir:
            parser.error('--directory mode requires --face_videos_dir, --audio_dir, and --output_dir')
        
        processor.process_directory(
            args.face_videos_dir,
            args.audio_dir,
            args.output_dir,
            args.quality
        )


if __name__ == '__main__':
    main()
