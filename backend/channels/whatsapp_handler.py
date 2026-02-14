import os
import logging
from typing import Dict, Any

from twilio.rest import Client
from twilio.request_validator import RequestValidator

from workers.kafka_config import publish_event, TOPICS

logger = logging.getLogger(__name__)

class WhatsAppHandler:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER") # e.g. "whatsapp:+14155238886"
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.validator = RequestValidator(self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not found. WhatsApp handler will assume mock mode.")

    def validate_webhook(self, url: str, params: Dict[str, Any], signature: str) -> bool:
        """
        Validates that the incoming webhook is from Twilio.
        """
        if not self.client:
            return True # Mock mode
        return self.validator.validate(url, params, signature)

    async def process_webhook(self, data: Dict[str, Any]):
        """
        Processes a webhook from Twilio.
        Data keys usually: Body, From, ProfileName, WaId, MessageSid
        """
        try:
            sender = data.get("From", "").replace("whatsapp:", "")
            body = data.get("Body", "")
            profile_name = data.get("ProfileName", "")
            
            logger.info(f"Received WhatsApp from {sender}: {body[:20]}...")
            
            event = {
                "channel": "whatsapp",
                "sender": sender,
                "profile_name": profile_name,
                "content": body,
                "event_type": "message_received",
                "raw_data": data
            }
            
            await publish_event(TOPICS["tickets_incoming"], event)
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {e}")
            raise e

    def send_message(self, to_number: str, body: str):
        """
        Sends a WhatsApp message via Twilio.
        """
        try:
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
                
            if not self.client:
                logger.info(f"[MOCK] Sending WhatsApp to {to_number}: {body}")
                return "mock_sid"

            message = self.client.messages.create(
                from_=self.from_number,
                body=body,
                to=to_number
            )
            logger.info(f"WhatsApp sent: {message.sid}")
            return message.sid
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {e}")
            raise e

# Singleton instance
whatsapp_handler = WhatsAppHandler()
