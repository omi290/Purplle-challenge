import os
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://apex:apex@db:5432/apex_retail"
    
    # Storage
    VIDEO_DIR: str = "/data/videos"
    UPLOAD_DIR: str = "/data/uploads"
    
    # Computer Vision
    YOLO_MODEL: str = "yolov8n.pt"
    YOLO_CONFIDENCE: float = 0.3
    FPS_SKIP: int = 5
    
    # Staff Detection
    STAFF_DETECTION_METHOD: str = "color"  # clip or color
    UNIFORM_COLOR_HSV_LOWER: str = "100,50,50"
    UNIFORM_COLOR_HSV_UPPER: str = "130,255,255"
    
    # System
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
