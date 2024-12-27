# src/services/message_processor.py

from src.models.message import Message, MessageStatus
from src.models.campaign import CampaignTarget
from src.services.whatsapp_client import WhatsAppClient
from src.utils.logging import get_logger
from src.config import settings
from google.cloud import firestore
from typing import Optional, Dict
import asyncio

logger = get_logger(__name__)

class MessageProcessor:
    def __init__(self):
        self.whatsapp = WhatsAppClient()
        self.db = firestore.Client()
        self.logger = logger

    async def process_target(self, target: CampaignTarget) -> Optional[Dict]:
        """Process a campaign target and send message"""
        try:
            # Get campaign settings
            settings_ref = (
                self.db.collection("users")
                .document(target.user_id)
                .collection("campaigns")
                .document(target.campaign_type)
            )
            settings_doc = settings_ref.get()
            
            if not settings_doc.exists:
                self.logger.error(
                    "campaign_settings_not_found",
                    user_id=target.user_id,
                    campaign_type=target.campaign_type
                )
                return None

            campaign_settings = settings_doc.to_dict()
            
            # Create message
            message = Message(
                user_id=target.user_id,
                campaign_type=target.campaign_type,
                target_id=target.id,
                phone_number=target.phone,
                template_name=campaign_settings["template_name"],
                parameters=self._prepare_parameters(target)
            )

            if target.campaign_type == 'loyalty':
                message.loyalty_count = target.data.get('loyalty_count', 0)

            # Send message
            result = await self.whatsapp.send_message(message)
            
            # Update message history
            await self._update_message_history(message, result)
            
            # Update target status
            await self._update_target_status(target, result)
            
            return result

        except Exception as e:
            self.logger.error(
                "target_processing_error",
                error=str(e),
                target_id=target.id,
                user_id=target.user_id
            )
            return None

    async def _update_message_history(self, message: Message, result: Dict):
        """Update message history in Firestore"""
        history_ref = self.db.collection("message_history").document()
        history_ref.set({
            "message_id": result.get("message_id"),
            "user_id": message.user_id,
            "campaign_type": message.campaign_type,
            "target_id": message.target_id,
            "phone": message.phone_number,
            "status": result.get("status", "failed"),
            "error": result.get("error_message"),
            "created_at": firestore.SERVER_TIMESTAMP,
            "loyalty_count": message.loyalty_count if message.campaign_type == 'loyalty' else None
        })

    async def _update_target_status(self, target: CampaignTarget, result: Dict):
        """Update target status after processing"""
        target_ref = (
            self.db.collection("users")
            .document(target.user_id)
            .collection("campaigns")
            .document(target.campaign_type)
            .collection("targets")
            .document(target.id)
        )
        
        target_ref.update({
            "processed": True,
            "processed_at": firestore.SERVER_TIMESTAMP,
            "status": result.get("status", "failed"),
            "message_id": result.get("message_id")
        })

    def _prepare_parameters(self, target: CampaignTarget) -> Dict:
        """Prepare message template parameters based on campaign type"""
        params = {
            "name": target.name
        }
        
        if target.campaign_type == "birthday":
            params.update({"coupon": target.data.get("coupon", "")})
        elif target.campaign_type == "reactivation":
            params.update({"days_inactive": target.data.get("days_since_last_purchase", "")})
        elif target.campaign_type == "loyalty":
            params.update({
                "services": str(target.data.get("loyalty_count", 0)),
                "points": str(target.data.get("loyalty_points", 0))
            })
            
        return params