"""
Diagnostic script to test the video composition fix
"""
import asyncio
from pathlib import Path

async def test_ffmpeg_composition():
    """Test if FFmpeg composition works"""
    print("=" * 60)
    print("🔍 DIAGNOSTIC TEST - FFmpeg Video Composition")
    print("=" * 60)
    print()
    
    # Check if FFmpeg is available
    import subprocess
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("✅ FFmpeg is installed")
        print(f"   Version: {result.stdout.split('\\n')[0]}")
    except FileNotFoundError:
        print("❌ FFmpeg not found! Please install FFmpeg.")
        return
    
    print()
    
    # Check for temp files
    output_dir = Path("outputs/videos")
    temp_files = list(output_dir.glob("temp_slide_*.mp4"))
    if temp_files:
        print(f"⚠️  Found {len(temp_files)} temporary slide files")
        print("   This suggests a previous generation failed during concatenation")
        print()
        
        # Try to concatenate these files
        print("🔧 Attempting to concatenate existing temp files...")
        
        # Create concat list
        concat_file = output_dir / "test_concat_list.txt"
        with open(concat_file, 'w') as f:
            for temp_file in sorted(temp_files):
                abs_path = temp_file.absolute().as_posix()
                f.write(f"file '{abs_path}'\\n")
        
        print(f"   Created concat list with {len(temp_files)} files")
        
        # Try concatenation
        output_file = output_dir / "test_concatenated.mp4"
        concat_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            str(output_file)
        ]
        
        try:
            result = subprocess.run(
                concat_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            print(f"✅ Concatenation successful!")
            print(f"   Output: {output_file}")
            print(f"   Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
            print()
            print("🎉 FFmpeg composition is working correctly!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Concatenation failed!")
            print(f"   Error: {e.stderr[:500]}")
            print()
            print("This means there's an issue with the temp files or FFmpeg command")
        
        finally:
            # Cleanup
            if concat_file.exists():
                concat_file.unlink()
    
    else:
        print("ℹ️  No temp files found. Running a fresh test...")
        print()
        
        # Import pipeline
        try:
            from orchestrator.pipeline import VideoGenerationPipeline
            
            pipeline = VideoGenerationPipeline()
            
            print("🧪 Testing with sample document...")
            print("   - Document: uploads/test.txt")
            print("   - Slides: 1")
            print("   - Avatar: No")
            print()
            
            result = await pipeline.generate_video(
                document_path="uploads/test.txt",
                output_name="diagnostic_test.mp4",
                max_slides=1,
                use_avatar=False,
                theme="modern_dark",
                provider="groq"
            )
            
            print()
            print("✅ Test completed successfully!")
            print(f"   Video: {result['video_path']}")
            print(f"   Time: {result['processing_time']:.1f}s")
            
        except Exception as e:
            print()
            print("❌ Test failed!")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ffmpeg_composition())
