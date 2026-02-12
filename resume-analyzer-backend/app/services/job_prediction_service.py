from transformers import pipeline
import torch
import logging

logger = logging.getLogger(__name__)

class JobPredictionService:
    _classifier = None

    @classmethod
    def get_classifier(cls):
        if cls._classifier is None:
            try:
                # Use a smaller, faster model for CPU inference and deployment (much lighter than facebook/bart-large-mnli)
                cls._classifier = pipeline("zero-shot-classification", 
                                         model="valhalla/distilbart-mnli-12-1", 
                                         device=-1) # -1 for CPU
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load generic job prediction model: {e}")
                return None
        return cls._classifier

    @staticmethod
    def predict_job_role(resume_text: str, candidate_labels: list = None) -> dict:
        """
        Predicts the most suitable job role based on resume text using Zero-Shot Classification.
        """
        if not candidate_labels:
            candidate_labels = [
                # IT & Tech
                "Software Engineer", "Data Scientist", "Data Analyst", "Product Manager",
                "Full Stack Developer", "DevOps Engineer", "Cybersecurity Analyst", "UI/UX Designer",
                
                # Engineering (Non-IT)
                "Civil Engineer", "Mechanical Engineer", "Electrical Engineer", 
                "Chemical Engineer", "Automobile Engineer",
                
                # Medical & Healthcare
                "Medical Doctor", "Nurse", "Pharmacist", "Biotechnologist", "Clinical Researcher",
                
                # Business & Management
                "Business Analyst", "Marketing Manager", "HR Manager", "Financial Analyst",
                "Sales Representative", "Operations Manager", "Supply Chain Manager",
                
                # Creative & Arts
                "Graphic Designer", "Content Writer", "Digital Marketer", "Video Editor",
                
                # Education & Others
                "Teacher", "Professor", "Legal Advisor", "Customer Support Specialist"
            ]
        
        classifier = JobPredictionService.get_classifier()
        if not classifier:
            return {"error": "Model not loaded"}

        # Truncate text to fit model context (usually 1024 tokens)
        # BART can handle longer but let's be safe and concise
        truncated_text = resume_text[:2000] 

        try:
            result = classifier(truncated_text, candidate_labels, multi_label=False)
            
            # Format result
            predictions = []
            for label, score in zip(result['labels'], result['scores']):
                predictions.append({
                    "role": label,
                    "confidence": round(score * 100, 2)
                })
            
            # Return top 5
            return predictions[:5]
        except Exception as e:
            logger.error(f"Error during job prediction: {e}")
            return {"error": str(e)}

    @staticmethod
    def validate_content_with_bert(text: str) -> dict:
        """
        Uses BERT (specifically a quality/grammar model if available, or just sentiment/logic)
        to validate content quality. Here we use a simple sentiment check as a proxy for 'positive/professional tone',
        or we could use a specific grammar checker.
        
        For 'checking BERT and validation', we can use a 'text-classification' pipeline 
        to check if the text sounds 'professional' or 'casual' if we had such a model.
        
        For now, let's use a standard grammar checking approach or simple quality heuristic.
        Transformer-based grammar checking is heavy.
        """
        # Placeholder for complex BERT-based validation
        # In a real scenario, you'd fine-tune a BERT model on 'good' vs 'bad' resumes.
        pass
