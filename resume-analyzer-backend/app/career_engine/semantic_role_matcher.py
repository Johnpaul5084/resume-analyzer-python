from app.core.ai_model import AIModelManager
import faiss
import numpy as np
import json
import os
import logging

logger = logging.getLogger(__name__)

class SemanticRoleMatcher:
    _index = None
    _role_names = []
    
    @classmethod
    def _initialize_index(cls):
        db_path = os.path.join(os.path.dirname(__file__), "role_database.json")
        if not os.path.exists(db_path):
            return
            
        with open(db_path, encoding='utf-8') as f:
            roles = json.load(f)
            
        role_texts = []
        cls._role_names = []
        
        for name, data in roles.items():
            combined = f"{name} {' '.join(data.get('mandatory_skills', []))} {data.get('category', '')}"
            role_texts.append(combined)
            cls._role_names.append(name)
            
        model = AIModelManager.get_model()
        embeddings = model.encode(role_texts)
        
        dimension = embeddings.shape[1]
        cls._index = faiss.IndexFlatL2(dimension)
        cls._index.add(np.array(embeddings))

    @classmethod
    def find_best_roles(cls, resume_text: str, top_k: int = 3):
        try:
            if cls._index is None:
                cls._initialize_index()
                
            if cls._index is None:
                return ["Software Engineer"]
                
            model = AIModelManager.get_model()
            resume_embedding = model.encode([resume_text])
            
            distances, indices = cls._index.search(np.array(resume_embedding), top_k)
            
            results = []
            for i in indices[0]:
                if i != -1 and i < len(cls._role_names):
                    results.append(cls._role_names[i])
            return results if results else ["Software Engineer"]
        except Exception as e:
            logger.error(f"SemanticRoleMatcher error: {e}")
            return ["Software Engineer"]
