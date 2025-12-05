from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Manhwa API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    # Rate limiting
    RATE_LIMIT: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # Download settings
    DOWNLOAD_PATH: str = "./downloads"
    MAX_CONCURRENT_DOWNLOADS: int = 5
    
    # Supported sources
    ENABLED_SOURCES: List[str] = [
        "asurascans",
        "flamescans",
        "reaperscans",
        "manganato",
        "mangadex"
    ]
    
    # Request settings
    REQUEST_TIMEOUT: int = 30
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    class Config:
        env_file = ".env"

settings = Settings()
