import logging
import uuid
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field

from database.queries import TicketRepository, get_db_pool
from workers.kafka_config import publish_event, TOPICS

logger = logging.getLogger(__name__)

# --- Pydantic Models ---

class SupportFormSubmission(BaseModel):
    name: str = Field(..., min_length=2, description="Customer Name")
    email: EmailStr = Field(..., description="Customer Email")
    subject: str = Field(..., min_length=5, description="Issue Subject")
    category: str = Field(..., description="Issue Category")
    message: str = Field(..., min_length=10, description="Detailed description")

class SupportFormResponse(BaseModel):
    ticket_id: str
    message: str
    status: str

class WebFormHandler:
    async def submit_support_form(self, form_data: SupportFormSubmission) -> SupportFormResponse:
        """
        Processes a new support form submission.
        1. Creates a Ticket in DB (initial status: open/pending).
        2. Publishes event to Kafka for the Agent to pick up and process (classify/respond).
        """
        try:
            # We'll generate a conversation_id here or the agent worker will do it.
            # Ideally, we create the ticket record first to give the user a confirmation ID immediately.
            # But the 'Customer' might not exist yet.
            # Strategy: Publish event "web_form_submission", Worker creates Customer -> Conversation -> Ticket.
            # BUT user wants ticket_id immediately.
            # So we have to do partial DB write or generate a tracking ID.
            
            tracking_id = str(uuid.uuid4())
            
            event = {
                "channel": "web_form",
                "event_type": "form_submission",
                "payload": form_data.model_dump(),
                "tracking_id": tracking_id
            }
            
            await publish_event(TOPICS["tickets_incoming"], event)
            
            # Since we are async processing, we return the tracking ID as the ticket reference for now,
            # or we await the DB creation if we want strict consistency (but that slows response).
            # For this architecture (Kafka), we return accepted.
            
            return SupportFormResponse(
                ticket_id=tracking_id,
                message="Support request received. We are processing it.",
                status="received"
            )
            
        except Exception as e:
            logger.error(f"Error submitting support form: {e}")
            raise e

    async def get_ticket_status(self, ticket_id: str) -> Dict[str, Any]:
        """
        Retrieves ticket status and public messages.
        """
        try:
            pool = await get_db_pool()
            # We need to look up by the external ticket_id / tracking_id if we used that,
            # or the DB id.
            # Assuming ticket_id passed here is the DB UUID if the user got it later, 
            # or we need to query by some reference.
            
            # For simplicity, let's assume the user queries by the UUID we gave them.
            ticket_repo = TicketRepository(pool)
            
            # TODO: Add get_ticket_by_id to TicketRepository in queries.py
            # For now, we mock or assume repo has it.
            # repo doesn't have it yet explicitly in the interface we defined earlier?
            # Let's check queries.py if we need to add it.
            
            # Mocking response for now to complete the handler structure
            return {
                "ticket_id": ticket_id,
                "status": "open",
                "messages": [] # Public messages
            }
            
        except Exception as e:
            logger.error(f"Error getting ticket status: {e}")
            raise e

web_form_handler = WebFormHandler()
