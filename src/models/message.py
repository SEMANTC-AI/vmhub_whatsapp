# src/models/message.py

from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, Any, List
from datetime import datetime
from src.config.constants import MessageStatus, CampaignType

class MessageTemplate(BaseModel):
    name: str
    content: str
    parameters: Dict[str, str] = Field(default_factory=dict)
    language_code: str = "pt_BR"

class Message(BaseModel):
    id: Optional[str] = None
    user_id: str
    campaign_type: CampaignType
    target_id: str
    phone_number: str
    template_name: str
    parameters: Dict[str, Any]
    media_urls: Optional[List[str]] = None
    loyalty_count: Optional[int] = None
    status: MessageStatus = MessageStatus.PENDING
    whatsapp_message_id: Optional[str] = None
    error_message: Optional[str] = None
    attempt_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        use_enum_values = True

class MessageStatus(BaseModel):
    message_id: str
    status: MessageStatus
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
