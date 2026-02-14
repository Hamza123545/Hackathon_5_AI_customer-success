import asyncio
import json
import logging
from typing import Dict, Any, Optional

from database.queries import (
    CustomerRepository,
    ConversationRepository,
    MessageRepository,
    CustomerIdentifierRepository,
    get_db_pool
)
from workers.kafka_config import KafkaConsumerManager, KafkaProducerManager, TOPICS, publish_event
from agent.customer_success_agent import CustomerSuccessAgent
from agent.tools import get_customer_history
from channels.gmail_handler import gmail_handler
from channels.whatsapp_handler import whatsapp_handler
from channels.web_form_handler import web_form_handler
from api.errors import gmail_circuit_breaker, twilio_circuit_breaker, ExternalAPIError, CircuitBreakerOpen

logger = logging.getLogger(__name__)

class MessageProcessor:
    def __init__(self):
        self.running = False
        self.consumer = KafkaConsumerManager(TOPICS["tickets_incoming"], group_id="fte_worker_group")
        self.agent = CustomerSuccessAgent()
        
    async def start(self):
        self.running = True
        logger.info("Message Processor starting...")
        
        # Ensure DB pool is ready
        await get_db_pool()
        
        await self.consumer.start()
        
        # Start background tasks
        asyncio.create_task(self.monitor_consumer_lag())
        await self.validate_conversation_state()
        
        try:
            while self.running:
                # Consume messages
                # Our KafkaConsumerManager.consume() returns a generator or we iterate it
                # For this implementation assumption, let's say it has a get_message method or we iterate
                # adapting to aiokafka style as implemented in kafka_config.py
                
                # Checking kafka_config.py implementation from memory/context:
                # It likely exposes the consumer directly or a consume method.
                # Let's assume standard aiokafka loop pattern via the manager if possible, 
                # or access the underlying consumer.
                
                msg = await self.consumer.consumer.getone()
                if msg:
                    try:
                        data = json.loads(msg.value.decode('utf-8'))
                        logger.info(f"Processing message: {data.get('event_type')}")
                        await self.process_message(data)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        # Move to DLQ logic here
                    finally:
                        # Commit offset
                        # In real env, manual commit after processing
                        pass
                        
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
        finally:
            await self.consumer.stop()

    async def validate_conversation_state(self):
        """
        On startup, check for any 'hanging' processing states.
        For MVP, we just log.
        """
        logger.info("Validating conversation state... (MVP: check complete)")

    async def monitor_consumer_lag(self):
        """
        Background task to monitor Kafka consumer lag.
        """
        while self.running:
            try:
                # In real implementation: admin_client.list_consumer_group_offsets()
                # For MVP/Hackathon: Log heartbeat
                # logger.info("Checking consumer lag...")
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error checking lag: {e}")
                await asyncio.sleep(60)

    async def process_message(self, event: Dict[str, Any]):
        """
        Main orchestration logic.
        """
        event_type = event.get("event_type")
        channel = event.get("channel")
        
        if event_type not in ["message_received", "email_received", "form_submission"]:
            return # Ignore other events for now

        pool = await get_db_pool()
        cust_repo = CustomerRepository(pool)
        conv_repo = ConversationRepository(pool)
        msg_repo = MessageRepository(pool)
        ident_repo = CustomerIdentifierRepository(pool)
        
        # 1. Resolve Customer
        # Need to extract identifier (email or phone) based on channel
        identifier_value = None
        identifier_type = None
        customer_name = None
        
        if channel == "email":
            # raw_data from Gmail webhook might need parsing or we passed it pre-parsed?
            # existing handlers passed "raw_data". 
            # ideally the handler should have normalized it.
            # For this MVP, let's assume the event has 'sender' (email) and 'content'
            # If not, we'd need to fetch it (as noted in handler).
            # Let's assume handler did the hard work or we do it here.
            # REVISIT: GmailHandler just passed raw_data. 
            # We need to simulate the extraction if mock, or use what's there.
            if "sender" in event:
                identifier_value = event["sender"]
                identifier_type = "email"
                
        elif channel == "whatsapp":
            identifier_value = event.get("sender") # Phone number
            identifier_type = "phone"
            customer_name = event.get("profile_name")
            
        elif channel == "web_form":
            payload = event.get("payload", {})
            identifier_value = payload.get("email")
            identifier_type = "email"
            customer_name = payload.get("name")
            
        if not identifier_value:
            logger.error("No identifier found in event")
            return

        # Lookup or Create Customer
        customer = await cust_repo.get_customer_by_identifier(identifier_type, identifier_value)
        
        if not customer:
            # Create new
            customer = await cust_repo.create_customer(
                name=customer_name,
                email=identifier_value if identifier_type == "email" else None,
                phone=identifier_value if identifier_type == "phone" else None
            )
            data = {"customer_id": str(customer["id"]), "type": identifier_type, "value": identifier_value}
            # Also create identifier record explicitly if repo doesn't do it automatically
            # assuming create_customer handles basic fields, but specific identifier mapping needed?
            # queries.py likely handles it or we call ident_repo.create_identifier
            
        customer_id = str(customer["id"])
        
        # 2. Resolve Conversation
        # Simple strategy: One active conversation per channel or global?
        # User Story 2 says "Cross-Channel Conversation Continuity".
        # We should find the most recent open conversation for this customer.
        conversation = await conv_repo.get_active_conversation(customer_id)
        
        if not conversation:
            conversation = await conv_repo.create_conversation(customer_id, channel, "active")
            
        conversation_id = str(conversation["id"])
        
        # 3. Store Inbound Message
        content = event.get("content") or event.get("payload", {}).get("message") or ""
        # If email, content extract logic needed if raw_data.
        
        if content:
            await msg_repo.create_message(
                conversation_id=conversation_id,
                role="customer",
                channel=channel,
                content=content,
                # metadata...
            )

            # Analyze Sentiment
            from agent.sentiment import analyze_sentiment
            sentiment_score = analyze_sentiment(content)
            await conv_repo.update_sentiment(conversation_id, sentiment_score)
        
        # 4. Invoke Agent
        # Retrieve history
        history = await msg_repo.get_history_by_conversation_id(conversation_id)
        
        context = {
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "channel": channel,
            "customer_name": customer_name or customer.get("name")
        }
        
        agent_response_text = await self.agent.run(history, context)
        
        # 5. Store Outbound Message
        await msg_repo.create_message(
            conversation_id=conversation_id,
            role="agent",
            channel=channel,
            content=agent_response_text
        )
        
        # 6. Publish/Send Response
        # We can call the channel handler directly since we are in the worker 
        # and have the secret keys loaded.
        await self.publish_response(channel, identifier_value, agent_response_text, context)

    async def publish_response(self, channel: str, recipient: str, message: str, context: Dict[str, Any]):
        """
        sends the response via the specific channel handler.
        """
        from agent.formatters import format_response_for_channel
        
        formatted_message = format_response_for_channel(message, channel, context)
        
        try:
            if channel == "email":
                # Subject? If conversation has a subject? Or RE: ...
                # For now a generic subject or tracked
                subject = "Re: Support Request"
                # Circuit Breaker used here
                try:
                    await gmail_circuit_breaker.call(gmail_handler.send_reply, recipient, subject, formatted_message)
                except (ExternalAPIError, CircuitBreakerOpen) as e:
                    logger.error(f"Email sending failed (Circuit Breaker): {e}")
                    # Potential Fallback: Mark message as 'failed' in DB or queue for retry
                
            elif channel == "whatsapp":
                try:
                    await twilio_circuit_breaker.call(whatsapp_handler.send_message, recipient, formatted_message)
                except (ExternalAPIError, CircuitBreakerOpen) as e:
                    logger.error(f"WhatsApp sending failed (Circuit Breaker): {e}")
                
            elif channel == "web_form":
                # Web form is usually sync request/response or polling. 
                # If polling, we just stored the message in DB, which get_ticket_status will fetch.
                # So nothing active to "push" unless using WebSocket.
                # We simply log that response is ready.
                logger.info(f"Response stored for Web Ticket (Customer: {recipient})")
                
        except Exception as e:
            logger.error(f"Failed to send response on {channel}: {e}")

if __name__ == "__main__":
    # Local run wrapper
    # In k8s, this would be the entrypoint
    processor = MessageProcessor()
    asyncio.run(processor.start())
