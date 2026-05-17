from groq import Groq
from typing import List, Dict
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EvaluatorService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.evaluator_model = settings.EVALUATOR_MODEL
    
    def evaluate_document_relevance(self, query: str, documents: List[Dict]) -> bool:
        logger.info(f"Evaluating relevance of {len(documents)} documents for query: '{query[:100]}...'")
        
        if not documents:
            logger.warning("No documents to evaluate")
            return False
        
        context = "\n\n".join([f"Document {i+1}:\n{doc['content']}" for i, doc in enumerate(documents)])
        
        evaluation_prompt = f"""You are an evaluator. Your task is to determine if the provided documents contain relevant information to answer the user's question.

DOCUMENTS:
{context}

USER QUESTION: {query}

Analyze the documents carefully and respond with ONLY one word:
- "RELEVANT" if the documents contain information that can answer the question
- "NOT_RELEVANT" if the documents do not contain sufficient information to answer the question

Response:"""
        
        try:
            completion = self.client.chat.completions.create(
                model=self.evaluator_model,
                messages=[
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=settings.EVALUATOR_TEMPERATURE,
                max_tokens=10
            )
            
            response = completion.choices[0].message.content.strip().upper()
            logger.info(f"Document relevance evaluation result: {response}")
            
            is_relevant = "RELEVANT" in response and "NOT_RELEVANT" not in response
            return is_relevant
            
        except Exception as e:
            logger.error(f"Error evaluating document relevance: {str(e)}")
            return False
    
    def evaluate_web_search_relevance(self, query: str, web_content: str) -> bool:
        logger.info(f"Evaluating web search relevance for query: '{query[:100]}...'")
        
        if not web_content or not web_content.strip():
            logger.warning("No web content to evaluate")
            return False
        
        evaluation_prompt = f"""You are an evaluator. Your task is to determine if the web search results contain relevant information to answer the user's question.

WEB SEARCH RESULTS:
{web_content}

USER QUESTION: {query}

Analyze the web search results carefully and respond with ONLY one word:
- "RELEVANT" if the web results contain information that can answer the question
- "NOT_RELEVANT" if the web results do not contain sufficient information to answer the question

Response:"""
        
        try:
            completion = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=settings.EVALUATOR_TEMPERATURE,
                max_tokens=10
            )
            
            response = completion.choices[0].message.content.strip().upper()
            logger.info(f"Web search relevance evaluation result: {response}")
            
            is_relevant = "RELEVANT" in response and "NOT_RELEVANT" not in response
            return is_relevant
            
        except Exception as e:
            logger.error(f"Error evaluating web search relevance: {str(e)}")
            return False

evaluator_service = EvaluatorService()
