from typing import List, Dict

class RoadmapGenerator:
    """
    IRIS Career Roadmap Generator
    Generates time-bound milestones for career goals.
    """

    @staticmethod
    def generate_roadmap(target_role: str, timeline_months: int = 6) -> List[Dict[str, str]]:
        if "Data Scientist" in target_role:
            return [
                {"period": "Month 1-2", "focus": "Statistical Foundations & Python for Data Science"},
                {"period": "Month 3", "focus": "Machine Learning Algorithms & Model Evaluation"},
                {"period": "Month 4", "focus": "Advanced SQL & Feature Engineering"},
                {"period": "Month 5", "focus": "End-to-End Capstone Project & Deployment"},
                {"period": "Month 6", "focus": "Advanced Resume Building & Mock Interviews"}
            ]
        
        # Default SDE Roadmap
        return [
            {"period": "Month 1-2", "focus": "Data Structures & Algorithms (Advanced Level)"},
            {"period": "Month 3", "focus": "System Design Fundamentals"},
            {"period": "Month 4", "focus": "Full Stack / Mobile Development Projects"},
            {"period": "Month 5", "focus": "Open Source Contributions & Portfolio Building"},
            {"period": "Month 6", "focus": "Mock Interviews & Soft Skill Refinement"}
        ]
