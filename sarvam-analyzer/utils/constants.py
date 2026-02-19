# Common skills list for ATS matching
SKILLS_DB = [
    "Python", "Java", "Javascript", "Typescript", "React", "Angular", "Vue", "Node.js", 
    "Express", "Flask", "Django", "FastAPI", "SQL", "NoSQL", "MongoDB", "PostgreSQL", 
    "MySQL", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Git", "C++", 
    "C#", "PHP", "Laravel", "Swift", "Kotlin", "Machine Learning", "Deep Learning", 
    "Data Analysis", "Tableau", "PowerBI", "R", "Unity", "Unreal Engine", "Solidity", 
    "TensorFlow", "PyTorch", "Scikit-Learn", "NLTK", "Spacy", "PowerShell", "Linux"
]

# Supported file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Default error messages
ERROR_MESSAGES = {
    "FILE_NOT_ALLOWED": "File type not supported. Please upload PDF, PNG, or JPG.",
    "OCR_FAILED": "Failed to extract text from the document.",
    "PARSING_FAILED": "Failed to parse resume content.",
    "API_ERROR": "Error connecting to AI service."
}
