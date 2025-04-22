"""
Configuration settings for the application.
Loads environment variables and provides them as configuration objects.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys for LLM providers
    OPENAI_API_KEY: str = Field(None, description="OpenAI API key")
    GOOGLE_API_KEY: str = Field(None, description="Google API key for Gemini")
    DEEPSEEK_API_KEY: str = Field(None, description="DeepSeek API key")
    
    # LLM Configuration
    LLM_PROVIDER: str = Field("claude", description="LLM provider to use (chatgpt, claude, gemini, deepseek)")
    MAX_TOKENS: int = Field(1000, description="Maximum tokens for LLM response")
    TEMPERATURE: float = Field(0.7, description="Temperature for LLM response generation")
    
    # API Configuration
    DEBUG: bool = Field(False, description="Debug mode")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings to avoid reloading from environment every time."""
    return Settings()