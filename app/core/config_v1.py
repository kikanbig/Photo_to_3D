"""
Application configuration for Pydantic v1
"""
import os
from typing import List, Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    PROJECT_NAME: str = "Photo to 3D"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # TRELLIS Configuration
    TRELLIS_MODEL_PATH: str = "microsoft/TRELLIS-image-large"
    CUDA_VISIBLE_DEVICES: str = ""  # Empty for CPU
    ATTN_BACKEND: str = "xformers"  # Use xformers instead of flash-attn
    SPCONV_ALGO: str = "auto"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    OUTPUT_DIR: str = "./outputs"
    MAX_FILE_SIZE_MB: int = 10
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # File Upload
    ALLOWED_IMAGE_TYPES: List[str] = ["image/png", "image/jpeg", "image/webp"]
    
    # 3D Generation
    GENERATION_TIMEOUT_SECONDS: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
