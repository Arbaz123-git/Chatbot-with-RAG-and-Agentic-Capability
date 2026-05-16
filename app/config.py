from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 2048
    
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 3
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    
    SYSTEM_PROMPT: str = """You are a knowledgeable and helpful AI assistant. 
You provide clear, accurate, and conversational responses. 
When you don't know something, you admit it honestly.
Be concise but thorough in your answers."""
    
    class Config:
        env_file = ".env"

settings = Settings()
