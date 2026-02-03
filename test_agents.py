"""
Test individual agents independently
"""

def test_ingestion():
    """Test document ingestion"""
    from agents.ingestion import IngestionAgent
    
    print("\n[*] Testing Ingestion Agent...")
    agent = IngestionAgent()
    
    # Create a test file
    test_file = "uploads/test.txt"
    with open(test_file, 'w') as f:
        f.write("DNS is the phonebook of the internet. It translates domain names to IP addresses.")
    
    result = agent.process_file(test_file)
    print(f"[OK] Extracted {len(result['raw_text'])} characters")
    print(f"  Text preview: {result['raw_text'][:100]}...")


def test_content_understanding():
    """Test content understanding with LLM"""
    from agents.content_understanding import ContentUnderstandingAgent
    
    print("\n[*] Testing Content Understanding Agent...")
    
    try:
        agent = ContentUnderstandingAgent()
        
        sample_text = """
        DNS, or Domain Name System, is like a phonebook for the internet.
        When you type a website address, DNS translates it into an IP address.
        DNS servers work together to resolve domain names quickly.
        """
        
        chunks = agent.process_content(sample_text)
        print(f"[OK] Generated {len(chunks)} content chunks")
        print(f"  First chunk: {chunks[0]['title']}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        print("  Make sure GROQ_API_KEY is set in .env")


def test_slide_generation():
    """Test slide image generation"""
    from agents.slide_generation import SlideGenerationAgent
    
    print("\n[*] Testing Slide Generation Agent...")
    
    agent = SlideGenerationAgent()
    
    sample_chunks = [
        {
            "title": "What is DNS?",
            "key_points": [
                "Translates domain names to IP addresses",
                "Works like a phonebook",
                "Essential for internet navigation"
            ],
            "visual_hint": "phonebook diagram"
        }
    ]
    
    slides = agent.generate_slides(sample_chunks)
    print(f"[OK] Generated {len(slides)} slide images")
    print(f"  First slide: {slides[0]['image_path']}")


def test_explanation():
    """Test script generation"""
    from agents.explanation import ExplanationAgent
    
    print("\n[*] Testing Explanation Agent...")
    
    try:
        agent = ExplanationAgent()
        
        sample_slide = {
            "slide_id": 1,
            "title": "What is DNS?",
            "bullets": [
                "Translates domain names to IP addresses",
                "Works like a phonebook"
            ],
            "type": "content"
        }
        
        script = agent._generate_script_for_slide(sample_slide)
        print(f"[OK] Generated script ({len(script.split())} words)")
        print(f"  Preview: {script[:150]}...")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        print("  Make sure GROQ_API_KEY is set in .env")


def test_tts():
    """Test text-to-speech"""
    from agents.tts import TTSAgent
    
    print("\n[*] Testing TTS Agent...")
    
    agent = TTSAgent()
    
    sample_scripts = [
        {
            "slide_id": 1,
            "script": "Welcome to this lesson about DNS. Today we'll learn how the internet resolves domain names.",
            "estimated_duration": 5
        }
    ]
    
    audio_files = agent.generate_audio(sample_scripts)
    print(f"[OK] Generated {len(audio_files)} audio files")
    print(f"  Audio file: {audio_files[0]['audio_path']}")


def test_avatar():
    """Test avatar generation (requires Wav2Lip)"""
    from agents.avatar import AvatarAgent
    from pathlib import Path
    
    print("\n[*] Testing Avatar Agent...")
    
    try:
        agent = AvatarAgent()
        
        # Check if we have test files
        audio_path = "outputs/audio/slide_001.mp3"
        avatar_path = "uploads/avatar.jpg"
        
        if not Path(audio_path).exists():
            print("[SKIP] No audio file found. Run TTS test first.")
            return
        
        if not Path(avatar_path).exists():
            print("[SKIP] No avatar image found. Add uploads/avatar.jpg")
            return
        
        sample_audio = [
            {
                "slide_id": 1,
                "audio_path": audio_path,
                "duration": 5
            }
        ]
        
        videos = agent.generate_avatars(sample_audio, avatar_path)
        print(f"[OK] Generated {len(videos)} avatar videos")
        print(f"  Video: {videos[0]['avatar_video']}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        print("  Make sure Wav2Lip is installed and model is downloaded")


def test_all():
    """Run all tests in sequence"""
    
    print("\n" + "="*60)
    print("RUNNING AGENT TESTS")
    print("="*60)
    
    test_ingestion()
    test_content_understanding()
    test_slide_generation()
    test_explanation()
    test_tts()
    # test_avatar()  # Uncomment when ready to test avatar
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60 + "\n")



if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        tests = {
            "ingestion": test_ingestion,
            "content": test_content_understanding,
            "slides": test_slide_generation,
            "explanation": test_explanation,
            "tts": test_tts,
            "avatar": test_avatar
        }
        
        if test_name in tests:
            tests[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available: {', '.join(tests.keys())}")
    else:
        test_all()
