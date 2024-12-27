# src/config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict

class Settings(BaseSettings):
    # Project settings
    PROJECT_ID: str
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # WhatsApp Business API settings
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_ACCESS_TOKEN: str
    WHATSAPP_BUSINESS_ID: str
    
    # Storage settings
    GCS_BUCKET_NAME: str

    # Service settings
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 300
    MAX_BATCH_SIZE: int = 100

    # Message Templates - Updated for WhatsApp format
    MESSAGE_TEMPLATES: Dict[str, Dict[str, str]] = {
        "birthday": {
            "name": "birthday_template",
            "language": "pt_BR"
        },
        "welcome": {
            "name": "welcome_template",
            "language": "pt_BR"
        },
        "reactivation": {
            "name": "reactivation_template",
            "language": "pt_BR"
        },
        "loyalty": {
            "name": "loyalty_template",
            "language": "pt_BR"
        }
    }

    # Webhook settings
    WEBHOOK_SECRET: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8"
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

settings = Settings()