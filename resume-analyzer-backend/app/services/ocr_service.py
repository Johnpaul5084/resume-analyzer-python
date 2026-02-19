import os
import requests
import pdfplumber
import pytesseract
from PIL import Image
import io
from pdf2image import convert_from_bytes
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Tesseract path for Windows
if os.path.exists(settings.TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

SARVAM_API_KEY = settings.SARVAM_API_KEY
SARVAM_OCR_URL = "https://api.sarvam.ai/v1/vision/ocr"

class OCRService:
    @staticmethod
    async def extract_text_from_bytes(content: bytes, file_type: str) -> str:
        """
        Phoenix Upgrade: High-Fidelity Multi-Stage Extraction
        1. Native PDF Extraction (Fastest)
        2. Sarvam AI Vision OCR (Best for Indian/Complex layouts)
        3. Tesseract Fallback (Local)
        """
        if file_type == 'pdf':
            return await OCRService._process_pdf(content)
        elif file_type in ['jpg', 'jpeg', 'png']:
            return await OCRService._process_image_bytes(content)
        return ""

    @staticmethod
    async def _process_pdf(content: bytes) -> str:
        """Extract text from PDF, fallback to OCR if scanned or complex."""
        text = ""
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # Heuristic: If text is very short but pages exist, it's likely scanned
            if len(text.strip()) < 50:
                logger.info("Complex or Scanned PDF detected. Triggering High-Fidelity OCR...")
                return await OCRService._ocr_scanned_pdf(content)
            
            return text
        except Exception as e:
            logger.error(f"Native PDF parsing failed: {e}. Falling back to Vision.")
            return await OCRService._ocr_scanned_pdf(content)

    @staticmethod
    async def _ocr_scanned_pdf(content: bytes) -> str:
        """High-Fidelity: Convert PDF pages to high-res images and run Sarvam AI."""
        try:
            # High DPI for better OCR accuracy
            images = convert_from_bytes(content, dpi=300)
            full_text = ""
            for img in images:
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # Process each page with Vision
                page_text = await OCRService._process_image_bytes(img_bytes)
                full_text += page_text + "\n"
                
            return full_text
        except Exception as e:
            logger.error(f"High-Res OCR Error: {e}")
            return ""

    @staticmethod
    async def _process_image_bytes(img_bytes: bytes) -> str:
        """Send image to Sarvam AI (Akshar Vision) for high-accuracy extraction."""
        if not SARVAM_API_KEY:
            return OCRService._tesseract_fallback_bytes(img_bytes)

        try:
            # Akshar Vision handles complex Indian/English layouts perfectly
            files = {"file": ("image.png", img_bytes, "image/png")}
            headers = {"api-subscription-key": SARVAM_API_KEY}
            
            # Using higher timeout for vision tasks
            response = requests.post(SARVAM_OCR_URL, files=files, headers=headers, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                extracted = data.get("text", "")
                if extracted.strip():
                    return extracted
                
            logger.warning(f"Sarvam Vision failed ({response.status_code}). Trying Tesseract.")
            return OCRService._tesseract_fallback_bytes(img_bytes)
            
        except Exception as e:
            logger.error(f"Vision API Exception: {e}")
            return OCRService._tesseract_fallback_bytes(img_bytes)

    @staticmethod
    def _tesseract_fallback_bytes(img_bytes: bytes) -> str:
        """Local fallback ensures project works even without internet/API credits."""
        try:
            img = Image.open(io.BytesIO(img_bytes))
            # Use --oem 1 --psm 3 for best general accuracy
            custom_config = r'--oem 3 --psm 6'
            return pytesseract.image_to_string(img, config=custom_config)
        except Exception as e:
            logger.error(f"Local OCR Critical Failure: {e}")
            return ""

