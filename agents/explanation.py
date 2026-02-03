"""
Explanation Agent
Responsibility: Generate natural teaching scripts for each slide
"""

import os
from groq import Groq
import boto3
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class ExplanationAgent:
    """Generates conversational teaching scripts for slides"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.groq_client = Groq(api_key=self.api_key)
        
        # Bedrock client with explicit credentials
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        # Target duration per slide (seconds)
        self.target_duration = 25
    
    async def generate_scripts(self, slides: List[Dict[str, Any]], model: str = None, detail_level: str = "standard", provider: str = "groq") -> List[Dict[str, Any]]:
        """
        Generate teaching scripts for all slides.
        detail_level: 'standard' (~25s/slide) or 'intelligent' (~60s/slide).
        """
        self.target_duration = 60 if detail_level == "intelligent" else 25
        scripts = []
        for i, slide in enumerate(slides):
            script = self._generate_script_for_slide(slide, slide_index=i, model=model, detail_level=detail_level, provider=provider)
            scripts.append(script)
        
        return scripts
    
    def _generate_script_for_slide(self, slide: Dict[str, Any], slide_index: int = 0, model: str = None, detail_level: str = "standard", provider: str = "groq") -> Dict[Any, Any]:
        """Generate script for a single slide"""
        
        slide_type = slide.get("type", "content")
        
        if slide_type == "title":
            script_text = self._generate_title_script(slide)
        elif slide_type == "outro":
            script_text = self._generate_outro_script(slide)
        else:
            script_text = self._generate_content_script(slide, slide_index=slide_index, model=model, detail_level=detail_level, provider=provider)
        
        # Estimate duration (rough: ~150 words per minute = 2.5 words per second)
        word_count = len(script_text.split())
        estimated_duration = word_count / 2.5
        
        return {
            "slide_id": slide["slide_id"],
            "script": script_text,
            "estimated_duration": round(estimated_duration, 1)
        }
    
    def _generate_title_script(self, slide: Dict[str, Any]) -> str:
        """Generate intro script for title slide"""
        topic = slide.get("title", "this topic")
        
        return f"""
        Welcome, everyone! Today, we're going to dive into an exciting topic: {topic}.
        By the end of this video, you'll have a clear understanding of the key concepts.
        So let's get started!
        """.strip()
    
    def _generate_outro_script(self, slide: Dict[str, Any]) -> str:
        """Generate closing script"""
        return """
        And that wraps up our lesson for today! I hope you found this explanation helpful
        and gained some valuable insights. If you have any questions, feel free to reach out.
        Thanks for watching, and see you in the next video!
        """.strip()
    
    def _generate_content_script(self, slide: Dict[str, Any], slide_index: int = 0, model: str = None, detail_level: str = "standard", provider: str = "groq") -> str:
        """Generate teaching script with intellectual depth"""
        target_model = model or self.model
        
        # High-intelligence prompt for deeper explanations
        if detail_level == "intelligent":
            detail_prompt = (
                "Provide an ELABORATE, EXPERT-level lecture. "
                "Dive deep into the 'why' and 'how', not just the 'what'. "
                "Use analogies, explain technical relationships, and provide historical or practical context. "
                "Ensure every point on the slide is thoroughly explained."
            )
        else:
            detail_prompt = "Keep it simple, clear, and conversational. Briefly explain each point."
            
        bullets = slide.get("bullets", [])
        
        # Context about slide position to avoid repeating "Welcome"
        position_instruction = (
            "This is the first slide. You may start with a brief greeting."
            if slide_index == 0 else
            "This is NOT the first slide. DO NOT say 'Welcome', 'Hello', or 'Hi'. "
            "DO NOT repeat previous greetings. Transition directly into the topic for this specific slide."
        )

        prompt = f"""
Generate a professional teaching script for a specific slide in an educational video.

**Slide Context:**
Slide Index: {slide_index + 1}
Title: {slide.get('title', '')}
Key Points (Bullets):
{chr(10).join(f"• {point}" for point in bullets)}

**Instructions:**
1. {position_instruction}
2. {detail_prompt}
3. Target Segment Duration: {self.target_duration} seconds ({int(self.target_duration * 2.5)} words).
4. Tone: Academic yet engaging (Professorial).
5. Output format: Return ONLY the script text, ready for TTS. No markdown, no meta-text.

**Script:**
"""
        if provider == "amazon_bedrock":
            return self._generate_with_bedrock(prompt)
        
        try:
            response = self.groq_client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": "You are an expert educator who creates engaging, easy-to-understand teaching scripts for educational videos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            return response.choices[0].message.content.strip().strip('"').strip("'")
        except Exception:
            return self._generate_fallback_script(slide.get("title", ""), bullets)

    def _generate_with_bedrock(self, prompt: str) -> str:
        """Generate script using Amazon Nova Pro v1"""
        model_id = "amazon.nova-pro-v1:0"
        
        messages = [{
            "role": "user",
            "content": [{"text": prompt}]
        }]

        try:
            response = self.bedrock_client.converse(
                modelId=model_id,
                messages=messages,
                inferenceConfig={"maxTokens": 500, "temperature": 0.8}
            )
            return response["output"]["message"]["content"][0]["text"].strip().strip('"').strip("'")
        except Exception as e:
            print(f"[-] Bedrock (Nova) failed: {e}")
            return "Failed to generate script with Amazon Nova."
    
    def _generate_fallback_script(self, title: str, bullets: List[str]) -> str:
        """Simple fallback script if LLM fails"""
        script = f"Let's talk about {title}. "
        
        for i, point in enumerate(bullets):
            if i == 0:
                script += f"First, {point}. "
            elif i == len(bullets) - 1:
                script += f"Finally, {point}."
            else:
                script += f"Next, {point}. "
        
        return script


# Example usage
if __name__ == "__main__":
    agent = ExplanationAgent()
    
    sample_slide = {
        "slide_id": 2,
        "title": "What is DNS?",
        "bullets": [
            "Maps domain names to IP addresses",
            "Works like a phonebook",
            "Essential for internet navigation"
        ],
        "type": "content"
    }
    
    # script = agent._generate_script_for_slide(sample_slide)
    # print(script)
