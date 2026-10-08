import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "VoyageAI"
    TAGLINE: str = "Your intelligent team of AI travel agents."
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./voyageai.db"

    # Security & Auth
    SECRET_KEY: str = "voyageai_secret_key_super_secure_random_hash_change_in_production_32bytes"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # AI Model (Groq)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # External APIs (Optional - Graceful Fallbacks Included)
    TAVILY_API_KEY: str = ""
    AVIATIONSTACK_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""

    # RAG
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_API_BASE_URL: str = "https://api.openai.com/v1/embeddings"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    RAG_CHUNK_SIZE: int = 800
    RAG_CHUNK_OVERLAP: int = 120
    RAG_ADMIN_USERNAMES: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def rag_admin_usernames(self) -> List[str]:
        return [name.strip().casefold() for name in self.RAG_ADMIN_USERNAMES.split(",") if name.strip()]


settings = Settings()
