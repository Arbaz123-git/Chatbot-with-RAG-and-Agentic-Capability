from sentence_transformers import SentenceTransformer
from typing import List
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"Generating embeddings for {len(texts)} texts using {settings.EMBEDDING_MODEL}")
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings.tolist()
    
    def generate_query_embedding(self, query: str) -> List[float]:
        logger.info(f"Generating query embedding for: '{query[:100]}...'")
        embedding = self.model.encode([query], convert_to_numpy=True)
        return embedding[0].tolist()

embedding_service = EmbeddingService()
