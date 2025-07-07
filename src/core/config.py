"""
Core configuration settings for the Financial Data AI Agent
"""

import os
from typing import Optional


class Settings:
    """Application settings configuration"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Gemini AI settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".csv", ".xlsx", ".xls"}
    
    # Data processing settings
    MAX_ROWS_PROCESS: int = 10000
    CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # Response settings
    MAX_RESPONSE_LENGTH: int = 5000
    
    def __init__(self):
        # Validate Gemini API key
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")


# Global settings instance
settings = Settings()
