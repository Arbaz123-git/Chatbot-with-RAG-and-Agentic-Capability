from groq import Groq
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.evaluator_model = settings.EVALUATOR_MODEL
    
    def search_web(self, query: str) -> str:
        logger.info(f"Performing web search for query: '{query[:100]}...'")
        
        if not settings.WEB_SEARCH_ENABLED:
            logger.warning("Web search is disabled in settings")
            return ""
        
        search_prompt = f"""Search the web and provide comprehensive information to answer the following question:

QUESTION: {query}

Provide detailed, accurate information from reliable sources."""
        
        try:
            completion = self.client.chat.completions.create(
                model=self.evaluator_model,
                messages=[
                    {"role": "user", "content": search_prompt}
                ],
                temperature=settings.EVALUATOR_TEMPERATURE,
                max_completion_tokens=1024,
                stream=True,
                compound_custom={
                    "tools": {
                        "enabled_tools": ["web_search", "visit_website"]
                    }
                }
            )
            
            web_content = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    web_content += chunk.choices[0].delta.content
            
            logger.info(f"Web search completed. Retrieved {len(web_content)} characters")
            logger.debug(f"Web content preview: {web_content[:200]}...")
            
            return web_content.strip()
            
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return ""

web_search_service = WebSearchService()
