"""
Quick Start Script
Test the pipeline with a sample document
"""

import sys
from pathlib import Path

# Sample text for testing
SAMPLE_TEXT = """
Understanding Computer Networks

A computer network is a collection of interconnected devices that can communicate and share resources.

The Internet Protocol
IP addresses are unique identifiers assigned to each device on a network. An IP address consists of four numbers separated by dots, like 192.168.1.1.

DNS - Domain Name System
DNS translates human-readable domain names (like google.com) into IP addresses that computers can understand. 
When you type a website address, your computer queries DNS servers to find the corresponding IP address.

Network Protocols
Protocols are standardized rules that govern how data is transmitted across networks. Common protocols include:
- HTTP for web browsing
- FTP for file transfer
- SMTP for email

Network Security
Firewalls protect networks by monitoring and controlling incoming and outgoing traffic based on security rules.
Encryption ensures that data transmitted over networks remains confidential and secure.
"""

def create_sample_files():
    """Create sample files for testing"""
    
    # Create uploads directory
    uploads_dir = Path("./uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # Create sample document
    sample_doc = uploads_dir / "sample_document.txt"
    with open(sample_doc, 'w', encoding='utf-8') as f:
        f.write(SAMPLE_TEXT)
    
    print(f"✓ Created sample document: {sample_doc}")
    
    # Create sample avatar image (placeholder)
    print("\n⚠️  You need to provide your own avatar image!")
    print("   Place a JPG/PNG image of a face at: uploads/avatar.jpg")
    print("   (Use a clear frontal photo for best results)\n")
    
    return str(sample_doc)


def run_quick_preview():
    """Run a quick preview without avatar"""
    from orchestrator.pipeline import VideoGenerationPipeline
    
    print("\n" + "="*60)
    print("🚀 QUICK START - Preview Mode (No Avatar)")
    print("="*60 + "\n")
    
    # Create sample files
    sample_doc = create_sample_files()
    
    # Initialize pipeline
    pipeline = VideoGenerationPipeline()
    
    # Generate preview (faster, no avatar needed)
    import asyncio
    result = asyncio.run(pipeline.generate_preview(
        document_path=sample_doc,
        max_slides=2
    ))
    
    print("\n" + "="*60)
    print("✅ PREVIEW COMPLETE!")
    print("="*60)
    print(f"Preview video: {result['preview_path']}")
    print("\nYou can now:")
    print("1. Watch the preview video")
    print("2. Add your avatar image to uploads/avatar.jpg")
    print("3. Run full generation with: python quick_start.py --full")
    print("="*60 + "\n")


def run_full_generation():
    """Run full video generation with avatar"""
    from orchestrator.pipeline import VideoGenerationPipeline
    
    print("\n" + "="*60)
    print("🎬 FULL VIDEO GENERATION")
    print("="*60 + "\n")
    
    # Check for avatar image
    avatar_path = Path("./uploads/avatar.jpg")
    if not avatar_path.exists():
        avatar_path = Path("./uploads/avatar.png")
    
    if not avatar_path.exists():
        print("❌ ERROR: Avatar image not found!")
        print("   Please add your avatar image to: uploads/avatar.jpg")
        print("   Then run: python quick_start.py --full")
        return
    
    # Create sample document
    sample_doc = create_sample_files()
    
    # Initialize pipeline
    pipeline = VideoGenerationPipeline()
    
    # Generate full video
    import asyncio
    result = asyncio.run(pipeline.generate_video(
        document_path=sample_doc,
        avatar_image_path=str(avatar_path),
        output_name="sample_video.mp4",
        max_slides=1  # Limit to 1 for fast testing
    ))
    
    print("\n🎉 Your video is ready!")
    print(f"   {result['video_path']}")


def run_voice_only_generation():
    """Run full video generation with voice and slides but NO avatar"""
    from orchestrator.pipeline import VideoGenerationPipeline
    
    print("\n" + "="*60)
    print("🎙️  VOICE-ONLY VIDEO GENERATION")
    print("="*60 + "\n")
    
    # Create sample document
    sample_doc = create_sample_files()
    
    # Initialize pipeline
    pipeline = VideoGenerationPipeline()
    
    # Generate video without avatar
    import asyncio
    result = asyncio.run(pipeline.generate_video(
        document_path=sample_doc,
        output_name="voice_only_video.mp4",
        use_avatar=False
    ))
    
    print("\n🎉 Your voice-only video is ready!")
    print(f"   {result['video_path']}")


if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            run_full_generation()
        elif sys.argv[1] == "--voice-only":
            run_voice_only_generation()
        else:
            run_quick_preview()
    else:
        run_quick_preview()
