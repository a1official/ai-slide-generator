"""
Slide Generation Agent (Pro Version)
Responsibility: Generate diverse, high-end visual slides including dynamic diagrams.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import List, Dict, Any, Tuple
from pathlib import Path
import textwrap
import os
import math
import random
import boto3
import json
import base64
from io import BytesIO
from agents.bedrock_slide_generator import BedrockSlideGenerator

class SlideGenerationAgent:
    """Generates premium slide images with multiple themes, layouts, and AI-driven diagrams."""
    
    def __init__(self, output_dir: str = "./outputs/slides"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.width = 1920
        self.height = 1080
        
        self.themes = {
            "modern_dark": {
                "bg": (15, 23, 42),
                "primary": (99, 102, 241),
                "accent": (168, 85, 247),
                "text": (248, 250, 252),
                "overlay": (255, 255, 255, 15)
            },
            "cyber_neon": {
                "bg": (5, 5, 5),
                "primary": (0, 255, 255),
                "accent": (255, 0, 255),
                "text": (255, 255, 255),
                "overlay": (0, 255, 255, 20)
            },
            "elegant_light": {
                "bg": (255, 255, 255),
                "primary": (30, 41, 59),
                "accent": (99, 102, 241),
                "text": (15, 23, 42),
                "overlay": (15, 23, 42, 10)
            },
            "corporate_pro": {
                "bg": (240, 244, 248),
                "primary": (26, 54, 93),
                "accent": (43, 108, 176),
                "text": (45, 55, 72),
                "overlay": (26, 54, 93, 10)
            }
        }
        
        # Bedrock client for Image Generation (Nova Canvas)
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        self.bedrock_slide_gen = BedrockSlideGenerator(output_dir)
        self.fonts = self._load_fonts()
    
    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load consistent premium fonts"""
        try:
            # Fallback for Windows
            font_path = "segoeui.ttf"
            bold_path = "segoeuib.ttf"
            return {
                "title": ImageFont.truetype(bold_path, 100),
                "heading": ImageFont.truetype(bold_path, 70),
                "body": ImageFont.truetype(font_path, 42),
                "small": ImageFont.truetype(font_path, 30)
            }
        except:
            return {
                "title": ImageFont.load_default(),
                "heading": ImageFont.load_default(),
                "body": ImageFont.load_default(),
                "small": ImageFont.load_default()
            }

    async def generate_slides(self, chunks: List[Dict[str, Any]], theme_name: str = "modern_dark", provider: str = "edge") -> List[Dict[str, Any]]:
        """Generate a complete deck using hybrid AWS + local approach for educational slides."""
        theme = self.themes.get(theme_name, self.themes["modern_dark"])
        slides = []
        
        # 1. Intro
        if provider in ["bedrock", "aws", "amazon_bedrock"]:
            print("  [1] Orchestrating Premium AI Slide: Title Slide...")
            
            # Create a synthetic chunk for the title slide
            title_chunk = {
                "title": chunks[0]["title"] if chunks else "Masterclass",
                "key_points": [
                    "Overview of the topic",
                    "Key concepts coverage", 
                    "In-depth analysis"
                ],
                "visual_hint": "Cinematic title screen, dramatic lighting, grand entrance, high quality"
            }
            
            slide_path = await self.bedrock_slide_gen.generate_slide_image(
                chunk=title_chunk,
                slide_num=1,
                theme=theme_name
            )
            
            if slide_path:
                slides.append({
                    "slide_id": 1,
                    "type": "title",
                    "image_path": slide_path,
                    "title": title_chunk["title"]
                })
            else:
                # Fallback if generation fails
                slides.append(self._generate_title_slide(chunks, theme))
        else:
            # Existing local behavior
            slides.append(self._generate_title_slide(chunks, theme))
        
        # 2. Content Chunks
        for idx, chunk in enumerate(chunks, start=2):
            if provider in ["bedrock", "aws", "amazon_bedrock"]:
                # Use Premium AI Slide Generation
                slide_path = await self.bedrock_slide_gen.generate_slide_image(
                    chunk=chunk,
                    slide_num=idx,
                    theme=theme_name
                )
                if slide_path:
                    slides.append({
                        "slide_id": idx, 
                        "type": "content", 
                        "image_path": slide_path, 
                        "title": chunk["title"],
                        "bullets": chunk["key_points"]
                    })
                    continue

            # Fallback to local hybrid if not AWS or if AWS synthesis fails
            ai_background = None
            if provider in ["bedrock", "aws", "amazon_bedrock"] and chunk.get("visual_hint"):
                # (Optional: use Nova Canvas background for hybrid too)
                ai_background = await self._generate_educational_background(
                    hint=chunk.get("visual_hint", "abstract education"),
                    theme_name=theme_name
                )
            
            if idx % 3 == 0 and chunk.get("visual_hint"):
                slides.append(self._generate_diagram_slide(chunk, idx, theme, ai_background))
            else:
                layout = "split" if idx % 2 == 0 else "list"
                slides.append(self._generate_content_slide(chunk, idx, theme, layout, ai_background))
                
        # 3. Outro
        slides.append(self._generate_outro_slide(len(chunks) + 2, theme))
        
        return slides

    async def _synthesize_full_slide_bedrock(self, chunk: Dict, slide_num: int, theme_name: str) -> str:
        """100% AI Synthesis of a slide using Amazon Titan Image Generator v2"""
        model_id = "amazon.titan-image-generator-v2:0"
        
        title = chunk["title"][:80]  # Limit title length
        bullets = " | ".join(chunk["key_points"][:2])[:150]  # Limit bullets
        
        # Shortened prompt under 512 chars for Titan v2
        prompt = (
            f"Professional presentation slide: {title}. "
            f"Key points: {bullets}. "
            f"Theme: {theme_name}. Clean corporate design, high-quality typography, abstract background."
        )
        
        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 1024,
                "cfgScale": 10.0,
                "seed": random.randint(0, 100000)
            }
        })

        try:
            response = self.bedrock_runtime.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get("body").read())
            base64_image = response_body.get("images")[0]
            
            image_path = self.output_dir / f"slide_{slide_num:03d}.png"
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(base64_image))
            
            return str(image_path)
        except Exception as e:
            print(f"[-] Bedrock Synthesis failed: {e}")
            return None


    async def _generate_educational_background(self, hint: str, theme_name: str) -> str:
        """Generate educational background using Amazon Nova Canvas
        
        Creates clean, professional backgrounds optimized for text overlay
        and educational content visualization.
        """
        model_id = "amazon.nova-canvas-v1:0"
        
        # Educational-focused prompt emphasizing readability and professionalism
        educational_themes = {
            "modern_dark": "dark blue gradient, subtle geometric patterns",
            "cyber_neon": "dark tech background, neon accents, minimal",
            "elegant_light": "soft white cream, subtle texture, professional",
            "corporate_pro": "clean corporate blue grey, minimal design"
        }
        
        theme_desc = educational_themes.get(theme_name, "professional clean background")
        
        # Optimized prompt for educational slides (under 512 chars)
        prompt = (
            f"Professional educational presentation background. "
            f"Theme: {theme_desc}. "
            f"Concept: {hint[:80]}. " 
            f"Clean, minimal, perfect for text overlay, "
            f"subtle abstract elements, high quality, academic style"
        )
        
        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 1024,
                "cfgScale": 7.0,  # Lower for more subtle backgrounds
                "seed": random.randint(0, 100000)
            }
        })

        try:
            response = self.bedrock_runtime.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get("body").read())
            base64_image = response_body.get("images")[0]
            
            # Save background
            temp_path = self.output_dir / f"bg_{hash(hint)}.png"
            with open(temp_path, "wb") as f:
                f.write(base64.b64decode(base64_image))
            
            print(f"  ✓ Generated AI background")
            return str(temp_path)
            
        except Exception as e:
            print(f"  ⚠ Nova Canvas failed: {e}, using theme gradient")
            return None

    def _create_canvas(self, theme: Dict, bg_image_path: str = None) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
        if bg_image_path and os.path.exists(bg_image_path):
            img = Image.open(bg_image_path).resize((self.width, self.height))
            # Apply a slight darkening overlay to ensure text readability
            overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 160))
            img = img.convert('RGBA')
            img.alpha_composite(overlay)
            img = img.convert('RGB')
        else:
            img = Image.new('RGB', (self.width, self.height), theme["bg"])
            
        draw = ImageDraw.Draw(img, 'RGBA')
        
        if not bg_image_path:
            # Background Aesthetic: Gradient wash
            for y in range(self.height):
                alpha = y / self.height
                c = tuple(int(theme["bg"][i] + (theme["primary"][i] - theme["bg"][i]) * alpha * 0.1) for i in range(3))
                draw.line([(0, y), (self.width, y)], fill=c)
            
            # Add subtle noise/texture for premium feel
            for _ in range(100):
                nx, ny = random.randint(0, self.width), random.randint(0, self.height)
                nk = random.randint(10, 30)
                draw.point((nx, ny), fill=(*theme["primary"], nk))
            
        return img, draw

    def _generate_title_slide(self, chunks: List[Dict], theme: Dict) -> Dict:
        img, draw = self._create_canvas(theme)
        topic = chunks[0]["title"] if chunks else "Masterclass"
        
        # Big hero typography
        self._draw_centered_text(draw, topic.upper(), self.height//2 - 50, self.fonts["title"], theme["text"])
        draw.rectangle([self.width//2 - 200, self.height//2 + 50, self.width//2 + 200, self.height//2 + 60], fill=theme["accent"])
        
        image_path = self.output_dir / "slide_001.png"
        img.save(image_path)
        return {"slide_id": 1, "type": "title", "image_path": str(image_path), "title": topic}

    def _generate_content_slide(self, chunk: Dict, slide_num: int, theme: Dict, layout: str, bg_path: str = None) -> Dict:
        img, draw = self._create_canvas(theme, bg_path)
        title = chunk["title"]
        bullets = chunk["key_points"][:5]
        
        if layout == "split":
            # Header
            draw.text((100, 80), title, font=self.fonts["heading"], fill=theme["text"])
            draw.rectangle([100, 180, 250, 190], fill=theme["primary"])
            
            # Content grid
            y = 280
            for i, bullet in enumerate(bullets):
                draw.rectangle([100, y-10, 140, y+30], fill=theme["primary"])
                draw.text((105, y-5), str(i+1), font=self.fonts["body"], fill=theme["bg"])
                
                wrapped = textwrap.fill(bullet, width=50)
                lines = wrapped.count('\n') + 1
                draw.text((180, y-5), wrapped, font=self.fonts["body"], fill=theme["text"])
                y += 80 + (lines * 45) # Adaptive vertical spacing
                
                if y > self.height - 100: break # Avoid bottom clipping
                
            # Right side decorative panel with theme accent
            draw.rectangle([self.width-400, 0, self.width, self.height], fill=tuple(list(theme["accent"]) + [20]))
            
        else: # List layout
            self._draw_centered_text(draw, title, 150, self.fonts["heading"], theme["text"])
            
            y = 300
            for bullet in bullets:
                wrapped = textwrap.fill(bullet, width=65)
                lines = wrapped.count('\n') + 1
                row_h = 40 + (lines * 50)
                
                # Glass list item
                draw.rectangle([250, y, 1670, y + row_h], fill=theme["overlay"], outline=theme["primary"])
                draw.text((300, y + 20), f"• {wrapped}", font=self.fonts["body"], fill=theme["text"])
                y += row_h + 30
                
                if y > self.height - 100: break

        image_path = self.output_dir / f"slide_{slide_num:03d}.png"
        img.save(image_path)
        return {"slide_id": slide_num, "type": "content", "image_path": str(image_path), "title": title, "bullets": bullets}

    def _generate_diagram_slide(self, chunk: Dict, slide_num: int, theme: Dict, bg_path: str = None) -> Dict:
        """Draws actual geometric diagrams based on visual hints."""
        img, draw = self._create_canvas(theme, bg_path)
        title = chunk["title"]
        hint = chunk.get("visual_hint", "").lower()
        
        self._draw_centered_text(draw, title, 100, self.fonts["heading"], theme["text"])
        
        # Simple Logic: Process Flow (Boxes and Arrows)
        points = chunk["key_points"][:4]
        box_w, box_h = 350, 200
        start_x = (self.width - (len(points) * box_w + (len(points)-1) * 100)) // 2
        y = 500
        
        for i, point in enumerate(points):
            x = start_x + i * (box_w + 100)
            
            # Draw Box
            draw.rectangle([x, y, x + box_w, y + box_h], outline=theme["primary"], width=5, fill=theme["overlay"])
            
            # Draw Arrow to next
            if i < len(points) - 1:
                arrow_x = x + box_w + 10
                draw.line([(arrow_x, y + box_h // 2), (arrow_x + 80, y+box_h//2)], fill=theme["accent"], width=8)
                draw.polygon([(arrow_x + 80, y+box_h//2-20), (arrow_x+100, y+box_h//2), (arrow_x+80, y+box_h//2+20)], fill=theme["accent"])
            
            # Text inside box
            wrapped = textwrap.fill(point, width=15)
            # Center text in box vertically
            lines = wrapped.split('\n')
            total_text_height = len(lines) * 35
            cur_y = y + (box_h - total_text_height) // 2
            
            for line in lines:
                l_bbox = draw.textbbox((0, 0), line, font=self.fonts["small"])
                l_w = l_bbox[2] - l_bbox[0]
                draw.text((x + (box_w - l_w)//2, cur_y), line, font=self.fonts["small"], fill=theme["text"])
                cur_y += 35

        # Add diagram label
        draw.text((self.width//2 - 100, 850), "[SYSTEM FLOW DIAGRAM]", font=self.fonts["small"], fill=theme["accent"])

        image_path = self.output_dir / f"slide_{slide_num:03d}.png"
        img.save(image_path)
        return {"slide_id": slide_num, "type": "diagram", "image_path": str(image_path), "title": title, "bullets": points}

    def _generate_outro_slide(self, slide_num: int, theme: Dict) -> Dict:
        img, draw = self._create_canvas(theme)
        self._draw_centered_text(draw, "LESSON SUMMARY", 400, self.fonts["heading"], theme["primary"])
        self._draw_centered_text(draw, "Scanning complete. Knowledge uploaded.", 550, self.fonts["body"], theme["text"])
        
        image_path = self.output_dir / f"slide_{slide_num:03d}.png"
        img.save(image_path)
        return {"slide_id": slide_num, "type": "outro", "image_path": str(image_path)}

    def _draw_centered_text(self, draw: ImageDraw, text: str, y: int, font: ImageFont, color: tuple):
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), text, fill=color, font=font)
