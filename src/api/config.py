"""API Configuration"""
import os
from typing import Optional

class APIConfig:
    """API configuration settings"""

    # Server
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Cache
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)  # None = use in-memory cache

    # Query optimization
    MAX_VECTOR_RESULTS: int = int(os.getenv("MAX_VECTOR_RESULTS", "3"))
    MAX_TABLE_RESULTS: int = int(os.getenv("MAX_TABLE_RESULTS", "5"))
    VECTOR_SEARCH_LIMIT: int = int(os.getenv("VECTOR_SEARCH_LIMIT", "10"))

    # Database
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")

    # Ingestion
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/rag_uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))

config = APIConfig()
