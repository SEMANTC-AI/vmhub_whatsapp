# src/main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.services import MessageProcessor, TwilioClient
from src.models.campaign import CampaignTarget
from src.models.business import BusinessPhone, PhoneVerification
from src.utils.logging import setup_logging, get_logger, RequestContextMiddleware
from typing import Dict
import structlog
import json

# Set up logging
setup_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)

app = FastAPI(
    title="VMHub WhatsApp Service",
    description="WhatsApp messaging service for VMHub campaigns",
    version="1.0.0"
)

# Add middleware
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
processor = MessageProcessor()
twilio = TwilioClient()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "whatsapp"}

@app.post("/process-target")
async def process_target(
    target: CampaignTarget,
    background_tasks: BackgroundTasks
):
    """Process a campaign target"""
    try:
        logger.info(
            "processing_target",
            user_id=target.user_id,
            campaign_type=target.campaign_type,
            target_id=target.id
        )
        
        background_tasks.add_task(processor.process_target, target)
        
        return {
            "status": "processing",
            "target_id": target.id
        }
    except Exception as e:
        logger.error(
            "target_processing_error",
            error=str(e),
            target_id=target.id
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-number")
async def verify_number(phone: BusinessPhone):
    """Start phone number verification process"""
    try:
        result = await twilio.verify_number(phone.phone_number)
        return result
    except Exception as e:
        logger.error(
            "verification_error",
            error=str(e),
            user_id=phone.user_id
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-verification")
async def check_verification(verification: PhoneVerification):
    """Check verification code"""
    try:
        result = await twilio.check_verification(
            verification.phone_number,
            verification.code
        )
        return {"verified": result}
    except Exception as e:
        logger.error(
            "verification_check_error",
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle Twilio webhook"""
    try:
        body = await request.json()
        logger.info("webhook_received", payload=body)
        
        # Validate webhook signature if configured
        if settings.WEBHOOK_SECRET:
            # Add signature validation here
            pass
            
        # Process status update
        message_sid = body.get("MessageSid")
        status = body.get("MessageStatus")
        
        if message_sid and status:
            # Update message status
            await processor._update_message_history(
                message_sid,
                {"status": status}
            )
            
        return {"status": "processed"}
    except Exception as e:
        logger.error("webhook_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=not settings.is_production
    )