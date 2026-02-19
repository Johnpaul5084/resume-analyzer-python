from flask import Blueprint, request, jsonify
from ..services.ocr_service import OCRService
from ..services.extractor import ResumeExtractor
from ..services.ats_engine import ATSEngine
from ..utils.helpers import handle_file_upload
import os

main_bp = Blueprint('main', __name__)

# Root directory of the package to locate uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@main_bp.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400
    
    file = request.files['resume']
    jd = request.form.get('job_description', '')

    if not jd:
        return jsonify({"error": "Job description is missing"}), 400

    # 1. Save File
    file_path = handle_file_upload(file, UPLOAD_FOLDER)
    if not file_path:
        return jsonify({"error": "Invalid file type"}), 400

    try:
        # 2. Extract Text via OCR Logic
        text = OCRService.extract_text(file_path)
        if not text.strip():
            return jsonify({"error": "Could not extract text from file"}), 500

        # 3. Parse Entities
        extracted_data = ResumeExtractor.extract_details(text)

        # 4. Calculate ATS Score
        ats_results = ATSEngine.calculate_score(extracted_data['skills'], jd)

        # 5. Cleanup (optional, keep for debugging or delete)
        # os.remove(file_path)

        return jsonify({
            "status": "success",
            "resume_data": extracted_data,
            "ats_analysis": ats_results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "alive"}), 200
