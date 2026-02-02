"""
Pipeline Orchestrator
Coordinates all agents to generate educational videos
"""

import json
from pathlib import Path
from typing import Dict, Any
import time

from agents.ingestion import IngestionAgent
from agents.content_understanding import ContentUnderstandingAgent
from agents.slide_generation import SlideGenerationAgent
from agents.explanation import ExplanationAgent
from agents.tts import TTSAgent
from agents.video_composition import VideoCompositionAgent


class VideoGenerationPipeline:
    """Orchestrates the entire video generation pipeline"""
    
    def __init__(self, output_base_dir: str = "./outputs"):
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
        
        # Initialize all agents except avatar (lazy load)
        print("Initializing agents...")
        self.ingestion_agent = IngestionAgent()
        self.content_agent = ContentUnderstandingAgent()
        self.slide_agent = SlideGenerationAgent()
        self.explanation_agent = ExplanationAgent()
        self.tts_agent = TTSAgent()
        self._avatar_agent = None  # Lazy load
        self.video_agent = VideoCompositionAgent()
        print("[OK] All agents initialized")
    
    @property
    def avatar_agent(self):
        """Lazy-load avatar agent only when needed"""
        if self._avatar_agent is None:
            from agents.avatar import AvatarAgent
            self._avatar_agent = AvatarAgent()
        return self._avatar_agent
    
    async def generate_video(
        self,
        document_path: str,
        avatar_image_path: str = None,
        output_name: str = "educational_video.mp4",
        max_slides: int = None,
        use_avatar: bool = True,
        model: str = None,
        theme: str = "modern_dark",
        intelligence: str = "standard",
        provider: str = "groq"
    ) -> Dict[Any, Any]:
        """
        Complete pipeline: Document → Video
        
        Args:
            document_path: Path to PDF/DOCX/TXT
            avatar_image_path: Path to presenter's face image
            output_name: Name of final video
            
        Returns:
            {
                "video_path": "outputs/videos/educational_video.mp4",
                "metadata": {...},
                "processing_time": 120.5
            }
        """
        
        start_time = time.time()
        print(f"\n🚀 [PIPELINE] Starting generation for: {document_path}")
        print(f"   - Provider: {provider}")
        print(f"   - Use Avatar: {use_avatar}")
        print(f"   - Avatar Image: {avatar_image_path}")
        print(f"   - Theme: {theme}")
        print(f"   - Intelligence: {intelligence}")
        
        print("\n" + "="*60)
        print("🎬 STARTING VIDEO GENERATION PIPELINE")
        print("="*60 + "\n")
        
        # Step 1: Ingestion
        print("📄 [1/7] Ingesting document...")
        ingested_data = self.ingestion_agent.process_file(document_path)
        print(f"✓ Extracted {len(ingested_data['raw_text'])} characters from {ingested_data['metadata']['pages']} pages")
        
        # Step 2: Content Understanding
        print(f"\n[*] [2/7] Understanding content (Intelligence: {intelligence})...")
        page_images = ingested_data.get("page_images", [])
        content_chunks = await self.content_agent.process_content(
            ingested_data["raw_text"], 
            model=model,
            page_images=page_images,
            depth="comprehensive" if intelligence == "intelligent" else "standard",
            provider=provider
        )
        
        # Limit slides if requested
        if max_slides:
            content_chunks = content_chunks[:max_slides]
            
        print(f"[OK] Generated {len(content_chunks)} learning chunks")
        
        # Step 3: Slide Generation
        print(f"\n📊 [3/7] Generating slides (Theme: {theme})...")
        slides = await self.slide_agent.generate_slides(content_chunks, theme_name=theme, provider=provider)
        print(f"✓ Created {len(slides)} slide images")
        
        # Step 4: Explanation Scripts
        print(f"\n🗣️ [4/7] Generating teaching scripts (Level: {intelligence})...")
        scripts = await self.explanation_agent.generate_scripts(
            slides, 
            model=model, 
            detail_level=intelligence,
            provider=provider
        )
        total_duration = sum(s["estimated_duration"] for s in scripts)
        print(f"✓ Generated {len(scripts)} scripts (estimated duration: {total_duration:.1f}s)")
        
        # Step 5: Text-to-Speech
        print("\n🎙️ [5/7] Converting scripts to speech...")
        audio_files = await self.tts_agent.generate_audio(scripts, provider=provider)
        print(f"✓ Generated {len(audio_files)} audio files")
        
        # Step 6: Avatar Generation
        avatar_videos = []
        if use_avatar and avatar_image_path:
            print("\n👤 [6/7] Generating lip-synced avatars...")
            print("⚠️  This may take a while (faster with GPU)...")
            try:
                avatar_videos = self.avatar_agent.generate_avatars(audio_files, avatar_image_path, provider=provider)
                print(f"✓ Generated {len(avatar_videos)} avatar videos")
            except Exception as e:
                print(f"✗ Avatar generation failed: {e}")
                print("Proceeding without avatar...")
        else:
            if not use_avatar:
                print("\n⏭️  Skipping avatar generation (Disabled by user)")
            else:
                print("\n⏭️  Skipping avatar generation (No face image provided)")
        
        # Step 7: Video Composition
        print("\n🎥 [7/7] Composing final video...")
        final_video_path = await self.video_agent.compose_video(
            slides=slides,
            audio_files=audio_files,
            avatar_videos=avatar_videos,
            output_filename=output_name,
            provider=provider
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Save metadata
        metadata = {
            "document": str(document_path),
            "avatar_image": str(avatar_image_path),
            "slides_generated": len(slides),
            "total_duration": sum(a["duration"] for a in audio_files),
            "processing_time": round(processing_time, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        metadata_path = Path(final_video_path).with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("\n" + "="*60)
        print("✅ VIDEO GENERATION COMPLETE!")
        print("="*60)
        print(f"📹 Video: {final_video_path}")
        print(f"📊 Metadata: {metadata_path}")
        print(f"⏱️  Processing Time: {processing_time:.1f}s")
        print("="*60 + "\n")
        
        return {
            "video_path": final_video_path,
            "metadata": metadata,
            "processing_time": processing_time
        }
    
    async def generate_preview(
        self,
        document_path: str,
        max_slides: int = 2,
        theme: str = "modern_dark",
        provider: str = "groq"
    ) -> Dict[str, Any]:
        """
        Generate a quick preview without avatar (for testing)
        
        Args:
            document_path: Path to document
            max_slides: Number of slides to generate (default: 2)
            
        Returns:
            Preview metadata
        """
        
        print("\n🔍 Generating preview (no avatar)...\n")
        
        # Steps 1-5 only (no avatar)
        ingested_data = self.ingestion_agent.process_file(document_path)
        page_images = ingested_data.get("page_images", [])
        content_chunks = await self.content_agent.process_content(
            ingested_data["raw_text"],
            page_images=page_images,
            provider=provider
        )
        
        # Limit chunks
        content_chunks = content_chunks[:max_slides]
        
        slides = await self.slide_agent.generate_slides(content_chunks, theme_name=theme, provider=provider)
        scripts = await self.explanation_agent.generate_scripts(slides, provider=provider)
        audio_files = await self.tts_agent.generate_audio(scripts, provider=provider)
        
        # Create preview video (first slide only)
        preview_path = self.video_agent.create_preview(
            slides=slides,
            audio_files=audio_files,
            slide_id=1,
            output_filename="preview.mp4"
        )
        
        print(f"\n✓ Preview generated: {preview_path}\n")
        
        return {
            "preview_path": preview_path,
            "slides_generated": len(slides)
        }


# Example usage
if __name__ == "__main__":
    pipeline = VideoGenerationPipeline()
    
    # Generate full video
    # result = pipeline.generate_video(
    #     document_path="uploads/sample.pdf",
    #     avatar_image_path="uploads/presenter.jpg",
    #     output_name="my_lesson.mp4"
    # )
    
    # Or generate quick preview
    # preview = pipeline.generate_preview("uploads/sample.pdf")
