# Transition Guide: Incubation to Production

## Overview
This document outlines the journey from the initial "Incubation" phase (prototyping with Claude Code/General Agents) to the "Specialization" phase (building the production Custom Agent).

## 1. Discovery & Requirements
During incubation, we discovered the following key requirements for the Customer Success FTE:

-   **Multi-Channel Support**: Seamlessly handling Email (Gmail), Messaging (WhatsApp), and Web Forms.
-   **Conversation Continuity**: The need to link distinct identifiers (email, phone) to a single customer identity to preserve context.
-   **Escalation Logic**: Strict rules for when to hand off to humans (e.g., pricing disputes, legal threats, sentiment < 0.3).
-   **Response Formatting**: Tailoring output length and tone per channel (Email = formal/long, WhatsApp = concise/casual).

## 2. Artifact Transformation

| Component | Incubation (Prototype) | Production (Specialization) |
| :--- | :--- | :--- |
| **Agent Logic** | Single Python Script / MCP Server | `openai-agents` SDK + FastAPI |
| **Tools** | MCP Tool Definitions | `@function_tool` decorated functions with Pydantic models |
| **Database** | In-memory / JSON files | PostgreSQL 16 (Relational + `pgvector`) |
| **Ingestion** | Polling / Manual Trigger | Kafka Event Streaming (`fte.tickets.incoming`) |
| **Infrastructure** | Local Script | Kubernetes (API + Worker Pods + HPA) |
| **Config** | Hardcoded Constants | Environment Variables + Kubernetes Secrets |

## 3. Transition Checklist

### ✅ Codebase Restructuring
-   Refactored monolithic script into modular `backend/` structure.
-   Separated `agent/`, `channels/`, `workers/`, and `database/` concerns.
-   Implemented `Next.js` frontend for the Web Form channel.

### ✅ Tool Hardening
-   Converted `search_knowledge_base` to use PostgreSQL vector search.
-   Added `KnowledgeSearchInput`, `TicketInput` Pydantic models for strict validation.
-   Added error handling (circuit breakers) for external APIs (Gmail, Twilio).

### ✅ Production Prompt Engineering
-   Extracted system prompts to `backend/agent/prompts.py`.
-   Formalized "Hardware Constraints" (NEVER discuss pricing, ALWAYS create ticket).
-   Implemented dynamic context injection (Customer History, Channel requirements).

## 4. Next Steps
-   **Validation**: Run `backend/tests/e2e/test_24_hour_operation.py` to verify resilience.
-   **Monitoring**: Check Grafana/Metrics endpoint for "Escalation Rate" and "Channel Health".
-   **Maintenance**: Regularly update `backend/agent/prompts.py` based on new edge cases found in logs.
