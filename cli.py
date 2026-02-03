"""
CLI Tool for Video Generation Pipeline
Simple command-line interface
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="AI Educational Video Generator - Transform documents into engaging video lessons",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full video with avatar
  python cli.py generate document.pdf presenter.jpg -o my_lesson.mp4
  
  # Generate quick preview (no avatar)
  python cli.py preview document.pdf
  
  # Test individual agent
  python cli.py test slides
  
  # List available TTS voices
  python cli.py voices
  
  # Start API server
  python cli.py serve
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate video (with or without avatar)')
    gen_parser.add_argument('document', help='Path to PDF/DOCX/TXT document')
    gen_parser.add_argument('-a', '--avatar', help='Path to presenter face image')
    gen_parser.add_argument('--no-avatar', action='store_true', help='Generate video without avatar (voice + slides only)')
    gen_parser.add_argument('-o', '--output', default='video.mp4', help='Output filename')
    
    # Preview command
    prev_parser = subparsers.add_parser('preview', help='Generate quick preview (no avatar)')
    prev_parser.add_argument('document', help='Path to PDF/DOCX/TXT document')
    prev_parser.add_argument('-n', '--num-slides', type=int, default=2, help='Number of slides')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test individual agent')
    test_parser.add_argument('agent', choices=[
        'ingestion', 'content', 'slides', 'explanation', 'tts', 'avatar', 'all'
    ], help='Agent to test')
    
    # Voices command
    subparsers.add_parser('voices', help='List available TTS voices')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start API server')
    serve_parser.add_argument('-p', '--port', type=int, default=8000, help='Port number')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host address')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'generate':
        generate_video(args.document, args.avatar, args.output, args.no_avatar)
    elif args.command == 'preview':
        generate_preview(args.document, args.num_slides)
    elif args.command == 'test':
        run_test(args.agent)
    elif args.command == 'voices':
        list_voices()
    elif args.command == 'serve':
        start_server(args.host, args.port)


def generate_video(document: str, avatar: str, output: str, no_avatar: bool = False):
    """Generate video"""
    from orchestrator.pipeline import VideoGenerationPipeline
    
    # Validate files exist
    if not Path(document).exists():
        print(f"❌ Error: Document not found: {document}")
        sys.exit(1)
    
    if not no_avatar:
        if not avatar:
            print("❌ Error: Avatar image required unless --no-avatar is used")
            sys.exit(1)
        if not Path(avatar).exists():
            print(f"❌ Error: Avatar image not found: {avatar}")
            sys.exit(1)
    
    print(f"\n🎬 Starting {'voice-only ' if no_avatar else ''}video generation...")
    
    pipeline = VideoGenerationPipeline()
    import asyncio
    result = asyncio.run(pipeline.generate_video(
        document_path=document,
        avatar_image_path=avatar if not no_avatar else None,
        output_name=output,
        use_avatar=not no_avatar
    ))
    
    print(f"\n✅ Success! Video saved to: {result['video_path']}")
    print(f"⏱️  Processing time: {result['processing_time']:.1f}s")


def generate_preview(document: str, num_slides: int):
    """Generate preview"""
    from orchestrator.pipeline import VideoGenerationPipeline
    
    if not Path(document).exists():
        print(f"❌ Error: Document not found: {document}")
        sys.exit(1)
    
    print("\n🔍 Generating preview...")
    
    pipeline = VideoGenerationPipeline()
    import asyncio
    result = asyncio.run(pipeline.generate_preview(
        document_path=document,
        max_slides=num_slides
    ))
    
    print(f"\n✅ Preview saved to: {result['preview_path']}")


def run_test(agent: str):
    """Run agent test"""
    import subprocess
    
    if agent == 'all':
        subprocess.run([sys.executable, 'test_agents.py'])
    else:
        subprocess.run([sys.executable, 'test_agents.py', agent])


def list_voices():
    """List available TTS voices"""
    import asyncio
    from agents.tts import TTSAgent
    
    async def get_voices():
        agent = TTSAgent()
        voices = await agent.list_available_voices()
        return voices
    
    print("\n🎙️  Available TTS Voices:\n")
    voices = asyncio.run(get_voices())
    
    for i, voice in enumerate(voices[:20], 1):  # Show first 20
        print(f"{i:2}. {voice}")
    
    print(f"\n... and {len(voices) - 20} more voices available")
    print("\nTo use a voice, set TTS_VOICE in .env file")


def start_server(host: str, port: int):
    """Start API server"""
    import uvicorn
    
    print(f"\n🚀 Starting server at http://{host}:{port}")
    print(f"📚 API docs at http://{host}:{port}/docs\n")
    
    uvicorn.run("app:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
