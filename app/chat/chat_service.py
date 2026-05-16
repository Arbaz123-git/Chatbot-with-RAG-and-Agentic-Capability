from typing import Dict, List
from app.config import settings
from app.rag.vector_store import vector_store
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
    
    def build_prompt(self, session_id: str, user_message: str, use_rag: bool = False) -> List[dict]:
        if use_rag:
            logger.info(f"RAG enabled - searching for: {user_message}")
            retrieved_docs = vector_store.search(user_message)
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            
            if retrieved_docs:
                context = "\n\n".join([doc["content"] for doc in retrieved_docs])
                logger.info(f"Context length: {len(context)} characters")
                logger.info(f"First 200 chars of context: {context[:200]}")
                
                # Try putting everything in user message with explicit extraction task
                rag_user_message = f"""Read the following text and answer the question based ONLY on what you read.

TEXT:
{context}

QUESTION: {user_message}

ANSWER (extract from the text above):"""
                
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that extracts information from provided text."},
                    {"role": "user", "content": rag_user_message}
                ]
                logger.info(f"RAG user message length: {len(rag_user_message)} characters")
            else:
                logger.warning("No documents retrieved!")
                messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]
                messages.extend(self.get_messages(session_id))
                messages.append({"role": "user", "content": f"{user_message}\n\nNote: No relevant information was found in the uploaded documents."})
        else:
            messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]
            messages.extend(self.get_messages(session_id))
            messages.append({"role": "user", "content": user_message})
        
        logger.info(f"Total messages to LLM: {len(messages)}")
        return messages

chat_service = ChatService()
