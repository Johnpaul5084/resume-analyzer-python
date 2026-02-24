import logging
import pdfplumber
import docx
from fastapi import UploadFile
import io
import re
from app.services.ocr_service import OCRService

logger = logging.getLogger(__name__)

class AIRawParser:
    @staticmethod
    async def extract_text(file: UploadFile) -> str:
        content = await file.read()
        await file.seek(0) # Reset file pointer for subsequent reads
        file_type = file.filename.split('.')[-1].lower()
        
        extracted_text = ""
        
        try:
            if file_type == 'pdf':
                # Use OCR Service which handles both text-based and scanned PDFs
                extracted_text = await OCRService.extract_text_from_bytes(content, 'pdf')
                    
            elif file_type in ['docx', 'doc']:
                try:
                    doc = docx.Document(io.BytesIO(content))
                    extracted_text = "\n".join([para.text for para in doc.paragraphs])
                except Exception as e:
                    logger.error(f"Error parsing DOCX: {e}")
                    raise ValueError("Failed to parse DOCX file.")
            
            elif file_type in ['jpg', 'jpeg', 'png']:
                # New: Support for image-based resumes
                extracted_text = await OCRService.extract_text_from_bytes(content, file_type)

            elif file_type == 'txt':
                extracted_text = content.decode('utf-8')
                
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            if not extracted_text.strip():
                logger.warning(f"No text extracted from {file_type} file.")

            # Basic cleanup
            extracted_text = re.sub(r'\s+', ' ', extracted_text).strip()
            return extracted_text

        except Exception as e:
            logger.error(f"Parser Error: {str(e)}")
            raise e
    
    @staticmethod
    def extract_sections(text: str) -> dict:
        """
        Heuristic-based section extraction.
        """
        sections = {
            "contact_info": "",
            "summary": "",
            "experience": "",
            "education": "",
            "skills": "",
            "projects": "",
            "certifications": ""
        }
        
        text_lower = text.lower()
        
        # Simple regex-based splitting (can be improved with ML/NER)
        keywords = {
            "experience": ["experience", "work history", "employment"],
            "education": ["education", "academic", "qualifications"],
            "skills": ["skills", "technologies", "competencies"],
            "projects": ["projects", "personal projects"],
            "certifications": ["certifications", "courses", "achievements"],
            "summary": ["summary", "profile", "objective"]
        }
        
        # This is a simplified extraction logic
        # In a real-world scenario, you might use strict regex or layout analysis
        
        current_section = "contact_info"
        lines = text.split('\n') # If we preserved newlines
        
        # If text was flattened, we can try to split by known headers
        # For now, let's just return the full text in 'raw' and do
        # basic keyword search for entire blocks if possible.
        
        # Robust implementation requires preserving layout or smart segmentation.
        # Here we just return the raw text for NLP analysis as a single block for now,
        # but structured data is better.
        
        return {"raw_text": text} # Placeholder for complex logic
