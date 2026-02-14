# Plan: Customer Success Digital FTE
## Technical Context

This project implements a production-grade AI-powered Digital Full-Time Employee (FTE) for customer support using the Agent Maturity Model (Incubation → Specialization → Production). The system handles multi-channel customer inquiries (Gmail, WhatsApp, Web Form) with unified context, intelligent escalation, and 24/7 operational excellence.

### Technology Stack Decisions

**Core Framework & Language**:
- **Python 3.11+**: Chosen for async/await patterns, extensive AI/ML library support
- **FastAPI**: Modern async web framework with automatic OpenAPI documentation, built-in validation
- **OpenAI Agents SDK**: Production agent framework with @function_tool decorators, Pydantic validation
- **asyncpg**: PostgreSQL async driver for non-blocking database operations

**Data & Streaming**:
- **PostgreSQL 16 with pgvector extension**: Selected as CRM (NOT external CRM like Salesforce/HubSpot)
  - Rationale: Vector similarity search for knowledge base, relational data for customers/conversations/tickets, single source of truth
  - pgvector enables semantic search of support articles using OpenAI embeddings
- **Apache Kafka**: Event streaming for async message processing
  - Chosen alternatives: Redis (insufficient durability), RabbitMQ (less scalable)
  - Confluent Cloud acceptable for simplicity (reduces operational overhead)
  - Topics: fte.tickets.incoming (unified), fte.channels.email.inbound, fte.channels.whatsapp.inbound, fte.channels.web.inbound, fte.escalations, fte.metrics, fte.dlq

**Orchestration**:
- **Kubernetes**: Container orchestration for 24/7 operation
  - Chosen alternatives: Docker Compose (insufficient for production), Swarm (less mature)
  - minikube for local development, any cloud provider for production
  - Horizontal Pod Autoscaler (HPA) for API (3-20 pods) and Worker (3-30 pods)

**Channel Integrations**:
- **Gmail API with Pub/Sub**: Email integration via push notifications (not polling)
  - Webhook signature validation prevents spoofing
  - OAuth2 service account for programmatic access
- **Twilio WhatsApp API**: Messaging integration
  - Sandbox sufficient for development (no production WhatsApp Business account needed)
  - Request validator for webhook signature security
- **Web Support Form**: React/Next.js component
  - Standalone, embeddable form (NOT full website)
  - FastAPI endpoints for submission and status checking

### Architecture Principles

**Constitution Compliance**:
1. **Multi-Channel Customer-Centric Design**: All features work across Email (formal, ≤500 words), WhatsApp (concise, ≤300 chars), Web Form (semi-formal, ≤300 words)
2. **Agent Maturity Model**: Incubation (MCP prototype) → Specialization (OpenAI SDK, PostgreSQL, Kafka, K8s) → Production (24/7 validation)
3. **24/7 Operational Excellence**: Pod restarts, horizontal scaling, DLQ for failed messages, graceful degradation
4. **Cross-Channel Conversation Continuity**: >95% customer ID accuracy, last 20 messages retrieved, channel switches logged
5. **Test-Driven Reliability**: Red-Green-Refactor enforced, edge cases have tests, load/chaos tests mandatory
6. **Data Privacy & Security**: No credentials in code, Kubernetes Secrets, webhook validation, PII redaction
7. **Observability & Metrics**: Structured JSON logs, 4 metric levels (channel/agent/system/business), alerting thresholds

### Performance Targets

**Non-Functional Requirements**:
- **Latency**: P95 response time < 3 seconds (processing), < 30 seconds (delivery SLA)
- **Throughput**: 100+ concurrent users, 100+ inquiries/day (scaling tested)
- **Uptime**: >99.9% (excluding planned maintenance)
- **Escalation Rate**: <25% of total conversations
- **Cross-Channel ID**: >95% accuracy (email/phone → unified customer_id)
- **Cost Efficiency**: <$1,000/year operating cost (vs $75,000/year human FTE)

