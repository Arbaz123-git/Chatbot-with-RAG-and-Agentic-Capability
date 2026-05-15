from openai import OpenAI
from app.config import settings

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL
        )
    
    def stream_chat(self, messages: list):
        response = self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

llm_client = LLMClient()
