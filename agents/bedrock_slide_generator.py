"""
Premium Slide Generation using AWS Bedrock + HTML Rendering
Uses Amazon Nova Pro to generate professional HTML/CSS slides, then renders to images
"""

from pathlib import Path
from typing import Dict, Any, List
import json
import os
import boto3
import base64
import random
from PIL import Image
from io import BytesIO

class BedrockSlideGenerator:
    """Generates premium educational slides using AWS Bedrock LLM + HTML rendering"""
    
    def __init__(self, output_dir: str = "./outputs/slides"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Bedrock client
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        # For background generation
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    

    
    async def generate_slide_image(self, chunk: Dict[str, Any], slide_num: int, theme: str) -> str:
        """Generate premium slide using Hybrid AWS AI: Nova Canvas (Art) + Nova Pro (Design)"""
        
        print(f"  [{slide_num}] Orchestrating Premium AI Slide: {chunk['title'][:50]}...")
        
        # 1. Generate Thematic Background with Nova Canvas
        bg_path = await self._generate_thematic_background(chunk, theme)
        bg_base64 = ""
        if bg_path:
            with open(bg_path, "rb") as f:
                bg_base64 = base64.b64encode(f.read()).decode()

        # 2. Get HTML design from Nova Pro, embedding the AI background
        html_content = await self.generate_slide_html(chunk, slide_num, theme, bg_base64)
        
        if html_content:
            # 3. Render HTML to image
            slide_path = await self._render_html_to_image(html_content, slide_num)
            if slide_path:
                print(f"  ✅ AI Hybrid slide created")
                return slide_path
        
        # REMOVED FALLBACK: We want to see the error, not hide it with a basic layout
        raise Exception("Failed to generate premium AI slide (Nova Pro HTML stage)")

    async def _generate_thematic_background(self, chunk: Dict[str, Any], theme: str) -> str:
        """Generate a thematic background image using Nova Canvas"""
        hint = chunk.get("visual_hint", "abstract educational background")
        prompt = f"Professional abstract teaching background, {hint}, {theme} palette, cinematic, high quality, minimal detail in center"
        
        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": prompt},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 1024,
                "cfgScale": 7.0,
                "seed": random.randint(0, 100000)
            }
        })

        try:
            response = self.bedrock_runtime.invoke_model(
                body=body,
                modelId="amazon.nova-canvas-v1:0",
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response.get("body").read())
            base64_image = response_body.get("images")[0]
            
            output_path = self.output_dir / f"bg_temp_{random.randint(0, 1000)}.png"
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(base64_image))
            return str(output_path)
        except Exception as e:
            print(f"    ⚠ Background generation failed: {e}")
            return None

    async def generate_slide_html(self, chunk: Dict[str, Any], slide_num: int, theme: str, bg_base64: str = "") -> str:
        """Use Amazon Nova Pro to generate professional HTML/CSS slide with embedded background"""
        
        title = chunk["title"]
        key_points = chunk["key_points"][:5]
        
        bg_style = ""
        if bg_base64:
            bg_style = f"background-image: url('data:image/png;base64,{bg_base64}'); background-size: cover; background-position: center;"

        # Use a placeholder for the background to save thousands of input tokens
        bg_instruction = ""
        if bg_base64:
            bg_instruction = "5. EMBED THE BACKGROUND: The body or main container MUST include this EXACT placeholder in the style: background-image: url('data:image/png;base64,{{AI_BACKGROUND_BASE64}}'); background-size: cover;"
        else:
            bg_instruction = "5. DESIGN: Use a professional solid or gradient background suited for the theme."

        # Prompt for Nova Pro to generate HTML/CSS (optimized tokens)
        prompt = f"""Create a stunning professional educational slide in HTML/CSS. 

**Slide Content:**
Title: {title}
Key Points:
{chr(10).join(f"- {point}" for point in key_points)}

**Design Requirements:**
1. Modern design, high-end corporate/educational aesthetic
2. Theme: {theme}
3. Use professional fonts (Inter, Roboto)
4. Slide size: 1920x1080px
{bg_instruction}
6. If a background is intended, use GLASSMORPHISM (semi-transparent blurred cards) for the content to ensure readability.
7. Use cards, icons, and subtle CSS animations.
8. Make the layout visually interesting (not just a list).

**Output:**
Return ONLY the self-contained HTML/CSS code. No extra text."""

        try:
            response = self.bedrock_client.converse(
                modelId="amazon.nova-pro-v1:0",
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 4000, "temperature": 0.7}
            )
            html = response["output"]["message"]["content"][0]["text"]
            if "```html" in html: html = html.split("```html")[1].split("```")[0].strip()
            elif "```" in html: html = html.split("```")[1].split("```")[0].strip()
            
            # Replace placeholder with actual large base64 data (saves input tokens!)
            if bg_base64:
                html = html.replace("{{AI_BACKGROUND_BASE64}}", bg_base64)
                
            return html
        except Exception as e:
            print(f"    ❌ Nova Pro HTML failed: {e}")
            raise # Propagate error for debugging as requested

    async def _render_html_to_image(self, html: str, slide_num: int) -> str:
        """Render HTML to image using headless browser"""
        try:
            from playwright.async_api import async_playwright
            output_path = self.output_dir / f"slide_{slide_num:03d}.png"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(viewport={"width": 1920, "height": 1080})
                await page.set_content(html)
                # Wait for any network requests (fonts, etc)
                await page.wait_for_timeout(1000)
                await page.screenshot(path=str(output_path), full_page=False)
                await browser.close()
            return str(output_path)
        except Exception as e:
            print(f"    ⚠ Playwright rendering failed: {e}")
            return None

    async def _generate_canvas_slide(self, chunk: Dict[str, Any], slide_num: int, theme: str) -> str:
        """Fallback: Generate slide with Nova Canvas (image-only)"""
        title = chunk["title"][:60]
        points = " | ".join(chunk["key_points"][:3])[:100]
        prompt = f"Educational presentation slide. Title: {title}. Topics: {points}. Theme: {theme}. Professional design, clean layout, readable text"
        
        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": prompt},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 1024,
                "cfgScale": 7.0,
                "seed": random.randint(0, 100000)
            }
        })
        try:
            response = self.bedrock_runtime.invoke_model(
                body=body,
                modelId="amazon.nova-canvas-v1:0",
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response.get("body").read())
            base64_image = response_body.get("images")[0]
            output_path = self.output_dir / f"slide_{slide_num:03d}.png"
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(base64_image))
            return str(output_path)
        except Exception as e:
            print(f"    ⚠ Nova Canvas fallback failed: {e}")
            return None