**Data Volume**:
- Knowledge base: 100+ articles (initial seed)
- Customer conversations: Retained indefinitely (MVP - no auto-deletion)
- Message history: Last 20 messages retrieved per response (configurable)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           MULTI-CHANNEL INTEGRATION LAYER                         │
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │ Gmail Webhook │    │Twilio Webhook │    │  Web Form     │                  │
│   │   (Email)    │    │  (WhatsApp)  │    │   (API)      │                  │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│          │                   │                 │                  │                          │
│          └───────────────────┼─────────────────┘                  │                          │
│                             ▼                                  ▼                          │
│                    ┌─────────────────────────────────────────┐                          │
│                    │     FastAPI (API Gateway)         │                          │
│                    │  /webhooks/{gmail,whatsapp}      │                          │
│                    │  /support/submit, /ticket/{id}      │                          │
│                    │  /conversations/{id}, /customers/lookup│                          │
│                    │  /metrics/channels, /health          │                          │
│                    └────────────────┬────────────────────┘                          │
│                                   ▼                                       │
│                    ┌───────────────────────────────────┐                          │
│                    │  Kafka (Event Streaming)        │                          │
│                    │  Topics:                       │                          │
│                    │  - fte.tickets.incoming (unified)│                          │
│                    │  - fte.channels.*.inbound      │                          │
│                    │  - fte.channels.*.outbound     │                          │
│                    │  - fte.escalations              │                          │
│                    │  - fte.metrics                   │                          │
│                    │  - fte.dlq (dead letter)        │                          │
│                    └────────────┬────────────────────┘                          │
│                             ▼                                       │
│              ┌──────────────────────────────────────┐                    │
│              │  Processing Layer (Worker Pods)  │                    │
│              │  Kafka Consumer Group             │                    │
│              │  OpenAI Agents SDK Runner          │                    │
│              │  Tools:                        │                    │
│              │  - search_knowledge_base (pgvector)│                    │
│              │  - create_ticket                 │                    │
│              │  - get_customer_history          │                    │
│              │  - escalate_to_human             │                    │
│              │  - send_response                 │                    │
│              └────────────┬───────────────────────┘                    │
│                    │                                  │                    ┌─────────────────┐
│                    │                                  │                    │  PostgreSQL 16   │
│                    │                                  │                    │  + pgvector      │
│                    │                                  │                    │  - customers     │
│                    │                                  │                    │  - customer_identifiers
│                    │                                  │                    │  - conversations  │
│                    │                                  │                    │  - messages       │
│                    │                                  │                    │  - tickets        │
│                    │                                  │                    │  - knowledge_base │
│                    │                                  │                    │  - escalations   │
│                    │                                  │                    │  - channel_configs│
│                    │                                  │                    └─────────────────┘
│                    │                                  │
│              ┌──────────────────────────────────────┐                    │
│              │  Channel Response Layer           │                    │
│              │  - Gmail API (send reply)        │                    │
│              │  - Twilio WhatsApp (send)        │                    │
│              │  - Email notification (web)      │                    │
│              └───────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Component Design

**1. API Gateway (FastAPI)**

**Responsibilities**:
- Receive webhooks from Gmail (Pub/Sub push) and Twilio WhatsApp
- Handle web form submissions and status checks
- Validate webhook signatures (Gmail Pub/Sub, Twilio)
- Publish inbound events to Kafka (fte.tickets.incoming topic)
- Provide health check and metrics endpoints
- CORS configuration for web form embedding

**Endpoints**:
- `POST /webhooks/gmail` - Gmail Pub/Sub push notifications
- `POST /webhooks/whatsapp` - Twilio webhook (signature validated)
- `POST /support/submit` - Web form submission with validation
- `GET /support/ticket/{ticket_id}` - Check ticket status
- `GET /conversations/{conversation_id}` - Get conversation history
- `GET /customers/lookup?email={email}&phone={phone}` - Cross-channel customer lookup
- `GET /metrics/channels` - Channel-specific metrics (response count, latency, escalation rate)
- `GET /health` - Health check (all channels status)

**Scaling**: 3-20 pods via Kubernetes HPA (target 70% CPU utilization)

**2. Message Processing Layer (Worker Pods)**

**Responsibilities**:
- Consume unified tickets from Kafka (fte.tickets.incoming)
- Resolve or create customer (email/phone → customer_id)
- Get or create conversation (24-hour active window)
- Retrieve customer history (last 20 messages across ALL channels)
- Run OpenAI Agent with tools
- Store inbound and outbound messages
- Publish metrics (fte.metrics topic)

**Agent Tools**:
```python
from agents import function_tool
from pydantic import BaseModel

class KnowledgeSearchInput(BaseModel):
    query: str
    max_results: int = 5

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """Search product documentation for relevant information.

    Use this when customer asks questions about product features,
    how to use something, or needs technical information.
    """
    # PostgreSQL pgvector similarity search
    # Returns formatted results with relevance scores
```

```python
class TicketInput(BaseModel):
    customer_id: str
    issue: str
    priority: str = "medium"
    category: str = "general"
    channel: str  # email/whatsapp/web_form

@function_tool
async def create_ticket(input: TicketInput) -> str:
    """Create a support ticket for tracking.

    ALWAYS create a ticket at the start of every conversation.
    Include source channel for proper tracking.
    """
    # Insert into tickets table
    # Returns ticket_id
```

```python
@function_tool
async def get_customer_history(customer_id: str) -> str:
    """Get customer's complete interaction history across ALL channels.

    Use this to understand context from previous conversations,
    even if they happened on a different channel.
    """
    # Join conversations + messages across all channels
    # Returns last 20 messages with channel metadata
```

```python
class EscalationInput(BaseModel):
    ticket_id: str
    reason: str  # pricing/refund/legal/anger/search_failed/human_request

@function_tool
async def escalate_to_human(input: EscalationInput) -> str:
    """Escalate conversation to human support.

    Use this when:
    - Customer asks about pricing or refunds
    - Customer sentiment is negative
    - You cannot find relevant information
    - Customer explicitly requests human help
    """
    # Update ticket status to 'escalated'
    # Publish to fte.escalations topic
```

```python
class ResponseInput(BaseModel):
    ticket_id: str
    message: str
    channel: str  # email/whatsapp/web_form

@function_tool
async def send_response(input: ResponseInput) -> str:
    """Send response to customer via their preferred channel.

    The response will be automatically formatted for channel:
    Email: Formal with greeting/signature
    WhatsApp: Concise and conversational
    Web: Semi-formal
    """
    # Call appropriate channel handler (Gmail API, Twilio, email notification)
```

