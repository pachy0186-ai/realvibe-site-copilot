"""
Configuration settings for RealVibe Site Copilot
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "RealVibe Site Copilot API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    database_url: Optional[str] = None
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None
    
    # Gmail Integration
    gmail_credentials_file: Optional[str] = None
    gmail_token_file: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Storage
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ]
    
    # Vector Search
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimensions: int = 1536
    
    # Agent Configuration
    max_retries: int = 3
    agent_timeout: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

