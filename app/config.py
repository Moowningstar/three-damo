from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: str
    openai_api_base: Optional[str] = None  # 自定义 API Base URL
    openai_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-3-small"
    max_history_length: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()