**Scaling**: 3-30 worker pods via Kubernetes HPA

**3. PostgreSQL (CRM & Data Store)**

**Schema Design**:
- **customers**: Unified customer records
  - `id` (UUID, PK)
  - `email` (VARCHAR(255), UNIQUE, indexed)
  - `phone` (VARCHAR(50), indexed
  - `name` (VARCHAR(255))
  - `metadata` (JSONB)

- **customer_identifiers**: Cross-channel linking
  - `id` (UUID, PK)
  - `customer_id` (UUID, FK → customers)
  - `identifier_type` (VARCHAR: 'email'/'phone'/'whatsapp')
  - `identifier_value` (VARCHAR(255))
  - `verified` (BOOLEAN)
  - UNIQUE(identifier_type, identifier_value)

- **conversations**: Support threads
  - `id` (UUID, PK)
  - `customer_id` (UUID, FK → customers)
  - `initial_channel` (VARCHAR: 'email'/'whatsapp'/'web_form')
  - `started_at` (TIMESTAMPTZ)
  - `ended_at` (TIMESTAMPTZ, nullable)
  - `status` (VARCHAR: 'active'/'resolved'/'escalated')
  - `sentiment_score` (DECIMAL(3,2), -1.0 to 1.0)
  - `escalated_to` (VARCHAR(255), nullable)

- **messages**: All interactions
  - `id` (UUID, PK)
  - `conversation_id` (UUID, FK → conversations)
  - `channel` (VARCHAR: inbound_email/outbound_email/inbound_whatsapp/outbound_whatsapp/inbound_web/outbound_web)
  - `direction` (VARCHAR: 'inbound'/'outbound')
  - `role` (VARCHAR: 'customer'/'agent'/'system')
  - `content` (TEXT, NOT NULL)
  - `created_at` (TIMESTAMPTZ)
  - `tokens_used` (INTEGER)
  - `latency_ms` (INTEGER)
  - `tool_calls` (JSONB)
  - `channel_message_id` (VARCHAR(255)) - External ID (Gmail ID, Twilio SID)

- **tickets**: Support tickets
  - `id` (UUID, PK)
  - `conversation_id` (UUID, FK → conversations)
  - `customer_id` (UUID, FK → customers)
  - `source_channel` (VARCHAR: 'email'/'whatsapp'/'web_form')
  - `category` (VARCHAR(100))
  - `priority` (VARCHAR: 'low'/'medium'/'high')
  - `status` (VARCHAR: 'open'/'processing'/'resolved'/'escalated')
  - `created_at` (TIMESTAMPTZ)
  - `resolved_at` (TIMESTAMPTZ, nullable)
  - `resolution_notes` (TEXT)

- **knowledge_base**: Support documentation with vector embeddings
  - `id` (UUID, PK)
  - `title` (VARCHAR(500), NOT NULL
  - `content` (TEXT, NOT NULL)
  - `category` (VARCHAR(100))
  - `embedding` (VECTOR(1536)) - OpenAI text-embedding-3-small
  - `created_at` (TIMESTAMPTZ)
  - `updated_at` (TIMESTAMPTZ)
  - Index: `idx_knowledge_embedding` USING hnsw (embedding vector_cosine_ops)

- **escalations**: Human escalation tracking
  - `id` (UUID, PK)
  - `conversation_id` (UUID, FK → conversations)
  - `reason` (VARCHAR: pricing/refund/legal/anger/search_failed/human_request)
  - `full_context` (JSONB)
  - `status` (VARCHAR: 'pending'/'in_progress'/'resolved')
  - `created_at` (TIMESTAMPTZ)
  - `resolved_at` (TIMESTAMPTZ, nullable)

- **channel_configs**: Channel-specific settings
  - `id` (UUID, PK)
  - `channel` (VARCHAR: 'email'/'whatsapp'/'web_form'), UNIQUE
  - `enabled` (BOOLEAN)
  - `config` (JSONB) - API keys, webhook URLs, etc.
  - `response_template` (TEXT)
  - `max_response_length` (INTEGER)

- **agent_metrics**: Performance tracking
  - `id` (UUID, PK)
  - `metric_name` (VARCHAR(100))
  - `metric_value` (DECIMAL(10,4))
  - `channel` (VARCHAR(50), nullable
  - `dimensions` (JSONB)
  - `recorded_at` (TIMESTAMPTZ)

**Connection Pooling**:
```python
import asyncpg

pool = asyncpg.create_pool(
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    min_size=5,  # Minimum connections
    max_size=20,  # Maximum connections
    command_timeout=60
)
```

**Indexes for Performance**:
- `idx_customers_email` ON customers(email)
- `idx_customer_identifiers_value` ON customer_identifiers(identifier_value)
- `idx_conversations_customer` ON conversations(customer_id)
- `idx_conversations_status` ON conversations(status)
- `idx_messages_conversation` ON messages(conversation_id)
- `idx_messages_channel` ON messages(channel)
- `idx_tickets_status` ON tickets(status)
- `idx_tickets_channel` ON tickets(source_channel)
- `idx_knowledge_embedding` ON knowledge_base USING hnsw (embedding vector_cosine_ops)

**4. Kafka Event Streaming**

**Topic Architecture**:
- `fte.tickets.incoming` - Unified inbound queue (all channels publish here)
- `fte.channels.email.inbound` - Gmail-specific (future partitioning)
- `fte.channels.whatsapp.inbound` - WhatsApp-specific (future partitioning)
- `fte.channels.web.inbound` - Web form-specific (future partitioning)
- `fte.channels.email.outbound` - Email responses
- `fte.channels.whatsapp.outbound` - WhatsApp responses
- `fte.escalations` - Human escalation events
- `fte.metrics` - Performance metrics (channel-level, agent-level, system-level)
- `fte.dlq` - Dead letter queue (failed messages)

**Producer Patterns**:
```python
from aiokafka import AIOKafkaProducer

producer = AIOKafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

async def publish(topic: str, event: dict):
    event["timestamp"] = datetime.utcnow().isoformat()
    await producer.send_and_wait(topic, event)
```

**Consumer Patterns**:
```python
from aiokafka import AIOKafkaConsumer

consumer = AIOKafkaConsumer(
    topics=[TOPICS['tickets.incoming']],
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    group_id="fte-message-processor",
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

await consumer.start()
async for msg in consumer:
    await process_message(msg.topic, msg.value)
```

**Exactly-Once Semantics**:
- Enable `enable.idempotence` for producer
- Consumer commits offsets only after successful processing
- Failed messages → DLQ (fte.dlq topic) for human review
- Transactional produce/consume for complex workflows

**5. Channel Handlers**

**Gmail Handler** (channels/gmail_handler.py):
- `setup_push_notifications()` - Configure Pub/Sub push for INBOX label
- `process_notification()` - Fetch new messages since history_id
- `get_message()` - Retrieve full message with headers, body, thread_id
- `send_reply()` - Send via Gmail API with threading support
- `_extract_body()` - Parse base64 encoded email body
- `_extract_email()` - Extract email address from From header

**WhatsApp Handler** (channels/whatsapp_handler.py):
- `validate_webhook()` - Twilio signature validation (CRITICAL for security)
- `process_webhook()` - Parse Twilio webhook: MessageSid, From, Body, ProfileName
- `send_message()` - Send via Twilio API
- `format_response()` - Split long responses (>300 chars) into multiple messages
- Twilio WhatsApp Sandbox for development (free testing)

**Web Form Handler** (channels/web_form_handler.py):
- FastAPI router: `/support` prefix
- Pydantic models: `SupportFormSubmission`, `SupportFormResponse`
- Validators: Name (≥2 chars), Email (EmailStr), Subject (≥5 chars), Message (≥10 chars), Category (general/technical/billing/feedback/bug_report)
- `submit_support_form()` - Create ticket, publish to Kafka, return ticket_id
- `get_ticket_status()` - Retrieve ticket with messages
- CORS enabled for embedding
- React/Next.js component provided (standalone, embeddable)

**6. Kubernetes Deployment**

**Namespace**: `customer-success-fte`

**ConfigMap** (fte-config):
- `ENVIRONMENT`: "production"
- `LOG_LEVEL`: "INFO"
- `KAFKA_BOOTSTRAP_SERVERS`: "kafka.kafka.svc.cluster.local:9092"
- `POSTGRES_HOST`: "postgres.customer-success-fte.svc.cluster.local"
- `POSTGRES_DB`: "fte_db"
- Channel configs: `GMAIL_ENABLED`, `WHATSAPP_ENABLED`, `WEBFORM_ENABLED`
- Response limits: `MAX_EMAIL_LENGTH` (2000), `MAX_WHATSAPP_LENGTH` (1600), `MAX_WEBFORM_LENGTH` (1000)

**Secrets** (fte-secrets, type=Opaque):
- `OPENAI_API_KEY`
- `POSTGRES_PASSWORD`
- `GMAIL_CREDENTIALS` (JSON)
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER`

**Deployments**:
- `fte-api` (FastAPI gateway): 3 replicas → 20 max (HPA based on CPU 70%)
  - Resources: 512Mi/250m → 1Gi/500m
  - Health checks: liveness (10s delay), readiness (5s delay)
- `fte-message-processor` (Workers): 3 replicas → 30 max (HPA based on CPU 70%)
  - Resources: 512Mi/250m → 1Gi/500m

**Services**:
- `customer-success-fte` (Service): Port 80, targetPort 8000
- Ingress: TLS with Let's Encrypt, host: support-api.yourdomain.com

**Ingress**:
- Annotations: `kubernetes.io/ingress.class: nginx`, `cert-manager.io/cluster-issuer: letsencrypt-prod`
- TLS: support-api.yourdomain.com
- Rules: host → / path: Prefix → backend: customer-success-fte:80

**Horizontal Pod Autoscalers**:
- `fte-api-hpa`: Scale `fte-api` deployment, min 3, max 20, target 70% CPU
- `fte-worker-hpa`: Scale `fte-message-processor`, min 3, max 30, target 70% CPU

## Data Model

**Entity Relationships**:
```
Customer (1) ──────┐ (N) CustomerIdentifier
         │
         │
         ├─────────────────┐ (1) Conversation
         │               │
         │               ├─────────────────┐ (N) Message
         │               │
         │               └─────────────────┘ (1) Ticket
         │
         └─────────────────┐ (1) Escalation
                         │
                         └─────────────────┘
```

**State Transitions** (Conversation):
- `active` → `escalated` (human intervention required)
- `active` → `resolved` (agent resolved without escalation)
- `escalated` → `resolved` (human resolved)

**State Transitions** (Ticket):
- `open` → `processing` (agent working)
- `processing` → `resolved` (agent completed)
- `processing` → `escalated` (escalation required)

## API Contracts

**OpenAPI Specification** (auto-generated by FastAPI):

**POST /webhooks/gmail**
- Description: Gmail Pub/Sub push notifications
- Request Body: Pub/Sub message format
- Response: 200 OK with count of processed messages
- Errors: 500 Internal Server Error

**POST /webhooks/whatsapp**
- Description: Twilio webhook (signature validated)
- Request Body: form-data (MessageSid, From, Body, ProfileName)
- Response: 200 OK (empty TwiML response for immediate reply)
- Errors: 403 Forbidden (invalid signature)

**POST /support/submit**
- Description: Web form submission
- Request Body:
  ```json
  {
    "name": "string (≥2 chars)",
    "email": "email format",
    "subject": "string (≥5 chars)",
    "category": "general|technical|billing|feedback|bug_report",
    "message": "string (≥10 chars)"
  }
  ```
- Response: 200 OK
  ```json
  {
    "ticket_id": "uuid",
    "message": "Thank you for contacting us! Our AI assistant will respond shortly.",
    "estimated_response_time": "Usually within 5 minutes"
  }
  ```
- Errors: 422 Validation Error (detail: specific field error)

**GET /support/ticket/{ticket_id}**
- Description: Check ticket status and conversation history
- Response: 200 OK
  ```json
  {
    "ticket_id": "uuid",
    "status": "open|processing|resolved|escalated",
    "messages": [
      {
        "role": "customer|agent|system",
        "channel": "inbound_email|outbound_email|...",
        "content": "message text",
        "created_at": "ISO-8601 timestamp"
      }
    ],
    "created_at": "ISO-8601 timestamp",
    "last_updated": "ISO-8601 timestamp"
  }
  ```
- Errors: 404 Not Found

**GET /conversations/{conversation_id}**
- Description: Get full conversation history with cross-channel context
- Response: 200 OK
  ```json
  {
    "conversation_id": "uuid",
    "customer_id": "uuid",
    "messages": [
      {
        "channel": "email",
        "content": "...",
        "role": "customer",
        "created_at": "timestamp"
      }
    ],
    "initial_channel": "email",
    "started_at": "timestamp"
  }
  ```
- Errors: 404 Not Found

**GET /customers/lookup**
- Query Params: `email` (optional), `phone` (optional)
- Description: Cross-channel customer lookup
- Response: 200 OK
  ```json
  {
    "customer_id": "uuid",
    "email": "john@example.com",
    "phone": "+15550100",
    "conversations": [
      {
        "conversation_id": "uuid",
        "status": "active",
        "channel": "email",
        "started_at": "timestamp"
      }
    ]
  }
  ```
- Errors: 400 Bad Request (both params missing), 404 Not Found

**GET /metrics/channels**
- Description: Channel-specific performance metrics
- Response: 200 OK
  ```json
  {
    "email": {
      "total_conversations": 150,
      "avg_sentiment": 0.2,
      "escalations": 30
    },
    "whatsapp": {
      "total_conversations": 200,
      "avg_sentiment": 0.15,
      "escalations": 25
    },
    "web_form": {
      "total_conversations": 100,
      "avg_sentiment": 0.25,
      "escalations": 20
    }
  }
  ```

**GET /health**
- Response: 200 OK
  ```json
  {
    "status": "healthy",
    "timestamp": "ISO-8601 timestamp",
    "channels": {
      "email": "active",
      "whatsapp": "active",
      "web_form": "active"
    }
  }
  ```

## Deployment Architecture

**Development Environment** (minikube):
```bash
minikube start  # 3 nodes: control-plane + 2 workers
kubectl apply -f k8s/
```

**Production Environment** (cloud provider):
1. Create namespace: `kubectl create namespace customer-success-fte`
2. Deploy secrets: `kubectl apply -f k8s/secrets.yaml`
3. Deploy config: `kubectl apply -f k8s/configmap.yaml`
4. Deploy PostgreSQL: `kubectl apply -f k8s/postgres/`
5. Deploy Kafka: (Confluent Cloud or self-hosted)
6. Deploy application: `kubectl apply -f k8s/deployment-api.yaml k8s/deployment-worker.yaml`
7. Expose services: `kubectl apply -f k8s/service.yaml k8s/ingress.yaml`
8. Configure HPA: `kubectl apply -f k8s/hpa.yaml`

**Rolling Update Strategy**:
- `deploymentStrategy`: RollingUpdate
- `maxSurge`: 25% (1 pod at a time)
- `maxUnavailable`: 25%
- Health checks: livenessProbe (10s delay), readinessProbe (5s delay)

**Gradual Rollout**:
1. Deploy 10% of traffic (manual or service mesh)
2. Monitor for 5 minutes: metrics, alerts, error rates
3. Scale to 50% if healthy
4. Scale to 100% after validation

## Operational Excellence

**Observability Strategy**:

**Structured Logging** (JSON format):
```json
{
  "timestamp": "2025-02-12T10:30:00Z",
  "customer_id": "abc123",
  "conversation_id": "def456",
  "channel": "email",
  "event_type": "message_processed",
  "latency_ms": 2500,
  "escalated": false,
  "tool_calls_count": 3
}
```

**Metrics Collection**:
1. **Channel-level** (per channel):
   - `total_conversations` (COUNT)
   - `avg_latency_ms` (AVG)
   - `escalation_rate` (escalations/total)
   - `avg_sentiment` (AVG of sentiment_score)

2. **Agent-level**:
   - `tool_usage_frequency` (calls per conversation)
   - `knowledge_base_hit_rate` (searches with results / total searches)
   - `token_usage_per_conversation` (AVG)
   - `error_rate` (failed tool calls / total calls)

3. **System-level**:
   - Pod health (CPU, memory, restarts)
   - Kafka consumer lag (unprocessed messages)
   - PostgreSQL connection pool utilization
   - API error rate (4xx/5xx per minute)

4. **Business-level**:
   - Tickets resolved without human intervention
   - Cross-channel customer identification success rate
   - Customer satisfaction (sentiment trend)

**Alerting Thresholds**:
- Escalation rate > 25% → Alert (indicates agent struggling)
- P95 latency > 3 seconds for any channel → SLA breach
- Pod crash loop > 3 times in 10 minutes → Unhealthy deployment
- Kafka consumer lag > 100 messages → Processing backlog
- PostgreSQL connection pool > 80% utilization → Database bottleneck

**24/7 Readiness Validation**:

**Pre-Deployment Checklist**:
- [ ] All unit tests pass (pytest)
- [ ] All integration tests pass (multi-channel E2E)
- [ ] Load test passes (100+ concurrent users, Locust)
- [ ] Chaos test passes (random pod kills, 1 of 3 API + 1 of 3 worker)
- [ ] 24-hour test passes (100+ web, 50+ email, 50+ WhatsApp)
- [ ] Uptime > 99.9%, P95 latency < 3s, escalation < 25%, cross-channel ID > 95%

**24-Hour Test Plan**:
- Web Form Traffic: 100+ submissions over 24 hours (via Locust script)
- Email Simulation: 50+ Gmail messages processed (Gmail API test data)
- WhatsApp Simulation: 50+ WhatsApp messages processed (Twilio test data)
- Cross-Channel: 10+ customers contact via multiple channels
- Chaos Testing: Random pod kills every 2 hours
- Metrics Validation after 24 hours:
  - Uptime > 99.9%
  - P95 latency < 3 seconds (all channels)
  - Escalation rate < 25%
  - Cross-channel customer identification > 95%
  - No message loss (DLQ empty or reviewed)

**Graceful Degradation**:
- Gmail API down → Continue WhatsApp + Web Form, log errors, retry connections
- Twilio API down → Continue Email + Web Form, log errors, retry connections
- Kafka partition unavailable → Process other partitions, log warnings
- PostgreSQL replica fail → Promote remaining replica, no data loss
- Single API/worker pod fails → Kubernetes replaces, continue processing

## Security & Privacy

**Credential Management**:
- All secrets in Kubernetes Secrets (fte-secrets)
- Environment variables inject secrets: `OPENAI_API_KEY`, `POSTGRES_PASSWORD`, `GMAIL_CREDENTIALS`, `TWILIO_*`
- `.env` files in `.gitignore`, never committed
- Secret rotation: Update Kubernetes Secret, rolling restart pods

**Webhook Signature Validation**:
- **Gmail Pub/Sub**: Verify Pub/Sub signature (X-Goog-Signature)
- **Twilio WhatsApp**: `RequestValidator` with `TWILIO_AUTH_TOKEN`
- Reject 403 Forbidden if signature invalid (log security alert)

**Input Sanitization**:
- SQL injection: asyncpg parameterized queries (no string concatenation)
- XSS: FastAPI automatic HTML escaping in responses
- Email/Phone validation: Pydantic EmailStr, regex patterns
- Message length limits: Truncate/split before sending

**PII Protection**:
- No customer emails/phones in logs (use customer_id)
- Redact sensitive data: `john@example.com` → `j***@example.com`
- PostgreSQL encryption at rest (database-level encryption)
- HTTPS everywhere (TLS enforced)

**Audit Logging**:
- Log all inbound messages (customer_id, conversation_id, channel, event_type)
- Log all escalations (reason, full_context JSON)
- Log all failed operations (error type, retry count)
- Retention: Indefinite (MVP), ship to external log aggregation (Loki/ELK/CloudWatch)

## Testing Strategy

**Test Pyramid** (Constitution Principle V):

**1. Unit Tests** (pytest):
- Agent tools: search_knowledge_base, create_ticket, get_customer_history, escalate_to_human, send_response
- Channel handlers: Gmail (mock Pub/Sub), WhatsApp (mock Twilio), Web Form (validators)
- Database queries: Customer resolution, conversation lookup, message history
- Coverage: >80% target

**2. Integration Tests** (async pytest, testcontainers-postgres):
- Multi-channel E2E: Gmail → WhatsApp → Web (same customer)
- Cross-channel continuity: Email today, WhatsApp tomorrow, Web form next week
- Escalation triggers: Pricing, refund, profanity, angry customer
- Kafka messaging: Producer → Consumer → PostgreSQL
- Coverage: All critical paths

**3. Load Tests** (Locust):
- `WebFormUser`: 100+ users submitting forms (2-10s wait between)
- `HealthCheckUser`: Monitor /health during test
- Target: P95 latency < 3s at 100 concurrent users
- Duration: 10 minutes

**4. Chaos Tests** (Kubernetes):
- Random pod termination: `kubectl delete pod` (1 of 3 API, 1 of 3 worker)
- Channel failure simulation: Disable Gmail webhook, verify others continue
- Kafka partition failure: Stop 1 of 3 brokers
- Validation: No message loss, auto-recovery, metrics > 99.9% uptime

**Edge Cases Discovered During Incubation** (from hackathon_5.md):
1. Empty message → Helpful prompt "How can I help you today?"
2. Pricing question → Immediate escalation (NEVER answer pricing)
3. Refund request → Immediate escalation + empathy
4. Profanity/anger → Escalation or empathy + escalation
5. Knowledge base search fails → "I couldn't find information... Escalating to human"
6. Customer switches channels → Acknowledge previous interaction
7. Multiple customer identifiers → Link via customer_identifiers table
8. Rate limiting (10 msgs/min) → "Processing your messages... Please wait"
9. WhatsApp response too long → Truncate at 300 chars with "..." + "Reply for more"
10. Email response too long → Split into multiple emails

**Test Data Sets**:
- 20+ edge cases per channel (60+ total)
- Sample tickets: 50+ real-world scenarios (multi-channel)
- Knowledge base: 100+ articles covering setup, billing, API, troubleshooting
- Customer personas: Technical, non-technical, angry, happy, multi-channel

## Migration Strategy

**Phase 1: Incubation** (Hours 1-16):
- Use Claude Code interactively
- Build MCP server with tools
- Discover requirements
- Create `specs/discovery-log.md`
- Create `specs/customer-success-fte-spec.md`
- Prototype: `context/company-profile.md`, `context/product-docs.md`, `context/sample-tickets.json`, `context/escalation-rules.md`, `context/brand-voice.md`
- Output: Working prototype, MCP server, discovery log, crystallized spec, edge cases documented

**Phase 2: Specialization** (Hours 17-40):
1. **Extract Discoveries** (1 hour):
   - Document all requirements in `specs/transition-checklist.md`
   - Extract working prompts, tool descriptions, edge cases, response patterns, escalation rules, performance baseline

2. **Create Production Folder Structure** (1 hour):
   ```
   production/
   ├── agent/
   │   ├── __init__.py
   │   ├── customer_success_agent.py  # Agent definition
   │   ├── tools.py  # All @function_tool definitions
   │   ├── prompts.py  # System prompts
   │   └── formatters.py  # Channel-specific response formatting
   ├── channels/
   │   ├── __init__.py
   │   ├── gmail_handler.py
   │   ├── whatsapp_handler.py
   │   └── web_form_handler.py
   ├── workers/
   │   ├── __init__.py
   │   ├── message_processor.py  # Kafka consumer + agent runner
   │   └── metrics_collector.py  # Background metrics
   ├── api/
   │   ├── __init__.py
   │   └── main.py  # FastAPI application
   ├── database/
   │   ├── schema.sql  # PostgreSQL schema
   │   ├── migrations/
   │   └── queries.py  # Database access functions
   ├── tests/
   │   ├── test_agent.py
   │   ├── test_channels.py
   │   └── test_e2e.py
   ├── k8s/  # Kubernetes manifests
   ├── Dockerfile
   ├── docker-compose.yml  # Local development
   └── requirements.txt
   ```

3. **Transform MCP Tools → @function_tool** (1 hour):
   - MCP server tools → OpenAI Agents SDK with Pydantic validation
   - Add error handling (try/catch → fallback messages)
   - Add database connection pooling (asyncpg)
   - Vector search (pgvector) instead of string matching
   - Compare:
     - MCP: `search_kb(query: str) -> str` (loose typing)
     - OpenAI SDK: `search_kb(input: KnowledgeSearchInput) -> str` (strict typing, validation)

4. **Transform System Prompt** (30 minutes):
   - Conversational → Explicit constraints
   - "Help customers" → Channel awareness, escalation triggers, hard constraints
   - Add context variables: `{{customer_id}}`, `{{conversation_id}}`, `{{channel}}`, `{{ticket_subject}}`

5. **Create Transition Test Suite** (1 hour):
   - `tests/test_transition.py`: Verify agent behavior matches incubation
   - Tests: Empty message, pricing escalation, angry customer, channel response length, tool execution order

**Phase 3: Production Deployment** (Hours 41-48+):
1. **Database Setup** (2-3 hours):
   - Deploy PostgreSQL 16 + pgvector extension
   - Run schema.sql migrations
   - Seed knowledge base (100+ articles with embeddings)

2. **Kafka Setup** (1-2 hours):
   - Confluent Cloud (free tier) or self-hosted
   - Create topics: fte.tickets.incoming, fte.escalations, fte.metrics, fte.dlq
   - Test producer/consumer with test messages

3. **Channel Handlers** (4-5 hours):
   - Gmail: OAuth2 service account, Pub/Sub push
   - WhatsApp: Twilio account, Sandbox testing
   - Web Form: React/Next.js component

4. **Kubernetes Deployment** (3-4 hours):
   - Build Docker images: `docker build -t your-registry/fte .`
   - Deploy to minikube (local) first
   - Validate health checks, HPA configuration
   - Run chaos tests (pod kills)

5. **24-Hour Test** (Hours 41-48):
   - Deploy to cloud Kubernetes cluster
   - Run Locust load test (100+ concurrent users)
   - Run 24-hour continuous test with chaos
   - Validate all metrics: uptime > 99.9%, P95 < 3s, escalation < 25%, cross-channel ID > 95%
   - Documentation: deployment guide, runbook, API docs

## Constitution Check

**Principle I: Multi-Channel Customer-Centric Design** ✅
- All 3 channels (Gmail, WhatsApp, Web Form) supported equally
- Channel-appropriate responses enforced via `formatters.py`
- Response length limits: Email ≤ 500 words, WhatsApp ≤ 300 chars, Web ≤ 300 words
- Cross-channel customer identification > 95% accuracy

**Principle II: Agent Maturity Model** ✅
- Incubation Phase: Claude Code + MCP server (Hours 1-16)
- Specialization Phase: OpenAI SDK + PostgreSQL + Kafka + K8s (Hours 17-40)
- Production Deployment Phase: 24-hour test + gradual rollout (Hours 41-48+)
- Transition artifacts: discovery-log.md, customer-success-fte-spec.md, transition-checklist.md, test_transition.py

**Principle III: 24/7 Operational Excellence** ✅
- Pod restarts: State in PostgreSQL, conversations resume
- Horizontal scaling: 3-20 API pods, 3-30 worker pods (Kubernetes HPA)
- Dead letter queue: fte.dlq topic for failed messages
- Health checks: /health endpoint returns all channel status
- P95 latency < 3s, uptime > 99.9%
- Graceful degradation: Single channel failure → others continue

**Principle IV: Cross-Channel Conversation Continuity** ✅
- Customer identification: customer_identifiers table (email/phone → customer_id)
- Last 20 messages: get_customer_history tool retrieves all channels
- Agent acknowledgment: "I see you contacted us about X last week via email..."
- Channel switches logged: conversations table tracks initial_channel, metadata.channel_switches

**Principle V: Test-Driven Reliability** ✅
- Red-Green-Refactor enforced
- Integration tests written first (E2E multi-channel, escalation triggers)
- Edge cases from incubation have tests (20+ per channel)
- Load tests pass (100+ concurrent users)
- Chaos tests pass (random pod kills)

**Principle VI: Data Privacy & Security** ✅
- Secrets: Kubernetes Secrets (fte-secrets), never in code/repo
- Webhook validation: Gmail Pub/Sub signature, Twilio RequestValidator
- Input sanitization: Pydantic validation, asyncpg parameterized queries
- PII redaction: Logs use customer_id, not email/phone
- PostgreSQL encryption at rest

**Principle VII: Observability & Metrics** ✅
- Structured JSON logs: timestamp, customer_id (redacted), conversation_id, channel, event_type
- Metrics by level: Channel (response count, latency, escalation, sentiment), Agent (tool usage, KB hit rate, token usage, error rate), System (pod health, Kafka lag, connection pool, API errors), Business (tickets resolved, cross-channel ID rate)
- Alerts: Escalation > 25%, P95 > 3s, pod crash loop > 3 in 10 min, Kafka lag > 100

## Next Steps

**Immediate Actions**:
1. Run `/sp.tasks` to generate testable tasks from this plan
2. Begin Phase 1 (Incubation) with `/sp.implement`
3. Create `context/` folder with company profile, product docs, sample tickets
4. Use Claude Code interactively to build MCP server prototype

**Decision Log**:
- Technology choices justified (PostgreSQL + pgvector vs external CRM, Kafka vs alternatives)
- Architecture patterns documented (event streaming, worker pools, horizontal scaling)
- Tradeoffs documented (synchronous vs async, complexity vs reliability)
- Constitutional compliance verified for all 7 principles

**Risks & Mitigations**:
- Risk: Kafka complexity → Mitigation: Confluent Cloud for simplicity
- Risk: pgvector learning curve → Mitigation: Use MCP during incubation
- Risk: Webhook spoofing → Mitigation: Signature validation mandatory
- Risk: Pod restart data loss → Mitigation: State in PostgreSQL, not in-memory

**Success Criteria Tracking**:
- [ ] >95% cross-channel customer identification (measured in integration tests)
- [ ] <25% escalation rate (monitored via metrics)
- [ ] P95 latency < 3s (measured in load tests)
- [ ] >99.9% uptime (measured in 24-hour test)
- [ ] <$1,000/year operating cost (calculated after cloud deployment)
