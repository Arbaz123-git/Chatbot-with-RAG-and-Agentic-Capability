from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 2048
    
    SYSTEM_PROMPT: str = """You are a knowledgeable and helpful AI assistant. 
You provide clear, accurate, and conversational responses. 
When you don't know something, you admit it honestly.
Be concise but thorough in your answers."""
    
    class Config:
        env_file = ".env"

settings = Settings()
