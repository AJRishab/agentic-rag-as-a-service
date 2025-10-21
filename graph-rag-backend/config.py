"""
Configuration Management
Central configuration for Graph RAG system
"""

import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    
    # Server
    HOST: str
    PORT: int
    
    # Graph Database
    GRAPH_DB_TYPE: str  # Options: neo4j, neptune, memory
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # AWS Neptune (if using)
    NEPTUNE_ENDPOINT: Optional[str] = None
    NEPTUNE_PORT: int
    
    # LLM Configuration
    LLM_PROVIDER: str  # Options: groq, ollama, openai, huggingface
    OLLAMA_ENDPOINT: str
    OLLAMA_MODEL: str
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    
    # HuggingFace Configuration (Optional)
    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_MODEL: Optional[str] = None
    
    # Embeddings
    EMBEDDING_MODEL: str
    EMBEDDING_DIMENSION: int
    
    # Processing
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    MAX_CHUNKS_PER_DOC: int
    
    # Entity Resolution
    ENTITY_SIMILARITY_THRESHOLD: float
    
    # Retrieval
    MAX_VECTOR_RESULTS: int
    GRAPH_TRAVERSAL_DEPTH: int
    RETRIEVAL_TIMEOUT_SECONDS: int
    
    # Storage
    UPLOAD_DIR: str
    VECTOR_STORE_PATH: str
    
    # Logging
    LOG_LEVEL: str
    LOG_FILE: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings