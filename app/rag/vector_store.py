import chromadb
from typing import List, Dict
from app.config import settings
from app.rag.embeddings import embedding_service
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, filename: str, chunks: List[str]) -> int:
        logger.info(f"Adding {len(chunks)} chunks from {filename} to vector store")
        embeddings = embedding_service.generate_embeddings(chunks)
        
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"filename": filename, "chunk_id": i} for i in range(len(chunks))]
        
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully added {len(chunks)} chunks to vector store")
        return len(chunks)
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        logger.info(f"Searching for top {top_k} results for query: '{query[:100]}...'")
        query_embedding = embedding_service.generate_query_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        if not results['documents'][0]:
            logger.warning("No documents found in search results")
            return []
        
        retrieved_docs = []
        for i in range(len(results['documents'][0])):
            doc = {
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            }
            retrieved_docs.append(doc)
            logger.info(f"Result {i+1}: distance={doc['distance']:.4f}, chunk_id={doc['metadata']['chunk_id']}, preview={doc['content'][:100]}...")
        
        return retrieved_docs
    
    def clear_collection(self):
        self.client.delete_collection("documents")
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def has_documents(self) -> bool:
        """Check if any documents have been uploaded to the vector store."""
        try:
            count = self.collection.count()
            return count > 0
        except:
            return False

vector_store = VectorStore()
