"""Core application functionality and configuration.

This module contains the fundamental components and settings for the backend:

Key components:
- Application configuration management with environment variable integration
- Dependency injection system for service resolution
- Security features including API key validation and rate limiting
- Constants and enumerations used throughout the application

The core module establishes the foundation for the application architecture,
ensuring proper initialization and configuration of all system components.
"""

from app.core.config import get_settings