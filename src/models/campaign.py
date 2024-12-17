# src/models/campaign.py

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from src.config.constants import CampaignType

class CampaignTarget(BaseModel):
    id: str
    user_id: str
    campaign_type: CampaignType
    customer_id: str
    name: str
    phone: str
    data: Dict[str, Any]
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CampaignSettings(BaseModel):
    user_id: str
    campaign_type: CampaignType
    enabled: bool = True
    template_name: Optional[str] = None
    custom_message: Optional[str] = None
    send_time: str = "09:00"  # Default send time
    settings: Dict[str, Any] = Field(default_factory=dict)