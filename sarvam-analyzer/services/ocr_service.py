import os
import requests
import pdfplumber
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from dotenv import load_dotenv

load_dotenv()

# Configure Tesseract path for Windows if specified in .env
tess_path = os.getenv("TESSERACT_PATH")
if tess_path:
    pytesseract.pytesseract.tesseract_cmd = tess_path

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_OCR_URL = "https://api.sarvam.ai/v1/vision/ocr"

class OCRService:
    @staticmethod
    def extract_text(file_path):
        """Main entry point to extract text based on file type."""
        ext = file_path.split('.')[-1].lower()
        
        if ext == 'pdf':
            return OCRService._process_pdf(file_path)
        elif ext in ['jpg', 'jpeg', 'png']:
            return OCRService._process_image(file_path)
        return ""

    @staticmethod
    def _process_pdf(file_path):
        """Extract text from PDF using pdfplumber, fallback to OCR if scanned."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # If no text extracted, it's likely a scanned PDF
            if not text.strip():
                print("Scanned PDF detected. Triggering OCR...")
                return OCRService._ocr_scanned_pdf(file_path)
            
            return text
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return OCRService._ocr_scanned_pdf(file_path)

    @staticmethod
    def _ocr_scanned_pdf(file_path):
        """Convert PDF pages to images and run OCR."""
        try:
            images = convert_from_path(file_path)
            full_text = ""
            for img in images:
                # Save temp image for processing
                temp_img_path = "temp_page.png"
                img.save(temp_img_path, "PNG")
                full_text += OCRService._process_image(temp_img_path) + "\n"
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
            return full_text
        except Exception as e:
            print(f"OCR Scanned PDF Error: {e}")
            return ""

    @staticmethod
    def _process_image(file_path):
        """Send image to Sarvam AI OCR, fallback to Tesseract."""
        if not SARVAM_API_KEY:
            print("Sarvam API Key missing. Falling back to Tesseract.")
            return OCRService._tesseract_fallback(file_path)

        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                headers = {"api-subscription-key": SARVAM_API_KEY}
                response = requests.post(SARVAM_OCR_URL, files=files, headers=headers, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                # Assuming Sarvam returns text in a specific key based on docs
                return data.get("text", "") 
            else:
                print(f"Sarvam AI OCR failed ({response.status_code}). Trying Tesseract.")
                return OCRService._tesseract_fallback(file_path)
        except Exception as e:
            print(f"Sarvam AI Exception: {e}. Trying Tesseract.")
            return OCRService._tesseract_fallback(file_path)

    @staticmethod
    def _tesseract_fallback(file_path):
        """Local OCR fallback using Tesseract."""
        try:
            return pytesseract.image_to_string(Image.open(file_path))
        except Exception as e:
            print(f"Tesseract Error: {e}")
            return ""
