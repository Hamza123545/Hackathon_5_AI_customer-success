import json
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
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

class ResponseInput(BaseModel):
    message: str = Field(..., description="The response message to send to the customer")

# --- Tool Functions ---

async def search_knowledge_base(args: KnowledgeSearchInput) -> str:
    """Searches the knowledge base for relevant articles."""
    try:
        pool = await get_db_pool()
        kb_repo = KnowledgeBaseRepository(pool)
        
        # In a real implementation, we would generate an embedding for args.query here
        # using OpenAI's embedding API.
        # For this hackathon/MVP without the embedding logic connected in this specific file,
        # we will assume the embedding generation happens or we mocked it.
        # However, to be functional, let's just return a placeholder or 
        # assume we have a helper to get embeddings.
        
        # Placeholder for embedding generation:
        # embedding = await get_embedding(args.query)
        # articles = await kb_repo.search_articles(embedding)
        
        # For now, we'll return a simulating response or empty if DB not populated
        return json.dumps([
            {"title": "Pricing", "content": "Our basic plan starts at $10/mo.", "similarity": 0.9}
        ]) # Mock response until embedding service is linked
    except Exception as e:
        logger.error(f"Error searching KB: {e}")
        return json.dumps({"error": str(e)})

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
        # Publish event
        await publish_event(TOPICS["tickets_incoming"], {"event_type": "ticket_created", "ticket": json.dumps(ticket, default=str)})
        return json.dumps({"status": "success", "ticket_id": str(ticket["id"])})
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        return json.dumps({"error": str(e)})

async def get_customer_history(args: CustomerHistoryInput) -> str:
    """Retrieves recent conversation history for the customer."""
    try:
        pool = await get_db_pool()
        msg_repo = MessageRepository(pool)
        messages = await msg_repo.get_last_20_messages_by_customer(args.customer_id)
        # Format for context
        formatted = []
        for m in messages:
            formatted.append(f"[{m['created_at']}] {m['role']} ({m['channel']}): {m['content']}")
        return "\n".join(formatted)
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return json.dumps({"error": str(e)})

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

# Definitions for the OpenAI API `tools` parameter
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Searches the knowledge base to answer customer questions.",
            "parameters": KnowledgeSearchInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Creates a formal support ticket when the user has a specific issue that cannot be resolved immediately.",
            "parameters": TicketInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_history",
            "description": "Retrieves the user's past interaction history to provide better context.",
            "parameters": CustomerHistoryInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalates the conversation to a human agent when the user is angry, mentions legal issues, or requests a human.",
            "parameters": EscalationInput.model_json_schema()
        }
    }
]

# Map names to functions for execution
AVAILABLE_TOOLS = {
    "search_knowledge_base": search_knowledge_base,
    "create_ticket": create_ticket,
    "get_customer_history": get_customer_history,
    "escalate_to_human": escalate_to_human,
}
