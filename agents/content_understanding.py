"""
Content Understanding Agent
Responsibility: Understand topic and break content into teachable chunks
"""

import os
from groq import Groq
from typing import List, Dict, Any
from dotenv import load_dotenv
import json
import base64
import boto3

load_dotenv()


class ContentUnderstandingAgent:
    """Uses LLM to break content into structured learning chunks"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.groq_client = Groq(api_key=self.api_key)
        
        # Bedrock config with explicit credentials
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    
    async def process_content(self, raw_text: str, model: str = None, page_images: List[str] = None, depth: str = "standard", provider: str = "groq") -> List[Dict[str, Any]]:
        """
        Convert raw text into structured learning chunks.
        Depth can be 'standard' (5-10 chunks) or 'comprehensive' (15-20 chunks).
        """
        target_model = model or self.model
        prompt = self._build_prompt(raw_text, depth)
        
        if provider == "amazon_bedrock":
            return await self._process_with_bedrock(prompt, page_images)
        
        # Groq implementation
        system_content = "You are an expert educator who breaks down complex topics into simple, teachable chunks suitable for educational video slides."
        messages = [{"role": "system", "content": system_content}]
        is_vision = "vision" in target_model.lower()
        
        if is_vision and page_images:
            user_content = [{"type": "text", "text": prompt}]
            for img_path in page_images[:3]:
                with open(img_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    user_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": prompt})

        try:
            response = self.groq_client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=0.7,
                max_tokens=8000
            )
            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Error processing content with Groq: {str(e)}")

    async def _process_with_bedrock(self, prompt: str, page_images: List[str] = None) -> List[Dict[str, Any]]:
        """Process using Amazon Nova Pro v1 (Bypasses third-party billing locks)"""
        # Amazon Nova Pro is a first-party model, so it doesn't need a marketplace license
        model_id = "amazon.nova-pro-v1:0"
        
        messages = [{
            "role": "user",
            "content": [{"text": prompt}]
        }]
        
        if page_images:
            for img_path in page_images[:3]:
                with open(img_path, "rb") as f:
                    data = f.read()
                    messages[0]["content"].append({
                        "image": {
                            "format": "png",
                            "source": {"bytes": data}
                        }
                    })

        try:
            print(f"[*] Invoking Amazon Bedrock: {model_id}...")
            response = self.bedrock_client.converse(
                modelId=model_id,
                messages=messages,
                inferenceConfig={"maxTokens": 4000, "temperature": 0.7}
            )
            return self._parse_response(response["output"]["message"]["content"][0]["text"])
                
        except Exception as e:
            print(f"[-] Amazon Bedrock failed: {str(e)}")
            raise e
    
    def _build_prompt(self, text: str, depth: str) -> str:
        """Build the prompt based on desired intellectual depth"""
        chunk_count = "15-20" if depth == "comprehensive" else "5-10"
        detail_instruction = (
            "Provide deep, nuanced insights. Do not just summarize; explain the 'why' and 'how'." 
            if depth == "comprehensive" 
            else "Keep it simple and conversational."
        )

        return f"""
Analyze the following educational content with an INTELLIGENT and ACADEMIC lens.
Break it down into {chunk_count} high-quality learning sections.

CONTENT:
{text[:12000]}  

INSTRUCTIONS:
1. {detail_instruction}
2. For each section, create:
   - A professional, descriptive title
   - 4-7 detailed key points (comprehensive but concise)
   - Complexity level (beginner/intermediate/advanced)
   - A 'visual_hint' for a diagram (e.g., 'flowchart', 'hierarchy', 'venn diagram')

3. Return ONLY a valid JSON array:
[
  {{
    "title": "Section Title",
    "key_points": ["Detail 1", "Detail 2", "Detail 3", "Detail 4"],
    "complexity": "intermediate",
    "visual_hint": "suggested diagram"
  }}
]
"""
    
    def _parse_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured chunks"""
        try:
            # Try to extract JSON from response
            # Sometimes LLM adds markdown code blocks
            content = content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            chunks = json.loads(content)
            
            # Validate structure
            if not isinstance(chunks, list):
                raise ValueError("Response is not a list")
            
            for chunk in chunks:
                if "title" not in chunk or "key_points" not in chunk:
                    raise ValueError("Invalid chunk structure")
            
            return chunks
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}\nResponse: {content}")
        except Exception as e:
            raise Exception(f"Error parsing content chunks: {str(e)}")


# Example usage
if __name__ == "__main__":
    agent = ContentUnderstandingAgent()
    
    sample_text = """
    DNS (Domain Name System) is like the phonebook of the internet. 
    When you type a website address, DNS translates it into an IP address 
    that computers can understand. The process involves multiple servers...
    """
    
    # chunks = agent.process_content(sample_text)
    # print(json.dumps(chunks, indent=2))
