# src/services/twilio_client.py

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from src.config import settings
from src.models.message import Message
from src.utils.logging import get_logger
from typing import Dict, Optional

logger = get_logger(__name__)

class TwilioClient:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.logger = logger

    async def send_message(self, message: Message) -> Dict:
        """Send WhatsApp message using Twilio"""
        try:
            self.logger.info(
                "sending_whatsapp_message",
                user_id=message.user_id,
                phone=message.phone_number,
                template=message.template_name
            )

            response = self.client.messages.create(
                from_=f'whatsapp:{message.from_number}',
                to=f'whatsapp:{message.phone_number}',
                template=message.template_name,
                language=message.language_code,
                components=[{
                    "type": "body",
                    "parameters": message.parameters
                }]
            )

            return {
                "message_id": response.sid,
                "status": response.status,
                "error_code": None,
                "error_message": None
            }

        except TwilioRestException as e:
            self.logger.error(
                "twilio_send_error",
                error=str(e),
                error_code=e.code,
                user_id=message.user_id
            )
            return {
                "message_id": None,
                "status": "failed",
                "error_code": e.code,
                "error_message": str(e)
            }
        except Exception as e:
            self.logger.error(
                "unexpected_send_error",
                error=str(e),
                user_id=message.user_id
            )
            raise

    async def verify_number(self, phone_number: str) -> Dict:
        """Start WhatsApp number verification process"""
        try:
            verification = self.client.verify.v2.services(
                settings.TWILIO_VERIFY_SERVICE_SID
            ).verifications.create(
                to=f'whatsapp:{phone_number}',
                channel='whatsapp'
            )
            
            return {
                "status": verification.status,
                "valid": True
            }
        except TwilioRestException as e:
            self.logger.error("verification_error", error=str(e))
            return {
                "status": "failed",
                "valid": False,
                "error": str(e)
            }

    async def check_verification(self, phone_number: str, code: str) -> bool:
        """Check verification code"""
        try:
            verification_check = self.client.verify.v2.services(
                settings.TWILIO_VERIFY_SERVICE_SID
            ).verification_checks.create(
                to=f'whatsapp:{phone_number}',
                code=code
            )
            
            return verification_check.status == "approved"
        except TwilioRestException as e:
            self.logger.error("verification_check_error", error=str(e))
            return False