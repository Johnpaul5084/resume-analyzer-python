import faiss
import numpy as np
import json
import os
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class SemanticRoleMatcher:
    _model = None
    _index = None
    _role_names = []
    
    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._model

    @classmethod
    def _initialize_index(cls):
        db_path = os.path.join(os.path.dirname(__file__), "role_database.json")
        if not os.path.exists(db_path):
            return
            
        with open(db_path) as f:
            roles = json.load(f)
            
        role_texts = []
        cls._role_names = []
        
        for name, data in roles.items():
            combined = f"{name} {' '.join(data.get('mandatory_skills', []))} {data.get('category', '')}"
            role_texts.append(combined)
            cls._role_names.append(name)
            
        model = cls.get_model()
        embeddings = model.encode(role_texts)
        
        dimension = embeddings.shape[1]
        cls._index = faiss.IndexFlatL2(dimension)
        cls._index.add(np.array(embeddings))

    @classmethod
    def find_best_roles(cls, resume_text: str, top_k: int = 3):
        if cls._index is None:
            cls._initialize_index()
            
        if cls._index is None:
            return ["Software Engineer"]
            
        model = cls.get_model()
        resume_embedding = model.encode([resume_text])
        
        distances, indices = cls._index.search(np.array(resume_embedding), top_k)
        
        results = []
        for i in indices[0]:
            if i < len(cls._role_names):
                results.append(cls._role_names[i])
        return results
