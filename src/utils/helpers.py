# src/utils/helpers.py

from datetime import datetime
import pytz
from typing import Optional

def get_brazil_time() -> datetime:
    """Get current time in Brazil timezone"""
    brazil_tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(brazil_tz)

def format_phone_number(phone: str) -> str:
    """Format phone number to WhatsApp format"""
    # Remove non-numeric characters
    cleaned = ''.join(filter(str.isdigit, phone))
    
    # Add country code if needed
    if len(cleaned) == 11:  # Brazilian number with DDD
        return f"55{cleaned}"
    elif len(cleaned) == 10:  # Old format without 9
        return f"559{cleaned}"
    elif len(cleaned) >= 12:  # Already has country code
        return cleaned
    
    raise ValueError(f"Invalid phone number format: {phone}")

def parse_template_vars(template: str, variables: dict) -> str:
    """Parse template variables into string"""
    try:
        return template.format(**variables)
    except KeyError as e:
        raise ValueError(f"Missing template variable: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing template: {e}")

def validate_message_content(content: str, max_length: Optional[int] = 1024) -> bool:
    """Validate message content length and characters"""
    if not content:
        return False
    if max_length and len(content) > max_length:
        return False
    return True