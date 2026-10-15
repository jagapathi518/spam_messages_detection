"""Application Configuration."""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))


class Settings(BaseSettings):
    PROJECT_NAME: str = "Spam Shield API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Groq Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")
    RATE_LIMIT_GROQ_PER_USER_PER_DAY: int = int(os.getenv("RATE_LIMIT_GROQ_PER_USER_PER_DAY", "50"))
    
    # Supabase Settings
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_PUBLISHABLE_KEY: str = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    SUPABASE_SECRET_KEY: str = os.getenv("SUPABASE_SECRET_KEY", "")
    
    # CORS Origins
    CORS_ORIGINS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
