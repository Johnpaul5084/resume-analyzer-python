import networkx as nx
from typing import List, Dict

class SkillGraph:
    """
    AI Skill Graph Logic
    Visualizes skill dependencies using NetworkX.
    """

    @staticmethod
    def get_skill_dependencies(primary_skill: str) -> List[Dict[str, str]]:
        G = nx.DiGraph()
        
        # Define some basic dependencies
        deps = {
            "Machine Learning": ["Python", "Statistics", "Linear Algebra"],
            "DevOps": ["Docker", "Linux", "CI/CD"],
            "Full Stack": ["JavaScript", "React", "Node.js", "SQL"],
            "SDE": ["DSA", "Operating Systems", "Networking", "Database"]
        }
        
        if primary_skill not in deps:
            return []
            
        return [{"from": primary_skill, "to": d} for d in deps[primary_skill]]
