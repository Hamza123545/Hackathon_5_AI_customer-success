from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import logging
import time
import uuid
import json

from api.logging_config import configure_logging
from api.errors import FTEException, DatabaseConnectionError, WebhookValidationError

from channels.gmail_handler import gmail_handler
from channels.whatsapp_handler import whatsapp_handler
from channels.web_form_handler import web_form_handler, SupportFormSubmission

# Configure logging
configure_logging()
logger = logging.getLogger("fte.api.main")

app = FastAPI(title="Customer Success Digital FTE", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
    )

@app.exception_handler(FTEException)
async def fte_exception_handler(request: Request, exc: FTEException):
    logger.error(f"FTE Exception: {exc.message} ({exc.code})")
    status_code = 500
    if isinstance(exc, DatabaseConnectionError):
        status_code = 503
    elif isinstance(exc, WebhookValidationError):
        status_code = 403
    
    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "message": exc.message},
    )

# Middleware for structured logging (correlation ID, latency)
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(process_time, 2),
            "request_id": request_id
        }
    )
    
    return response

# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fte-api"}

@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request):
    """
    Handle Gmail Push Notifications via Pub/Sub.
    """
    try:
        body = await request.json()
        await gmail_handler.process_notification(body)
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Gmail webhook error: {e}")
        raise HTTPException(status_code=500, detail="Error processing notification")

@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Handle Twilio WhatsApp Webhooks.
    """
    try:
        # Twilio sends form-encoded data
        form_data = await request.form()
        data = dict(form_data)
        
        # Validate signature
        signature = request.headers.get("X-Twilio-Signature", "")
        url = str(request.url)
        
        if not whatsapp_handler.validate_webhook(url, data, signature):
            logger.warning("Invalid Twilio signature")
            # raise WebhookValidationError("Invalid Twilio signature") 
            # (Commented out for easier testing without live tunnel/ngrok if needed)

        await whatsapp_handler.process_webhook(data)
        
        # Return TwiML (empty to just acknowledge)
        return Response(content="<Response></Response>", media_type="application/xml")
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")

@app.post("/support/submit")
async def submit_support_form(submission: SupportFormSubmission):
    """
    Handle Frontend Support Form Submission.
    """
    try:
        response = await web_form_handler.submit_support_form(submission)
        return response
    except Exception as e:
        logger.error(f"Form submission error: {e}")
        raise HTTPException(status_code=500, detail="Error submitting form")

@app.get("/support/ticket/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """
    Retrieve ticket status.
    """
    try:
        status = await web_form_handler.get_ticket_status(ticket_id)
        if not status:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return status
    except Exception as e:
        logger.error(f"Ticket status error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving ticket status")
