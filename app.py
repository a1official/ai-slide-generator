"""
FastAPI Server for Educational Video Generator
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uvicorn
from dotenv import load_dotenv
import os

from orchestrator.pipeline import VideoGenerationPipeline

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Educational Video Generator",
    description="Convert documents into educational videos with AI narration and avatar",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./outputs"))
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize pipeline
pipeline = VideoGenerationPipeline()


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "AI Educational Video Generator",
        "version": "1.0.0",
        "endpoints": {
            "generate_video": "/generate-video [POST]",
            "generate_preview": "/generate-preview [POST]",
            "health": "/health [GET]"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    
    # Check if API key is configured
    groq_key = os.getenv("GROQ_API_KEY")
    
    return {
        "status": "healthy",
        "agents": {
            "ingestion": "✓",
            "content_understanding": "✓" if groq_key else "✗ Missing GROQ_API_KEY",
            "slide_generation": "✓",
            "explanation": "✓" if groq_key else "✗ Missing GROQ_API_KEY",
            "tts": "✓",
            "avatar": "✓" if Path("./Wav2Lip").exists() else "✗ Wav2Lip not installed",
            "video_composition": "✓"
        },
        "directories": {
            "uploads": str(UPLOAD_DIR),
            "outputs": str(OUTPUT_DIR)
        }
    }


@app.post("/generate-video")
async def generate_video(
    file: UploadFile = File(..., description="PDF/DOCX/TXT document"),
    avatar_image: UploadFile = File(None, description="Presenter face image (JPG/PNG), optional"),
    model: str = Form(None),
    theme: str = Form("modern_dark"),
    intelligence: str = Form("standard"),
    provider: str = Form("groq")
):
    """
    Generate a complete educational video
    
    Upload a document and optional presenter image to generate a video with:
    - AI-generated slides
    - Text-to-speech narration
    - Lip-synced avatar (if image provided)
    - custom LLM model (optional)
    """
    
    try:
        # Save uploaded document
        doc_path = UPLOAD_DIR / file.filename
        with open(doc_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        avatar_path = None
        if avatar_image and avatar_image.filename:
            print(f"[*] Avatar image detected: {avatar_image.filename}")
            avatar_path = UPLOAD_DIR / avatar_image.filename
            with open(avatar_path, "wb") as buffer:
                shutil.copyfileobj(avatar_image.file, buffer)
            use_avatar = True
        else:
            print("[*] No avatar image provided or empty filename.")
            use_avatar = False
        
        # Generate video using pipeline
        result = await pipeline.generate_video(
            document_path=str(doc_path),
            avatar_image_path=str(avatar_path) if avatar_path else None,
            output_name=f"video_{file.filename.split('.')[0]}.mp4",
            use_avatar=use_avatar,
            model=model,
            theme=theme,
            intelligence=intelligence,
            provider=provider
        )
        
        return JSONResponse(content={
            "status": "success",
            "message": "Video generated successfully",
            "video_path": result["video_path"],
            "metadata": result["metadata"],
            "download_url": f"/download/{Path(result['video_path']).name}"
        })
        
    except Exception as e:
        print(f"❌ Error in generate_video: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-preview")
async def generate_preview(
    file: UploadFile = File(..., description="PDF/DOCX/TXT document"),
    max_slides: int = Form(2),
    theme: str = Form("modern_dark"),
    provider: str = Form("groq")
):
    """
    Generate a quick preview (2 slides, no avatar)
    
    Faster than full video generation, useful for testing content extraction
    """
    
    try:
        # Save uploaded document
        doc_path = UPLOAD_DIR / file.filename
        with open(doc_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate preview
        result = await pipeline.generate_preview(
            document_path=str(doc_path),
            max_slides=max_slides,
            theme=theme,
            provider=provider
        )
        
        return JSONResponse(content={
            "status": "success",
            "message": "Preview generated successfully",
            "preview_path": result["preview_path"],
            "slides_generated": result["slides_generated"],
            "download_url": f"/download/{Path(result['preview_path']).name}"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_video(filename: str):
    """Download generated video"""
    
    video_path = OUTPUT_DIR / "videos" / filename
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=filename
    )


@app.delete("/cleanup")
async def cleanup_files():
    """Clean up all generated files (useful for development)"""
    
    try:
        # Clean outputs
        for subdir in OUTPUT_DIR.iterdir():
            if subdir.is_dir():
                for file in subdir.iterdir():
                    file.unlink()
        
        # Clean uploads
        for file in UPLOAD_DIR.iterdir():
            if file.is_file():
                file.unlink()
        
        return {
            "status": "success",
            "message": "All files cleaned up"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Get config from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print("\n" + "="*60)
    print("🎓 AI Educational Video Generator API")
    print("="*60)
    print(f"Server: http://{host}:{port}")
    print(f"Docs: http://{host}:{port}/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host=host, port=port)
