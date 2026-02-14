import os
import base64
import json
import logging
from typing import Dict, Any, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from workers.kafka_config import publish_event, TOPICS

logger = logging.getLogger(__name__)

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailHandler:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """
        Authenticates with Gmail API using credentials.json or token.json.
        For server-side (headless), we usually use Service Account or stored token.
        Checking functionality for now with assumed token.
        """
        try:
            # In a real K8s env, we'd load from secrets/env var or a volume
            # For hackathon, we might skip actual auth if no token provided
            # and just mock the sending/receiving logic structure.
            if os.path.exists('token.json'):
                self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            if self.creds and self.creds.valid:
                self.service = build('gmail', 'v1', credentials=self.creds)
            else:
                logger.warning("Gmail credentials not found or invalid. Gmail handler will assume mock mode.")
        except Exception as e:
            logger.error(f"Gmail auth failed: {e}")

    async def process_notification(self, data: Dict[str, Any]):
        """
        Processes a Pub/Sub notification from Gmail.
        """
        try:
            # Decode the Pub/Sub message data
            if 'message' not in data or 'data' not in data['message']:
                logger.error("Invalid Pub/Sub message format")
                return

            pubsub_data = base64.b64decode(data['message']['data']).decode('utf-8')
            json_data = json.loads(pubsub_data)
            
            email_address = json_data.get('emailAddress')
            history_id = json_data.get('historyId')
            
            logger.info(f"Received Gmail notification for {email_address}, historyId: {history_id}")
            
            # Use historyId to fetch changes/new messages
            if self.service:
                # changes = self.service.users().history().list(userId='me', startHistoryId=history_id).execute()
                # For each new message, fetch full details
                # msg_details = self.service.users().messages().get(userId='me', id=msg_id).execute()
                pass
            
            # For Hackathon MVP (without live Pub/Sub), we might receive a direct payload 
            # simulating an email for testing.
            # payload = { "sender": "...", "subject": "...", "body": "..." }
            
            # Publish to Kafka for the worker to process
            # We wrap the raw data or extracted email data
            event = {
                "channel": "email",
                "raw_data": json_data,
                "event_type": "email_received"
            }
            await publish_event(TOPICS["tickets_incoming"], event)
            
        except Exception as e:
            logger.error(f"Error processing Gmail notification: {e}")
            raise e

    def send_reply(self, to_email: str, subject: str, body: str, thread_id: Optional[str] = None):
        """
        Sends an email reply.
        """
        try:
            if not self.service:
                logger.info(f"[MOCK] Sending Email to {to_email}: {subject}")
                return

            message = self._create_message(to_email, subject, body, thread_id)
            sent_message = self.service.users().messages().send(userId='me', body=message).execute()
            logger.info(f"Email sent: {sent_message['id']}")
            return sent_message
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise e

    def _create_message(self, to: str, subject: str, body: str, thread_id: Optional[str] = None):
        """Create a message for an email."""
        from email.mime.text import MIMEText
        import base64

        message = MIMEText(body, 'html')
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw}
        if thread_id:
            body['threadId'] = thread_id
            
        return body

# Singleton instance
gmail_handler = GmailHandler()
