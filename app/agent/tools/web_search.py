import requests
import json
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class WebSearchTool:
    def __init__(self):
        self.api_url = "https://api.langsearch.com/v1/web-search"
        self.api_key = settings.LANGSEARCH_API_KEY
    
    def search(self, query: str, count: int = 10) -> str:
        logger.info(f"Performing LangSearch web search for: {query}")
        
        payload = json.dumps({
            "query": query,
            "freshness": "noLimit",
            "summary": True,
            "count": count
        })
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, data=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Web search completed successfully")
            
            if 'summary' in result:
                return result['summary']
            elif 'results' in result:
                formatted_results = self._format_results(result['results'])
                return formatted_results
            else:
                return json.dumps(result, indent=2)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error performing web search: {str(e)}")
            return f"Error performing web search: {str(e)}"
    
    def _format_results(self, results: list) -> str:
        formatted = "Web Search Results:\n\n"
        for i, result in enumerate(results[:5], 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', result.get('description', 'No description'))
            url = result.get('url', '')
            formatted += f"{i}. {title}\n{snippet}\n{url}\n\n"
        return formatted

web_search_tool = WebSearchTool()
