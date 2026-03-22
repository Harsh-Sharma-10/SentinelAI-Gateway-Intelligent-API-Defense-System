from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """
    Application settings
    Loads from environment variables or .env file
    """

    # Application
    app_name: str = "AI Decision Service"
    version: str = "1.0.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Rate Limiting Thresholds for AI Analysis
    suspicious_request_count: int = 50
    high_frequency_threshold: int = 30
    very_high_frequency_threshold: int = 80

    # User Agent Analysis
    bot_keywords: List[str] = [
        "bot", "crawler", "spider", "scraper",
        "python-requests", "curl", "wget",
        "scrapy", "headless"
    ]

    # Time-based patterns (in seconds)
    burst_window_seconds: int = 60

    # Confidence thresholds
    block_confidence_threshold: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()