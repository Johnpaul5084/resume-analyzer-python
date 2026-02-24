import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AIParserService:
    """
    AI Resume Analyzer Parser
    Uses spaCy NER and rule-based extraction for high-fidelity structured data.
    IIT/IIIT Level Implementation
    """
    
    _nlp = None

    @classmethod
    def get_nlp(cls):
        if cls._nlp is None:
            try:
                import spacy
                cls._nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.error(f"Failed to load spaCy model: {e}")
                return None
        return cls._nlp

    @staticmethod
    def extract_structured_data(text: str) -> Dict[str, Any]:
        """
        Main entry point for structured extraction.
        """
        nlp = AIParserService.get_nlp()
        doc = nlp(text) if nlp else None
        
        return {
            "personal_info": AIParserService._extract_personal_info(text, doc),
            "education": AIParserService._extract_education(text, doc),
            "experience": AIParserService._extract_experience(text, doc),
            "skills": AIParserService._extract_skills(text, doc),
            "projects": AIParserService._extract_projects(text, doc),
            "entities": [(ent.text, ent.label_) for ent in doc.ents] if doc else []
        }

    @staticmethod
    def _extract_personal_info(text: str, doc) -> Dict[str, str]:
        email = re.search(r'[\w\.-]+@[\w\.-]+', text)
        phone = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        
        name = ""
        if doc:
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text
                    break
                    
        return {
            "name": name,
            "email": email.group() if email else "",
            "phone": phone.group() if phone else ""
        }

    @staticmethod
    def _extract_skills(text: str, doc) -> List[str]:
        """
        IIT Level: Uses a combination of predefined skill sets and NER.
        """
        # Common skill keywords (expandable)
        skill_db = {
            "python", "java", "cpp", "javascript", "react", "node", "express", "fastapi",
            "mongodb", "postgresql", "mysql", "docker", "kubernetes", "aws", "azure", "gcp",
            "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
            "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "tableau", "powerbi",
            "git", "github", "ci/cd", "agile", "scrum", "project management", "leadership",
            "communication", "teamwork", "problem solving", "critical thinking"
        }
        
        found_skills = set()
        text_lower = text.lower()
        
        # Rule-based match
        for skill in skill_db:
            if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                found_skills.add(skill.capitalize())
        
        # Entity match (for uncommon skills)
        if doc:
            for ent in doc.ents:
                if ent.label_ in ["PRODUCT", "ORG", "WORK_OF_ART"] and len(ent.text) < 20:
                    # Often technologies are picked up as ORG or PRODUCT
                    found_skills.add(ent.text)
                    
        return list(found_skills)

    @staticmethod
    def _extract_education(text: str, doc) -> List[str]:
        edu_keywords = ["Bachelor", "Master", "B.Tech", "M.Tech", "B.Sc", "M.Sc", "PhD", "University", "IIT", "NIT", "College"]
        found_edu = []
        for line in text.split('\n'):
            if any(kw in line for kw in edu_keywords):
                found_edu.append(line.strip())
        return found_edu[:3]

    @staticmethod
    def _extract_experience(text: str, doc) -> List[str]:
        # Simple heuristic: look for lines with dates and job titles
        # In a real IIT project, we'd use a more complex dependency parser
        return []

    @staticmethod
    def _extract_projects(text: str, doc) -> List[str]:
        return []
