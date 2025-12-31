from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "documind-index"
    OPENROUTER_API_KEY: str = ""  # Now loaded from .env
    LLM_MODEL: str = "models/gemini-flash-latest"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 8
    UPLOAD_DIR: str = "uploads"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
