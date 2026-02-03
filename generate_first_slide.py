#!/usr/bin/env python3
"""
Generate only the first slide from a PDF document
"""
import asyncio
import sys
from pathlib import Path
from orchestrator.pipeline import VideoGenerationPipeline

async def generate_first_slide(pdf_path: str):
    """Generate only the first slide from a PDF"""
    
    pdf_file = Path(pdf_path).expanduser()
    
    if not pdf_file.exists():
        print(f"❌ Error: File not found: {pdf_file}")
        return
    
    print(f"📄 Processing: {pdf_file}")
    print("🎨 Generating first slide only...\n")
    
    pipeline = VideoGenerationPipeline()
    
    # Use generate_preview with max_slides=0 to get just the title slide
    # We'll use amazon_bedrock provider to get the premium quality
    result = await pipeline.generate_preview(
        document_path=str(pdf_file),
        max_slides=0,  # This will generate only the title slide
        theme="modern_dark",
        provider="amazon_bedrock"
    )
    
    print(f"\n✅ First slide generated!")
    print(f"📍 Location: outputs/slides/slide_001.png")
    print(f"🎬 Preview video: {result['preview_path']}")

if __name__ == "__main__":
    pdf_path = "~/Downloads/leph101.pdf"
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    asyncio.run(generate_first_slide(pdf_path))
