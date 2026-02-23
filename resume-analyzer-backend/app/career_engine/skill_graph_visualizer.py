import networkx as nx
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from typing import List

class SkillGraphVisualizer:
    SKILL_ONTOLOGY_MAP = {
        "Python": ["Machine Learning", "Backend Development", "Data Analysis"],
        "Machine Learning": ["Deep Learning", "NLP", "Computer Vision"],
        "SQL": ["Data Engineering", "Backend Development"],
        "JavaScript": ["React", "Node.js", "Vue.js"],
        "React": ["Frontend Engineering"],
        "Node.js": ["Full Stack Development"],
        "Docker": ["DevOps", "Cloud Computing"],
        "AWS": ["Cloud Engineering", "DevOps"],
        "SolidWorks": ["Mechanical Design"],
        "AutoCAD": ["Civil Engineering", "Mechanical Design"]
    }

    @staticmethod
    def generate_skill_graph(user_skills: List[str], target_role_skills: List[str]) -> str:
        plt.clf() # Clear current figure
        G = nx.DiGraph()
        
        # Build graph from ontology
        for parent, children in SkillGraphVisualizer.SKILL_ONTOLOGY_MAP.items():
            for child in children:
                G.add_edge(parent, child)
        
        # Identify colors
        user_skills_set = set(s.lower() for s in user_skills)
        target_skills_set = set(s.lower() for s in target_role_skills)
        
        node_colors = []
        for node in G.nodes():
            n_lower = node.lower()
            if n_lower in user_skills_set:
                node_colors.append("#10b981") # Green
            elif n_lower in target_skills_set:
                node_colors.append("#ef4444") # Red
            else:
                node_colors.append("#e2e8f0") # Gray
        
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        nx.draw(G, pos, with_labels=True, node_color=node_colors, 
                node_size=2500, font_size=9, font_weight="bold",
                arrows=True, edge_color="#cbd5e1", width=1.5)
        
        # Buffer save
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_str
