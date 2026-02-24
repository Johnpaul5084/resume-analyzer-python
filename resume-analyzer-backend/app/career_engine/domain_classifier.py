from typing import List, Dict

class DomainClassifier:
    """
    AI Domain Intelligence
    Classifies profile into IT, Core, or Non-IT based on extracted skills.
    """
    
    DOMAINS = {
        "Software & AI": ["python", "java", "sql", "react", "node.js", "machine learning", "fastapi", "docker", "aws", "git"],
        "Core Engineering": ["solidworks", "autocad", "vlsi", "embedded", "iot", "staad", "ansys", "matlab", "vhdl"],
        "Business & Management": ["excel", "data analysis", "marketing", "product management", "operations", "hr", "finance"]
    }

    @staticmethod
    def classify_profile(skills: List[str]) -> str:
        skills_lower = [s.lower() for s in skills]
        counts = {domain: 0 for domain in DomainClassifier.DOMAINS}
        
        for domain, keywords in DomainClassifier.DOMAINS.items():
            for skill in skills_lower:
                if any(kw in skill for kw in keywords):
                    counts[domain] += 1
        
        # Determine best fit
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        primary_domain, score = sorted_counts[0]
        
        if score == 0:
            return "General Professional"
        return primary_domain
