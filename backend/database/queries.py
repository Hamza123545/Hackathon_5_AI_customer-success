import os
import asyncpg
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

class DatabasePool:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                database=os.getenv("POSTGRES_DB", "fte_db"),
                user=os.getenv("POSTGRES_USER", "user"),
                password=os.getenv("POSTGRES_PASSWORD", "password"),
                min_size=5,
                max_size=20,
            )
        return cls._pool

    @classmethod
    async def close_pool(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None

async def get_db_pool() -> asyncpg.Pool:
    return await DatabasePool.get_pool()

class BaseRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

class CustomerRepository(BaseRepository):
    async def create_customer(self, email: Optional[str], phone: Optional[str], name: Optional[str], metadata: Dict = {}) -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO customers (email, phone, name, metadata)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """, email, phone, name, json.dumps(metadata))
            return dict(row)

    async def get_customer_by_email(self, email: str) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM customers WHERE email = $1", email)
            return dict(row) if row else None

    async def get_customer_by_phone(self, phone: str) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM customers WHERE phone = $1", phone)
            return dict(row) if row else None

class CustomerIdentifierRepository(BaseRepository):
    async def create_identifier(self, customer_id: str, identifier_type: str, identifier_value: str, verified: bool = False) -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value, verified)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """, customer_id, identifier_type, identifier_value, verified)
            return dict(row)
    
    async def get_identifiers_by_customer_id(self, customer_id: str) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM customer_identifiers WHERE customer_id = $1", customer_id)
            return [dict(row) for row in rows]

class ConversationRepository(BaseRepository):
    async def create_conversation(self, customer_id: str, initial_channel: str, status: str = 'active') -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO conversations (customer_id, initial_channel, status)
                VALUES ($1, $2, $3)
                RETURNING *
            """, customer_id, initial_channel, status)
            return dict(row)

    async def get_active_conversation(self, customer_id: str) -> Optional[Dict]:
         async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM conversations 
                WHERE customer_id = $1 AND status = 'active'
                ORDER BY started_at DESC LIMIT 1
            """, customer_id)
            return dict(row) if row else None
            
    async def update_conversation_status(self, conversation_id: str, status: str) -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                UPDATE conversations SET status = $2, ended_at = CASE WHEN $2 IN ('resolved', 'escalated') THEN CURRENT_TIMESTAMP ELSE NULL END
                WHERE id = $1
                RETURNING *
            """, conversation_id, status)
            return dict(row)

class MessageRepository(BaseRepository):
    async def create_message(self, conversation_id: str, channel: str, direction: str, role: str, content: str, tool_calls: Optional[Dict] = None) -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO messages (conversation_id, channel, direction, role, content, tool_calls)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """, conversation_id, channel, direction, role, content, json.dumps(tool_calls) if tool_calls else None)
            return dict(row)

    async def get_last_20_messages_by_customer(self, customer_id: str) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT m.* FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.customer_id = $1
                ORDER BY m.created_at DESC
                LIMIT 20
            """, customer_id)
            return [dict(row) for row in rows]

class TicketRepository(BaseRepository):
    async def create_ticket(self, conversation_id: str, customer_id: str, source_channel: str, category: str, priority: str = 'medium') -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO tickets (conversation_id, customer_id, source_channel, category, priority)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            """, conversation_id, customer_id, source_channel, category, priority)
            return dict(row)

    async def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tickets WHERE id = $1", ticket_id)
            return dict(row) if row else None

class KnowledgeBaseRepository(BaseRepository):
    async def search_articles(self, embedding: List[float], limit: int = 5) -> List[Dict]:
        async with self.pool.acquire() as conn:
            # Requires pgvector extension
            rows = await conn.fetch("""
                SELECT id, title, content, category, 1 - (embedding <=> $1) as similarity
                FROM knowledge_base
                ORDER BY embedding <=> $1
                LIMIT $2
            """, str(embedding), limit)
            return [dict(row) for row in rows]

class EscalationRepository(BaseRepository):
    async def create_escalation(self, conversation_id: str, reason: str, full_context: Dict) -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO escalations (conversation_id, reason, full_context)
                VALUES ($1, $2, $3)
                RETURNING *
            """, conversation_id, reason, json.dumps(full_context))
            return dict(row)

class AgentMetricsRepository(BaseRepository):
    async def record_metric(self, metric_name: str, metric_value: float, channel: Optional[str] = None, dimensions: Dict = {}) -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO agent_metrics (metric_name, metric_value, channel, dimensions)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """, metric_name, metric_value, channel, json.dumps(dimensions))
            return dict(row)
