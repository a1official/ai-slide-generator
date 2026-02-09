"""
Example usage script for Wav2Lip video processing
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_inference import Wav2LipVideoProcessor
import config


def example_single_video():
    """Example: Process a single video"""
    print("\n" + "="*60)
    print("Example 1: Single Video Processing")
    print("="*60 + "\n")
    
    # Paths (update these to your actual files)
    checkpoint_path = "../checkpoints/wav2lip_gan.pth"
    face_video = "path/to/your/video.mp4"
    audio_file = "path/to/your/audio.wav"
    output_path = "outputs/result.mp4"
    
    # Create processor
    processor = Wav2LipVideoProcessor(checkpoint_path)
    
    # Process video with default settings
    processor.process_video(
        face_video_path=face_video,
        audio_source_path=audio_file,
        output_path=output_path
    )
    
    print(f"\n✓ Output saved to: {output_path}")


def example_custom_params():
    """Example: Process video with custom parameters"""
    print("\n" + "="*60)
    print("Example 2: Custom Parameters")
    print("="*60 + "\n")
    
    checkpoint_path = "../checkpoints/wav2lip_gan.pth"
    face_video = "path/to/your/video.mp4"
    audio_file = "path/to/your/audio.wav"
    output_path = "outputs/result_custom.mp4"
    
    processor = Wav2LipVideoProcessor(checkpoint_path)
    
    # Process with custom parameters
    processor.process_video(
        face_video_path=face_video,
        audio_source_path=audio_file,
        output_path=output_path,
        resize_factor=2,  # Reduce resolution by 2x for faster processing
        face_det_batch_size=32,  # Larger batch size
        wav2lip_batch_size=256,  # Larger batch size
        pads=[0, 20, 0, 0],  # More bottom padding to include chin
        output_quality=1  # Best quality
    )
    
    print(f"\n✓ Output saved to: {output_path}")


def example_quality_presets():
    """Example: Using quality presets"""
    print("\n" + "="*60)
    print("Example 3: Quality Presets")
    print("="*60 + "\n")
    
    checkpoint_path = "../checkpoints/wav2lip_gan.pth"
    face_video = "path/to/your/video.mp4"
    audio_file = "path/to/your/audio.wav"
    
    processor = Wav2LipVideoProcessor(checkpoint_path)
    
    # Process with different quality presets
    for quality in ['low', 'medium', 'high']:
        print(f"\nProcessing with {quality} quality...")
        output_path = f"outputs/result_{quality}.mp4"
        
        params = config.QUALITY_PRESETS[quality]
        processor.process_video(
            face_video_path=face_video,
            audio_source_path=audio_file,
            output_path=output_path,
            **params
        )
        
        print(f"✓ {quality.capitalize()} quality output: {output_path}")


def example_video_to_video():
    """Example: Use audio from another video"""
    print("\n" + "="*60)
    print("Example 4: Video-to-Video (Extract Audio from Video)")
    print("="*60 + "\n")
    
    checkpoint_path = "../checkpoints/wav2lip_gan.pth"
    face_video = "path/to/face_video.mp4"
    audio_video = "path/to/audio_video.mp4"  # Audio will be extracted
    output_path = "outputs/result_v2v.mp4"
    
    processor = Wav2LipVideoProcessor(checkpoint_path)
    
    # The processor will automatically extract audio from the video
    processor.process_video(
        face_video_path=face_video,
        audio_source_path=audio_video,  # Can be video or audio file
        output_path=output_path
    )
    
    print(f"\n✓ Output saved to: {output_path}")


def example_batch_processing():
    """Example: Batch process multiple videos"""
    print("\n" + "="*60)
    print("Example 5: Batch Processing")
    print("="*60 + "\n")
    
    from batch_process import BatchProcessor
    
    checkpoint_path = "../checkpoints/wav2lip_gan.pth"
    
    # Create batch processor
    processor = BatchProcessor(checkpoint_path)
    
    # Option 1: Process from config file
    print("Option 1: Using config file")
    processor.process_batch_from_config("examples/batch_config.json")
    
    # Option 2: Process directory
    print("\nOption 2: Processing directory")
    processor.process_directory(
        face_videos_dir="path/to/videos",
        audio_dir="path/to/audio",
        output_dir="outputs/batch",
        quality="medium"
    )


def main():
    """Run examples"""
    print("\n" + "="*70)
    print(" Wav2Lip Video Processing - Usage Examples")
    print("="*70)
    
    examples = {
        '1': ('Single video processing', example_single_video),
        '2': ('Custom parameters', example_custom_params),
        '3': ('Quality presets', example_quality_presets),
        '4': ('Video-to-video (extract audio)', example_video_to_video),
        '5': ('Batch processing', example_batch_processing),
    }
    
    print("\nAvailable examples:")
    for key, (desc, _) in examples.items():
        print(f"  {key}. {desc}")
    
    print("\nNote: Update the file paths in this script before running!")
    print("\nTo run a specific example, modify this script to call the")
    print("desired example function directly.\n")
    
    # Uncomment to run a specific example:
    # example_single_video()
    # example_custom_params()
    # example_quality_presets()
    # example_video_to_video()
    # example_batch_processing()


if __name__ == '__main__':
    main()
