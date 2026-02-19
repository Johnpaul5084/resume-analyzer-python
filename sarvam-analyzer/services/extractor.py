import re
from ..utils.constants import SKILLS_DB

class ResumeExtractor:
    @staticmethod
    def extract_details(text):
        """Extract name, email, phone, and skills using patterns."""
        details = {
            "name": ResumeExtractor._extract_name(text),
            "email": ResumeExtractor._extract_email(text),
            "phone": ResumeExtractor._extract_phone(text),
            "skills": ResumeExtractor._extract_skills(text),
            "education": ResumeExtractor._extract_education(text),
            "experience": ResumeExtractor._extract_experience(text)
        }
        return details

    @staticmethod
    def _extract_name(text):
        # Basic name extraction (usually the first line or capitalized words)
        # For simplicity in a beginner project, take the first 2-3 words
        lines = text.strip().split('\n')
        if lines:
            name_match = re.search(r"^([A-Z][a-z]+)\s([A-Z][a-z]+)", lines[0])
            if name_match:
                return name_match.group(0)
        return "Not found"

    @staticmethod
    def _extract_email(text):
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else "Not found"

    @staticmethod
    def _extract_phone(text):
        pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        match = re.search(pattern, text)
        return match.group(0) if match else "Not found"

    @staticmethod
    def _extract_skills(text):
        found_skills = []
        for skill in SKILLS_DB:
            # Use word boundaries to avoid partial matches (e.g., 'C' in 'CAT')
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found_skills.append(skill)
        return list(set(found_skills))

    @staticmethod
    def _extract_education(text):
        patterns = ["B.E", "B.Tech", "M.Tech", "B.Sc", "M.Sc", "PhD", "Bachelor", "Master", "University", "College"]
        found = []
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                # Try to capture the context around the education keyword
                match = re.search(r'([^.!\n]*' + p + r'[^.!\n]*)', text, re.IGNORECASE)
                if match:
                    found.append(match.group(0).strip())
        return list(set(found))[:3] # Limit to top 3 matches

    @staticmethod
    def _extract_experience(text):
        # Look for "years" near numbers
        match = re.search(r'(\d+)\+?\s*years?', text, re.IGNORECASE)
        return match.group(0) if match else "Entry Level / Internship"
