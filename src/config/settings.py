# src/config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Project settings
    PROJECT_ID: str
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Twilio settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str

    # Service settings
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 300  # 5 minutes
    MAX_BATCH_SIZE: int = 100

    # WhatsApp settings
    MESSAGE_TEMPLATES: dict = {
        "birthday": "birthday_template",
        "welcome": "welcome_template",
        "reactivation": "reactivation_template",
        "loyalty": "loyalty_template"
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

# Create global settings instance
settings = Settings()