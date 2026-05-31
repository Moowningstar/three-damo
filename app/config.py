from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: str
    openai_api_base: Optional[str] = None  # LLM API Base URL
    openai_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-3-small"
    embedding_api_base: Optional[str] = None  # Embedding API Base URL (独立配置)
    embedding_api_key: Optional[str] = None  # Embedding API Key (独立配置，如果不设置则使用 openai_api_key)
    max_history_length: int = 10

    class Config:
        env_file = ".env"

settings = Settings()
