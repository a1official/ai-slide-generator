"""
Simple end-to-end test for FFmpeg video composition
"""
import asyncio
from orchestrator.pipeline import VideoGenerationPipeline

async def main():
    print("\n" + "=" * 60)
    print("🧪 TESTING FFMPEG VIDEO COMPOSITION FIX")
    print("=" * 60 + "\n")
    
    pipeline = VideoGenerationPipeline()
    
    print("📝 Generating a simple 1-slide test video...")
    print("   Document: uploads/test.txt")
    print("   Provider: groq")
    print("   Slides: 1")
    print("   Avatar: No\n")
    
    try:
        result = await pipeline.generate_video(
            document_path="uploads/test.txt",
            output_name="ffmpeg_test_output.mp4",
            max_slides=1,
            use_avatar=False,
            theme="modern_dark",
            provider="groq"
        )
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"📹 Video: {result['video_path']}")
        print(f"⏱️  Time: {result['processing_time']:.1f}s")
        print("\n🎉 FFmpeg video composition is working!\n")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ FAILED")
        print("=" * 60)
        print(f"Error: {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
