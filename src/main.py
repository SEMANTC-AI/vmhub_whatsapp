# src/main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.services import MessageProcessor
from src.models.campaign import CampaignTarget
from src.models.business import BusinessPhone, PhoneVerification
from src.utils.logging import setup_logging, get_logger, RequestContextMiddleware
from typing import Dict, Optional
import structlog
import json
import hmac
import hashlib

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

async def verify_webhook_signature(
    request: Request,
    x_hub_signature: Optional[str] = Header(None)
) -> bool:
    """Verify Meta webhook signature"""
    if not settings.WEBHOOK_SECRET:
        return True
        
    if not x_hub_signature:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    try:
        body = await request.body()
        expected_signature = hmac.new(
            settings.WEBHOOK_SECRET.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        received_signature = x_hub_signature.replace('sha256=', '')
        
        if not hmac.compare_digest(received_signature, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
            
        return True
    except Exception as e:
        logger.error("signature_verification_error", error=str(e))
        raise HTTPException(status_code=401, detail="Signature verification failed")

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

@app.post("/webhook")
async def webhook_handler(
    request: Request,
    verified: bool = Depends(verify_webhook_signature)
):
    """Handle Meta webhook"""
    try:
        body = await request.json()
        logger.info("webhook_received", payload=body)
            
        # Process status update
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        message_id = value.get("message_id")
        status = value.get("status")
        
        if message_id and status:
            # Update message status
            await processor._update_message_history(
                message_id,
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
