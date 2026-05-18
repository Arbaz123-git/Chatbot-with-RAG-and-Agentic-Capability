from typing import Dict, List, Tuple
from app.config import settings
from app.rag.vector_store import vector_store
from app.agent.evaluator_service import evaluator_service
from app.utils.logger import step_logger

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
        step_logger.step(f"Starting RAG context retrieval", "RAG")
        step_logger.info(f"Query: {user_message[:50]}...", "RAG")
        
        retrieved_docs = vector_store.search(user_message)
        step_logger.step(f"Retrieved {len(retrieved_docs)} documents from vector store", "RAG")
        
        if not retrieved_docs:
            step_logger.step("No documents found - will use model knowledge", "RAG")
            return "", "model_knowledge"
        
        step_logger.step("Evaluating document relevance", "RAG")
        is_doc_relevant = evaluator_service.evaluate_document_relevance(user_message, retrieved_docs)
        
        if is_doc_relevant:
            step_logger.step("Documents are RELEVANT - using document context", "RAG")
            context = "\n\n".join([doc["content"] for doc in retrieved_docs])
            step_logger.info(f"Context length: {len(context)} characters", "RAG")
            source = "documents"
            return context, source
        else:
            step_logger.step("Documents NOT relevant - falling back to model knowledge", "RAG")
            return "", "model_knowledge"
    
    def build_prompt(self, session_id: str, user_message: str, use_rag: bool = False) -> List[dict]:
        if use_rag:
            step_logger.step("Building RAG prompt", "CHAT")
            
            context, source = self._evaluate_and_get_context(user_message)
            
            if source == "documents":
                step_logger.step("Using document context for response", "CHAT")
                
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
                step_logger.step("No relevant context - using model knowledge", "CHAT")
                
                model_knowledge_message = f"""{user_message}

IMPORTANT: The answer was not found in the provided documents. If you can answer this question from your training knowledge, start your response with "[Source: Model Training Knowledge - Not found in documents]" and then provide the answer. If you truly don't know the answer, clearly state "I don't have enough information to answer this question. [Not found in documents]"""
                
                messages = [
                    {"role": "system", "content": "You are a helpful assistant. Always indicate the source of your answer and be honest when information is not found in provided documents."},
                    {"role": "user", "content": model_knowledge_message}
                ]
        else:
            step_logger.step("Building direct chat prompt", "CHAT")
            messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]
            messages.extend(self.get_messages(session_id))
            messages.append({"role": "user", "content": user_message})
        
        step_logger.step(f"Prompt built with {len(messages)} messages", "CHAT")
        return messages

chat_service = ChatService()
