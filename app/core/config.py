"""Configuration module for the application."""

import os
import logging
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

class Settings(BaseSettings):
    """Application settings.
    
    Attributes:
        app_name: Name of the application
        debug: Debug mode flag
    """
    app_name: str = "Portfolio Assessment Agentic AI Backend"
    debug: bool = bool(os.getenv("DEBUG", False))


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Configure logging
logging.basicConfig(
    level=logging.INFO if not get_settings().debug else logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
) 