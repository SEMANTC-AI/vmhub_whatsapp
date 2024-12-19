from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from src.config import settings
from src.models.message import Message
from src.utils.logging import get_logger
from typing import Dict, Optional
from pathlib import Path

logger = get_logger(__name__)

class TwilioClient:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.logger = logger
        self.bucket_url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}"

    def get_loyalty_card_url(self, count: int) -> Optional[str]:
        """Get loyalty card image URL"""
        return f"{self.bucket_url}/card{count}.jpg"

    async def send_message(self, message: Message) -> Dict:
        """Send WhatsApp message using Twilio"""
        try:
            self.logger.info(
                "sending_whatsapp_message",
                user_id=message.user_id,
                phone=message.phone_number,
                template=message.template_name
            )

            # Clean and format the from number - remove any comments and whitespace
            from_number = settings.TWILIO_FROM_NUMBER.split('#')[0].strip()
            if not from_number.startswith('+'):
                from_number = f'+{from_number}'
            from_whatsapp = f'whatsapp:{from_number}'

            # Format the to number
            to_whatsapp = f'whatsapp:+{message.phone_number}'

            message_params = {
                'from_': from_whatsapp,
                'to': to_whatsapp,
                'body': self._format_message(message.template_name, message.parameters)
            }

            # Add media for loyalty campaign
            if message.campaign_type == 'loyalty' and message.loyalty_count:
                media_url = self.get_loyalty_card_url(message.loyalty_count)
                if media_url:
                    message_params['media_url'] = [media_url]
                    self.logger.info(
                        "adding_loyalty_card",
                        media_url=media_url,
                        loyalty_count=message.loyalty_count
                    )

            print("Sending with params:", message_params)  # Debug print
            response = self.client.messages.create(**message_params)

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

    def _format_message(self, template_name: str, parameters: Dict[str, str]) -> str:
        """Format message with parameters"""
        try:
            template = settings.MESSAGE_TEMPLATES.get(template_name)
            if not template:
                raise ValueError(f"Template not found: {template_name}")
            return template.format(**parameters)
        except KeyError as e:
            raise ValueError(f"Missing template parameter: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error formatting message: {str(e)}")