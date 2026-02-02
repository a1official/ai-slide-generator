"""
Ingestion Agent
Responsibility: Extract and clean text from PDF/DOCX/TXT files
"""

import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from docx import Document
from pathlib import Path
from typing import Dict, Any
import re


class IngestionAgent:
    """Extracts clean text from various document formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Main entry point for file processing
        
        Args:
            file_path: Path to the document file
            
        Returns:
            {
                "raw_text": "...",
                "metadata": {
                    "pages": 12,
                    "source": "pdf",
                    "filename": "document.pdf"
                }
            }
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self._process_pdf(file_path)
        elif extension == '.docx':
            return self._process_docx(file_path)
        elif extension == '.txt':
            return self._process_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text and render pages as images for Vision-based analysis"""
        try:
            # Extract text with pdfplumber
            raw_text = ""
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                raw_text = "\n\n".join(text_parts)
            
            if not raw_text.strip():
                raw_text = self._extract_with_pymupdf(file_path)
            
            # Render pages as images (for Vision models)
            page_images = []
            doc = fitz.open(file_path)
            temp_img_dir = Path("./temp/pdf_pages")
            temp_img_dir.mkdir(parents=True, exist_ok=True)
            
            # Render max 5 pages for vision to save tokens/time
            total_pages = len(doc)
            for i in range(min(5, total_pages)):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # High res
                img_path = temp_img_dir / f"page_{i}.png"
                pix.save(str(img_path))
                page_images.append(str(img_path))
            doc.close()

            cleaned_text = self._clean_text(raw_text)
            
            return {
                "raw_text": cleaned_text,
                "page_images": page_images,
                "metadata": {
                    "pages": total_pages,
                    "source": "pdf",
                    "filename": file_path.name
                }
            }
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _extract_with_pymupdf(self, file_path: Path) -> str:
        """Fallback PDF extraction using PyMuPDF"""
        doc = fitz.open(file_path)
        text_parts = []
        
        for page in doc:
            text_parts.append(page.get_text())
        
        doc.close()
        return "\n\n".join(text_parts)
    
    def _process_docx(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            raw_text = "\n\n".join(paragraphs)
            cleaned_text = self._clean_text(raw_text)
            
            return {
                "raw_text": cleaned_text,
                "metadata": {
                    "pages": len(doc.sections),
                    "source": "docx",
                    "filename": file_path.name
                }
            }
        except Exception as e:
            raise Exception(f"Error processing DOCX: {str(e)}")
    
    def _process_txt(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            
            cleaned_text = self._clean_text(raw_text)
            
            return {
                "raw_text": cleaned_text,
                "metadata": {
                    "pages": 1,
                    "source": "txt",
                    "filename": file_path.name
                }
            }
        except Exception as e:
            raise Exception(f"Error processing TXT: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing:
        - Headers and footers
        - Page numbers
        - Excessive whitespace
        - Special characters
        """
        # Remove page numbers (common patterns)
        text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove common header/footer patterns
        text = re.sub(r'^.*?confidential.*?$', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Trim
        text = text.strip()
        
        return text


# Example usage
if __name__ == "__main__":
    agent = IngestionAgent()
    
    # Test with a sample file
    # result = agent.process_file("sample.pdf")
    # print(result["raw_text"][:500])
    # print(result["metadata"])
