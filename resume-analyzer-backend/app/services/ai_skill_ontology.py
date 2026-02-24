import re
from typing import Dict, List, Set

class SkillOntology:
    """
    AI Skill Ontology & Taxonomy
    Definitions of skill clusters for semantic matching.
    """
    
    CLUSTERS = {
        "Data Science": {
            "Core": ["Python", "R", "SQL", "Statistics", "Machine Learning"],
            "Libraries": ["Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Keras"],
            "Concepts": ["Feature Engineering", "A/B Testing", "Deep Learning", "NLP", "Computer Vision"],
            "Tools": ["Tableau", "Power BI", "Jupyter", "MLflow"]
        },
        "Web Development": {
            "Frontend": ["React", "Angular", "Vue", "JavaScript", "TypeScript", "HTML5", "CSS3", "Tailwind"],
            "Backend": ["Node.js", "Express", "Django", "FastAPI", "Flask", "Spring Boot", "Go"],
            "Database": ["PostgreSQL", "MongoDB", "MySQL", "Redis", "Elasticsearch"],
            "DevOps": ["Docker", "Kubernetes", "CI/CD", "AWS", "Azure", "GCP", "Nginx"]
        },
        "Software Engineering": {
            "Languages": ["C++", "Java", "C#", "Rust", "Go"],
            "Fundamentals": ["Algorithms", "Data Structures", "System Design", "Design Patterns"],
            "Practices": ["Unit Testing", "Microservices", "TDD", "Agile", "Scrum"]
        }
    }

    @staticmethod
    def identify_primary_cluster(skills: List[str]) -> str:
        """Determines the most likely career path based on skills."""
        scores = {}
        skills_lower = [s.lower() for s in skills]
        
        for cluster, categories in SkillOntology.CLUSTERS.items():
            count = 0
            for cat_skills in categories.values():
                for s in cat_skills:
                    if s.lower() in skills_lower:
                        count += 1
            scores[cluster] = count
            
        return max(scores, key=scores.get) if any(scores.values()) else "General Engineering"

    @staticmethod
    def get_missing_skills(cluster: str, user_skills: List[str]) -> List[str]:
        """Finds gaps in the user's skillset for a target cluster."""
        if cluster not in SkillOntology.CLUSTERS:
            return []
            
        required = []
        for cat_skills in SkillOntology.CLUSTERS[cluster].values():
            required.extend(cat_skills)
            
        user_skills_lower = [s.lower() for s in user_skills]
        missing = [s for s in required if s.lower() not in user_skills_lower]
        
        return missing[:5] # Return top 5 gaps
