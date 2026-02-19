import os
import re
from werkzeug.utils import secure_filename
from .constants import ALLOWED_EXTENSIONS

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_text(text):
    """Remove special characters and extra whitespace from text."""
    # Remove non-ascii characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Replace newlines/tabs with spaces
    text = re.sub(r'[\n\t\r]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def setup_directories(base_path):
    """Ensure necessary directories exist."""
    dirs = ['uploads', 'routes', 'services', 'utils', 'templates', 'static/css', 'static/js']
    for d in dirs:
        os.makedirs(os.path.join(base_path, d), exist_ok=True)

def handle_file_upload(file, upload_folder):
    """Securely save the uploaded file."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return file_path
    return None
