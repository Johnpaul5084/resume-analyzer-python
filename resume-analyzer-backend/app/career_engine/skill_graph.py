from typing import List, Dict

class SkillGraph:
    """
    Lightweight Skill Graph Logic.
    Removed NetworkX to save RAM. Uses simple list processing.
    """

    @staticmethod
    def get_skill_dependencies(primary_skill: str) -> List[Dict[str, str]]:
        # Define some basic dependencies matching the ontology
        deps = {
            "Machine Learning": ["Python", "Statistics", "Linear Algebra"],
            "DevOps": ["Docker", "Linux", "CI/CD"],
            "Full Stack": ["JavaScript", "React", "Node.js", "SQL"],
            "SDE": ["DSA", "Operating Systems", "Networking", "Database"]
        }
        
        if primary_skill not in deps:
            return []
            
        return [{"from": primary_skill, "to": d} for d in deps[primary_skill]]
