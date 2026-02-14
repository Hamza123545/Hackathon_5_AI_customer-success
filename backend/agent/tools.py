import json
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from agents import function_tool
from database.queries import (
    KnowledgeBaseRepository,
    TicketRepository,
    MessageRepository,
    EscalationRepository,
    get_db_pool
)
from workers.kafka_config import publish_event, TOPICS

logger = logging.getLogger(__name__)

# --- Pydantic Input Models ---

class KnowledgeSearchInput(BaseModel):
    query: str = Field(..., description="The user's question or search query")

class TicketInput(BaseModel):
    customer_id: str = Field(..., description="UUID of the customer")
    conversation_id: str = Field(..., description="UUID of the conversation")
    activity_channel: str = Field(..., description="Source channel (email, whatsapp, web_form)")
    category: str = Field(..., description="Category: general, technical, billing, feedback, bug_report")
    priority: str = Field("medium", description="Priority: low, medium, high, critical")
    description: str = Field(..., description="Summary of the issue for the ticket")

class CustomerHistoryInput(BaseModel):
    customer_id: str = Field(..., description="UUID of the customer")

class EscalationInput(BaseModel):
    conversation_id: str = Field(..., description="UUID of the conversation")
    reason: str = Field(..., description="Reason for escalation: pricing, refund, legal, anger, human_request")
    context_summary: str = Field(..., description="Brief summary of why escalation is needed")

# --- Tool Functions ---

@function_tool
async def search_knowledge_base(args: KnowledgeSearchInput) -> str:
    """Searches the knowledge base for relevant articles."""
    try:
        pool = await get_db_pool()
        kb_repo = KnowledgeBaseRepository(pool)
        
        # Placeholder for embedding generation:
        # embedding = await get_embedding(args.query)
        # articles = await kb_repo.search_articles(embedding)
        
        # Mock response
        return json.dumps([
            {"title": "Pricing", "content": "Our basic plan starts at $10/mo.", "similarity": 0.9}
        ]) 
    except Exception as e:
        logger.error(f"Error searching KB: {e}")
        return json.dumps({"error": str(e)})

@function_tool
async def create_ticket(args: TicketInput) -> str:
    """Creates a support ticket."""
    try:
        pool = await get_db_pool()
        ticket_repo = TicketRepository(pool)
        ticket = await ticket_repo.create_ticket(
            conversation_id=args.conversation_id,
            customer_id=args.customer_id,
            source_channel=args.activity_channel,
            category=args.category,
            priority=args.priority
        )
        await publish_event(TOPICS["tickets_incoming"], {"event_type": "ticket_created", "ticket": json.dumps(ticket, default=str)})
        return json.dumps({"status": "success", "ticket_id": str(ticket["id"])})
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        return json.dumps({"error": str(e)})

@function_tool
async def get_customer_history(args: CustomerHistoryInput) -> str:
    """Retrieves recent conversation history for the customer."""
    try:
        pool = await get_db_pool()
        msg_repo = MessageRepository(pool)
        messages = await msg_repo.get_last_20_messages_by_customer(args.customer_id)
        formatted = []
        for m in messages:
            formatted.append(f"[{m['created_at']}] {m['role']} ({m['channel']}): {m['content']}")
        return "\n".join(formatted)
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return json.dumps({"error": str(e)})

@function_tool
async def escalate_to_human(args: EscalationInput) -> str:
    """Escalates the conversation to a human agent."""
    try:
        pool = await get_db_pool()
        esc_repo = EscalationRepository(pool)
        escalation = await esc_repo.create_escalation(
            conversation_id=args.conversation_id,
            reason=args.reason,
            full_context={"summary": args.context_summary}
        )
        await publish_event(TOPICS["escalations"], {"event_type": "escalation_created", "escalation": json.dumps(escalation, default=str)})
        return json.dumps({"status": "escalated", "escalation_id": str(escalation["id"])})
    except Exception as e:
        logger.error(f"Error escalating: {e}")
        return json.dumps({"error": str(e)})

# List of tools to be passed to the Agent
AGENT_TOOLS = [
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human
]
