-- Initial Schema Migration
-- Applied during startup if tables do not exist
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customer_identifiers_value ON customer_identifiers(identifier_value);
CREATE INDEX IF NOT EXISTS idx_conversations_customer ON conversations(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_channel ON tickets(source_channel);
-- Vector Index (HNSW) for Knowledge Base
-- Note: Requires data to be effective, but creating structure here
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_base USING hnsw (embedding vector_cosine_ops);