"""
TTS Agent
Responsibility: Convert text scripts to speech using Edge TTS (100% FREE)
"""

import edge_tts
import asyncio
import os
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class TTSAgent:
    """Converts teaching scripts into audio using Microsoft Edge TTS"""
    
    def __init__(self, output_dir: str = "./outputs/audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default voice (can be changed)
        self.voice = os.getenv("TTS_VOICE", "en-US-JennyNeural")
        self.polly_voice = os.getenv("POLLY_VOICE", "Joanna")
        
        # AWS Client for Polly
        import boto3
        self.polly_client = boto3.client(
            service_name="polly",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    
    async def generate_audio(self, scripts: List[Dict[str, Any]], provider: str = "edge") -> List[Dict[str, Any]]:
        """
        Generate audio files for all scripts
        """
        if provider in ["bedrock", "aws", "amazon_bedrock"]:
            return await self._generate_all_audio_polly(scripts)
        else:
            return await self._generate_all_audio_edge(scripts)
    
    async def _generate_all_audio_edge(self, scripts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Async generation using Edge TTS"""
        tasks = [self._generate_single_audio_edge(script) for script in scripts]
        results = await asyncio.gather(*tasks)
        return results

    async def _generate_all_audio_polly(self, scripts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generation using Amazon Polly"""
        results = []
        for script in scripts:
            result = await self._generate_single_audio_polly(script)
            results.append(result)
        return results
    
    async def _generate_single_audio_edge(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio for a single script using Edge TTS"""
        slide_id = script_data["slide_id"]
        script_text = script_data["script"]
        
        audio_filename = f"slide_{slide_id:03d}.mp3"
        audio_path = self.output_dir / audio_filename
        
        communicate = edge_tts.Communicate(script_text, self.voice)
        await communicate.save(str(audio_path))
        
        word_count = len(script_text.split())
        estimated_duration = word_count / 2.5
        
        return {
            "slide_id": slide_id,
            "script": script_text,
            "audio_path": str(audio_path),
            "duration": round(estimated_duration, 2)
        }

    async def _generate_single_audio_polly(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio using Amazon Polly"""
        slide_id = script_data["slide_id"]
        script_text = script_data["script"]
        
        audio_filename = f"slide_{slide_id:03d}.mp3"
        audio_path = self.output_dir / audio_filename

        try:
            response = self.polly_client.synthesize_speech(
                Text=script_text,
                OutputFormat="mp3",
                VoiceId=self.polly_voice,
                Engine="neural"
            )
            
            with open(audio_path, 'wb') as f:
                f.write(response['AudioStream'].read())
                
            # Get real duration (rough estimate since Polly stream doesn't give it easily)
            word_count = len(script_text.split())
            duration = word_count / 2.5
            
            return {
                "slide_id": slide_id,
                "script": script_text,
                "audio_path": str(audio_path),
                "duration": round(duration, 2)
            }
        except Exception as e:
            print(f"Polly error: {e}")
            return await self._generate_single_audio_edge(script_data)
    
    async def list_available_voices(self) -> List[str]:
        """List all available Edge TTS voices (for reference)"""
        voices = await edge_tts.list_voices()
        
        # Filter English voices
        english_voices = [
            v["ShortName"] for v in voices 
            if v["Locale"].startswith("en-")
        ]
        
        return english_voices
    
    def set_voice(self, voice_name: str):
        """Change the TTS voice"""
        self.voice = voice_name


# Example usage
if __name__ == "__main__":
    agent = TTSAgent()
    
    # List available voices
    # voices = asyncio.run(agent.list_available_voices())
    # print("Available voices:", voices[:10])
    
    sample_scripts = [
        {
            "slide_id": 1,
            "script": "Welcome! Today we're going to learn about DNS.",
            "estimated_duration": 3.5
        }
    ]
    
    # audio_files = agent.generate_audio(sample_scripts)
    # print(audio_files)
