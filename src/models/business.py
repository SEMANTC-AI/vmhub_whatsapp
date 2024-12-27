# src/models/business.py

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from src.utils.helpers import format_phone_number

class BusinessPhone(BaseModel):
    user_id: str
    phone_number: str
    is_verified: bool = False
    wa_id: Optional[str] = None
    business_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('phone_number')
    def validate_phone(cls, v):
        try:
            return format_phone_number(v)
        except ValueError as e:
            raise ValueError(f"Invalid phone number: {e}")

class PhoneVerification(BaseModel):
    user_id: str
    code: str
