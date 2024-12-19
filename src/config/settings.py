# src/config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict

class Settings(BaseSettings):
    # Project settings
    PROJECT_ID: str
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Twilio settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str
    TWILIO_VERIFY_SERVICE_SID: Optional[str] = None

    # Storage settings
    GCS_BUCKET_NAME: str

    # Service settings
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 300  # 5 minutes
    MAX_BATCH_SIZE: int = 100

    # WhatsApp settings
    MESSAGE_TEMPLATES: Dict[str, str] = {
        "birthday": "Olá {name}! 🎉 Feliz Aniversário! Como presente especial, preparamos um cupom para você: {coupon}",
        "welcome": "Olá {name}! 👋 Bem-vindo à nossa lavanderia! Estamos felizes em ter você como cliente.",
        "reactivation": "Olá {name}! 😊 Sentimos sua falta! Faz {days_inactive} dias que não te vemos. Que tal voltar?",
        "loyalty": "Parabéns {name}! 🌟 Você completou {services} serviços! Aqui está seu cartão fidelidade atualizado."
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