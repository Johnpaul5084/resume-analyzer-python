from app.core.ai_model import AIModelManager
import faiss
import numpy as np
import json
import os
import logging

logger = logging.getLogger(__name__)

# Global index and role tracking
_index = None
_role_names = []

def build_index():
    global _index, _role_names
    
    logger.info("⚡ Initializing AI RAG Engine...")
    
    # 1. Load Model (Shared instance)
    try:
        model = AIModelManager.get_model()
    except Exception as e:
        logger.error(f"Failed to get AI model for RAG: {e}")
        return
    
    # 2. Load Knowledge Base
    db_path = os.path.join(os.path.dirname(__file__), "role_database.json")
    if not os.path.exists(db_path):
        logger.error(f"❌ Role Database not found at {db_path}")
        return

    with open(db_path, encoding='utf-8') as f:
        roles = json.load(f)

    role_texts = []
    _role_names = []

    for role, data in roles.items():
        # GROUNDED CONTEXT: Role + Mandatory Skills + Description
        text = f"Role: {role}. Mandatory Skills: {', '.join(data.get('mandatory_skills', []))}. Description: {data.get('description', 'Professional career path.')}"
        role_texts.append(text)
        _role_names.append(role)

    if not role_texts:
        logger.warning("⚠️ No roles found to index.")
        return

    # 3. Create Embeddings
    embeddings = model.encode(role_texts)
    
    # 4. Build FAISS Index
    dimension = embeddings.shape[1]
    _index = faiss.IndexFlatL2(dimension)
    _index.add(np.array(embeddings))
    
    logger.info(f"✅ AI RAG Index built with {len(_role_names)} roles.")

def retrieve_relevant_roles(resume_text: str, top_k: int = 3):
    global _index, _role_names
    
    # 1. Input Validation
    if not resume_text or len(resume_text.strip()) < 10:
        return ["Software Engineer"]

    try:
        # Fallback if index not built
        if _index is None:
            build_index()
        
        if _index is None or not _role_names:
            return ["Software Engineer"]

        # 2. Vector Search (RAG Retrieval)
        model = AIModelManager.get_model()
        resume_embedding = model.encode([resume_text])
        distances, indices = _index.search(np.array(resume_embedding), top_k)
        
        # 3. Guard against invalid search results
        valid_indices = [i for i in indices[0] if i != -1 and i < len(_role_names)]
        if not valid_indices:
            return ["Software Engineer"]
            
        return [_role_names[i] for i in valid_indices]
    except Exception as e:
        logger.error(f"⚠️ RAG Retrieval Error: {e}")
        return ["Software Engineer"]
