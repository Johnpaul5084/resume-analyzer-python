import base64
from typing import List

class SkillGraphVisualizer:
    """
    Lightweight Skill Graph Visualizer.
    Removed Matplotlib and NetworkX to save 300MB+ RAM.
    Returns a placeholder or SVG-based representation.
    """
    @staticmethod
    def generate_skill_graph(user_skills: List[str], target_role_skills: List[str]) -> str:
        # Returning a very simple base64 placeholder for now
        # In a real app, you'd use a JS library for the graph instead of generating on backend
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
