# src/config/constants.py

from enum import Enum

class MessageStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class CampaignType(str, Enum):
    BIRTHDAY = "birthday"
    WELCOME = "welcome"
    REACTIVATION = "reactivation"
    LOYALTY = "loyalty"

# WhatsApp template parameters
TEMPLATE_PARAMS = {
    "birthday": ["name", "coupon"],
    "welcome": ["name"],
    "reactivation": ["name", "days_inactive"],
    "loyalty": ["name", "points"]
}

# Error messages
ERROR_MESSAGES = {
    "invalid_phone": "Invalid phone number format",
    "template_not_found": "Message template not found",
    "invalid_campaign": "Invalid campaign type",
    "message_too_long": "Message content exceeds maximum length",
    "missing_params": "Missing required template parameters",
}

# Queue settings
QUEUE_CONFIG = {
    "retry_attempts": 3,
    "backoff_seconds": 300,  # 5 minutes
    "max_batch_size": 100,
}

# Brazil timezone
BRAZIL_TIMEZONE = "America/Sao_Paulo"

# Maximum content lengths
MAX_LENGTHS = {
    "message": 1024,
    "name": 100,
    "phone": 20,
}