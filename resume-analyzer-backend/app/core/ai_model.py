from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class AIModelManager:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            logger.info("⚡ Loading Shared AI Resume Analyzer Model (all-MiniLM-L6-v2)...")
            try:
                cls._model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("✅ Shared AI Model Loaded Successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to load AI Model: {e}")
                raise e
        return cls._model

    @classmethod
    def preload(cls):
        """Used for background preloading"""
        return cls.get_model()
