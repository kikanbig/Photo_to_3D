"""
Database models and connection for Photo to 3D
"""
import os
from datetime import datetime
from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./photo_to_3d.db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class GenerationTask(Base):
    """3D Generation task model"""
    __tablename__ = "generation_tasks"
    
    # Primary key
    id = Column(String, primary_key=True)
    
    # Task info
    user_id = Column(String, nullable=True)  # For future auth
    status = Column(String, default=GenerationStatus.PENDING.value)
    
    # Input data
    original_image_url = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    
    # Generation parameters
    seed = Column(Integer, default=42)
    ss_guidance_strength = Column(Float, default=7.5)
    ss_sampling_steps = Column(Integer, default=12)
    slat_guidance_strength = Column(Float, default=3.0)
    slat_sampling_steps = Column(Integer, default=12)
    
    # Output files
    glb_file_url = Column(String, nullable=True)
    ply_file_url = Column(String, nullable=True) 
    preview_video_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_code = Column(String, nullable=True)
    
    # Metadata
    processing_time_seconds = Column(Float, nullable=True)
    file_size_mb = Column(Float, nullable=True)

class User(Base):
    """User model for future authentication"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    
    # Subscription info
    is_premium = Column(Boolean, default=False)
    generations_used = Column(Integer, default=0)
    generations_limit = Column(Integer, default=5)  # Free tier limit
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

# Database functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

if __name__ == "__main__":
    init_database()
