# src/__init__.py

from src.config import settings
from src.utils.logging import setup_logging

# Set up logging on package import
setup_logging(settings.LOG_LEVEL)

__version__ = "1.0.0"