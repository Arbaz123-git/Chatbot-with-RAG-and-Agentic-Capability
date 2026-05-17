from typing import Dict, List, Tuple
from app.config import settings
from app.rag.vector_store import vector_store
from app.agent.evaluator_service import evaluator_service
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.sessions: Dict[str, List[dict]] = {}
    
    def get_messages(self, session_id: str) -> List[dict]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": role, "content": content})
    
    def _evaluate_and_get_context(self, user_message: str) -> Tuple[str, str]:
        logger.info(f"Starting evaluation and context retrieval for: {user_message}")
        
        retrieved_docs = vector_store.search(user_message)
        logger.info(f"Retrieved {len(retrieved_docs)} documents from vector store")
        
        if not retrieved_docs:
            logger.warning("No documents retrieved from vector store - will use model knowledge")
            return "", "model_knowledge"
        
        is_doc_relevant = evaluator_service.evaluate_document_relevance(user_message, retrieved_docs)
        
        if is_doc_relevant:
            logger.info("Documents are relevant - using document context")
            context = "\n\n".join([doc["content"] for doc in retrieved_docs])
            source = "documents"
            return context, source
        else:
            logger.info("Documents are not relevant - falling back to model knowledge")
            return "", "model_knowledge"
    
    def build_prompt(self, session_id: str, user_message: str, use_rag: bool = False) -> List[dict]:
        if use_rag:
            logger.info(f"RAG enabled - searching for: {user_message}")
            
            context, source = self._evaluate_and_get_context(user_message)
            
            if source == "documents":
                logger.info(f"Using document context - length: {len(context)} characters")
                
                rag_user_message = f"""Read the following text and answer the question based ONLY on what you read.

TEXT:
{context}

QUESTION: {user_message}

IMPORTANT: Start your response with "[Source: Provided Documents]" to indicate the answer is from the uploaded files, then provide the answer."""
                
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that extracts information from provided text. Always indicate the source of your answer."},
                    {"role": "user", "content": rag_user_message}
                ]
                
            else:
                logger.warning("No relevant context found from documents - using model knowledge")
                
                model_knowledge_message = f"""{user_message}

IMPORTANT: The answer was not found in the provided documents. If you can answer this question from your training knowledge, start your response with "[Source: Model Training Knowledge - Not found in documents]" and then provide the answer. If you truly don't know the answer, clearly state "I don't have enough information to answer this question. [Not found in documents]"""
                
                messages = [
                    {"role": "system", "content": "You are a helpful assistant. Always indicate the source of your answer and be honest when information is not found in provided documents."},
                    {"role": "user", "content": model_knowledge_message}
                ]
        else:
            messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]
            messages.extend(self.get_messages(session_id))
            messages.append({"role": "user", "content": user_message})
        
        logger.info(f"Total messages to LLM: {len(messages)}")
        return messages

chat_service = ChatService()
