# Research: Customer Success Digital FTE

**Created**: 2025-02-12
**Purpose**: Document technology decisions, alternatives considered, and rationale for architectural choices

---

## Decision 1: Database & CRM Platform

### Selected: PostgreSQL 16 with pgvector Extension

**Decision**: Use PostgreSQL as the CRM and data store (NOT external CRM like Salesforce/HubSpot)

**Rationale**:
- **Single Source of Truth**: PostgreSQL serves as the complete CRM system - customers, conversations, tickets, messages, knowledge base all in one place
- **Vector Similarity Search**: pgvector extension enables semantic search of knowledge base articles using OpenAI embeddings (text-embedding-3-small model, 1536 dimensions)
- **Cross-Channel Unification**: Customer data (email, phone) links across all channels in one customers table
- **Relationships**: Foreign key constraints ensure data integrity (conversations → messages → tickets)
- **Open Source**: PostgreSQL and pgvector are open-source, mature, well-documented
- **Cost Efficiency**: Single database to manage vs multiple integrations + CRM subscription costs

**Tradeoffs**:
- **No Salesforce/HubSpot Features**: Out-of-the-box contact syncing, lead scoring, email automation
  **Manual Implementation**: Must build all CRM features from scratch (customer management, ticket lifecycle, etc.)
- **Query Complexity**: Requires writing SQL vs using pre-built ORM methods and APIs
- **Scaling**: Must handle database scaling and connection pooling manually

**Alternatives Considered**:
- **Salesforce**: Full-featured CRM, extensive documentation, but adds significant cost and complexity
- **HubSpot**: Strong CRM, but adds operational overhead and learning curve
- **Redis**: Fast in-memory caching, but insufficient durability (data loss on restart) and lacks relational features
- **Custom CRM (JSON files)**: Simple to start, but lacks query capabilities, joins, and scalability

**MCP Context7 Research**:
- Selected `/pgvector/pgvector` library (Benchmark: 91.4) - Open-source PostgreSQL vector similarity search
- Confirmed vector operations: `<#>` (inner product), `<=>` (cosine distance), `<~>` (L1 distance) for semantic search
- HNSW indexing for fast approximate nearest neighbor search on high-dimensional vectors

**Conclusion**: PostgreSQL with pgvector provides the best balance of relational data integrity, vector search capabilities, open-source maturity, and operational simplicity for this hackathon scope.

---

## Decision 2: Event Streaming Platform

### Selected: Apache Kafka (Confluent Cloud acceptable)

**Decision**: Use Apache Kafka for event streaming between API Gateway, Message Processing Layer, and Channel Response Layer

**Rationale**:
- **Durable Event Streaming**: Kafka's distributed commit log provides exactly-once semantics, critical for multi-channel coordination
- **Consumer Groups**: fte-message-processor group enables horizontal scaling (3+ worker pods) with position tracking
- **Partitioning Strategy**: Future ability to partition by channel (fte.channels.email.inbound, fte.channels.whatsapp.inbound, fte.channels.web.inbound) for targeted scaling
- **Dead Letter Queue**: fte.dlq topic captures failed messages for human review and recovery
- **Ecosystem Maturity**: Largest open-source streaming platform with extensive community support and tooling

**Tradeoffs**:
- **Operational Overhead**: More complex than Redis (requires Zookeeper or Confluent Cloud management)
- **Learning Curve**: Kafka concepts (producers, consumers, topics, partitions, offsets) more complex than Redis pub/sub
- **Confluent Cloud Cost**: Adds operational expense vs self-hosted Kafka cluster (acceptable tradeoff for simplicity)

**Alternatives Considered**:
- **Redis Pub/Sub**: Simple publish/subscribe, but lacks durability (no message persistence if consumer crashes before persisting), limited horizontal scaling
- **RabbitMQ**: Mature messaging broker with management UI, but adds operational complexity (Erlang nodes, clustering)
- **Redis Streams**: Lightweight data structure store, but lacks Kafka's durability and transactional guarantees
- **Google Cloud Pub/Sub**: Fully managed, but could introduce vendor lock-in

**MCP Context7 Research**:
- Selected `/confluentinc/confluent-kafka-python` library (Benchmark: 68.8) - Official Python client
- Confirmed producer patterns: AIOKafkaProducer with `enable_idempotence=true`
- Confirmed consumer patterns: AIOKafkaConsumer with `enable.auto_commit=false` (consumer controls offset commits)
- Transactional semantics: Producer.beginTransaction() → produce → sendOffsetsToTransaction → commitTransaction()
- Exactly-once processing: Combine Kafka producer and consumer in same transaction for complex workflows

**Implementation Patterns**:
```python
# Producer with idempotence
producer = AIOKafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    enable_idempotence=True,
    transactional_id="processor-1"
)

# Consumer with explicit commits
consumer = AIOKafkaConsumer(
    topics=[TOPICS['tickets.incoming']],
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    group_id="fte-message-processor",
    enable_auto_commit=False  # Consumer commits offsets after processing
)
)
```

**Conclusion**: Apache Kafka provides the reliability, scalability, and transactional guarantees required for a production 24/7 Digital FTE. Confluent Cloud acceptable for simplicity (eliminates Zookeeper management).

---

## Decision 3: Container Orchestration

### Selected: Kubernetes

**Decision**: Use Kubernetes for container orchestration (NOT Docker Compose or Docker Swarm)

**Rationale**:
- **Horizontal Pod Autoscaler**: HPA (Horizontal Pod Autoscaler) automatically scales fte-api (3-20) and fte-worker (3-30) based on CPU 70% target
- **Self-Healing**: Liveness and readiness probes detect unhealthy pods, Kubernetes restarts them automatically
- **Rolling Updates**: RollingUpdate strategy with maxSurge=25%, maxUnavailable=25% ensures zero-downtime deployments
- **Service Discovery**: Kubernetes Service abstraction enables LoadBalancer and Ingress for external access
- **Production-Grade**: Battle-tested orchestration platform with extensive documentation and community support

**Tradeoffs**:
- **Operational Complexity**: More complex than Docker Compose (requires learning YAML manifests, pod specs, services)
- **Resource Overhead**: Requires more infrastructure (cluster) than single-machine Docker deployment
- **Setup Time**: Kubernetes takes longer to learn than Docker Compose Swarm

**Alternatives Considered**:
- **Docker Compose**: Declarative syntax (`docker-compose.yml`), easy local development, but lacks built-in auto-scaling and self-healing
- **Docker Swarm**: Simpler than Kubernetes, but less mature ecosystem, fewer tools, deprecated in favor of Kubernetes
- **Nomad**: Orchestration tool that manages containers across multiple hosts, but adds operational layer and cost

**MCP Context7 Research**:
- Selected `/kubernetes-client/python` (Benchmark: 74.4) - Official Python client library
- Confirmed deployment patterns: `apps/v1` API for creating Deployments from YAML files or Python dicts
- Confirmed HPA patterns: `autoscaling/v2` API for Horizontal Pod Autoscaler configuration
- Confirmed rollout strategies: RollingUpdate with maxSurge and maxUnavailable settings

**Implementation Pattern**:
```python
from kubernetes import client, config

# Load kube config
config.load_kube_config()

# Create apps/v1 API client
api = client.AppsV1Api()

# Create HPA
api.create_namespaced_deployment(
    body={
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'fte-api',
            'labels': {'app': 'customer-success-fte'}
        },
        'spec': {
            'replicas': 3,
            'selector': {
                'matchLabels': {
                    'app': 'customer-success-fte',
                    'component': 'api'
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': 'customer-success-fte',
                        'component': 'api'
                    }
                },
                'spec': {
                    'containers': [{
                        'name': 'fte-api',
                        'image': 'your-registry/fte:latest',
                        'command': ['uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', '8000']
                    }],
                    'ports': [
                        {'containerPort': 8000, 'hostIp': '0.0.0.0'}
                    ]
                }
            }
        }
    }
)

# Create HPA
api.create_namespaced_horizontal_pod_autoscaler(
    name='fte-api-hpa',
    spec={
        'scaleTargetRef': {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'name': 'fte-api'
        },
        'minReplicas': 3,
        'maxReplicas': 20,
        'metrics': {
            'type': 'Resource',
            'resource': {
                'name': 'cpu',
                'target': {
                    'type': 'Utilization',
                    'averageUtilization': 70
                }
            }
        }
    }
)
)
```

**Conclusion**: Kubernetes is the industry-standard for production container orchestration. While Docker Compose is simpler for local development, Kubernetes provides the auto-scaling, self-healing, and production-ready features required for 24/7 operation.

---

## Decision 4: Database Driver

### Selected: asyncpg

**Decision**: Use asyncpg for PostgreSQL async operations (NOT psycopg2, not asyncpg)

**Rationale**:
- **Async/Await Native**: asyncpg is built specifically for Python's async/await syntax (PEP 492)
- **Connection Pooling**: Built-in connection pool management (min_size=5, max_size=20) with automatic acquisition/release
- **Performance**: Non-blocking database operations prevent event loop blocking, critical for 100+ concurrent users
- **Active Development**: Actively maintained, updated in 2024, aligns with Python 3.10+ async patterns

**Tradeoffs**:
- **Learning Curve**: asyncpg has smaller community than asyncpg (less documentation, fewer examples)
- **Psycopg2 Maturity**: psycopg2 is extremely mature, well-documented, widely used
- **Synchronous Alternative**: Could use psycopg3 (async wrapper around sync driver), but adds complexity

**Alternatives Considered**:
- **asyncpg**: Next-generation asyncpg, but still maturing, breaking changes between versions
- **psycopg2**: Synchronous driver with excellent performance and documentation, but blocking I/O hurts scalability
- **SQLAlchemy**: Popular ORM, but adds abstraction layer and learning curve for team

**MCP Context7 Research**:
- Selected `/websites/magicstack_github_io_asyncpg_current` (Benchmark: 70.9) - PostgreSQL interface library
- Confirmed connection pool pattern: `asyncpg.create_pool()` with min/max size and automatic connection management
- Confirmed best practice: Use asyncpg directly with `pool.acquire()` context managers for transaction management

**Implementation Pattern**:
```python
import asyncpg

# Create pool
pool = asyncpg.create_pool(
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    min_size=5,  # Minimum connections
    max_size=20  # Maximum connections
    command_timeout=60
)

# Usage in agent tools
@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Generate embedding
        embedding = await generate_embedding(input.query)

        # Query with vector similarity
        results = await conn.fetch(
            """
            SELECT title, content, 1 - (embedding <=> $1::vector) as similarity
            FROM knowledge_base
            WHERE $2::text IS NULL OR category = $3
            ORDER BY embedding <=> $1::vector
            LIMIT $4
            """,
            embedding,
            input.category,
            input.max_results
        )

        # Format results
        formatted = []
        for r in results:
            formatted.append(f"**{r['title']}** (relevance: {r['similarity']:.2f})\n{r['content'][:500]}...\n")

        return "\n---\n".join(formatted)
```

**Conclusion**: asyncpg provides the best combination of async-native performance, connection pooling, and maturity for high-concurrency web applications. The non-blocking I/O is critical for handling 100+ concurrent users in the message processing layer.

---

## Decision 5: Web Framework

### Selected: FastAPI for Backend + React/Next.js for Web Form

**Decision**: Use FastAPI (backend API Gateway) and React/Next.js (web form component)

**Rationale**:
- **FastAPI**: Modern async web framework with automatic OpenAPI documentation, built-in Pydantic validation, WebSocket support for future enhancements
- **React/Next.js**: Industry-standard React framework for building standalone, embeddable web components
- **Type Safety**: Pydantic v2 with strict validation prevents runtime errors at the boundary (FastAPI auto-validates requests)
- **Performance**: 30% faster than Flask (async/await), critical for P95 < 3s SLA
- **Developer Experience**: Automatic API docs at `/docs` endpoint helps frontend integration

**Tradeoffs**:
- **Framework Complexity**: Learning two frameworks (FastAPI + React) vs Django templates + Jinja2
- **State Management**: FastAPI has simpler state management than React's useState for complex interactions
- **Build Tooling**: Requires Next.js build step for React component (minor overhead)

**Alternatives Considered**:
- **Django**: Full-featured framework with built-in ORM, admin panels, but slower performance and heavier resource usage
- **Flask**: Simpler than Django, but requires more manual setup for WebSocket, API docs
- **Vue.js**: Alternative to React, but team chose React for larger ecosystem and Next.js momentum

**MCP Context7 Research**:
- Selected `/websites/fastapi_tiangolo` (Benchmark: 91.4) - FastAPI web framework
- Confirmed background tasks pattern: BackgroundTasks for async webhook processing
- Confirmed CORS middleware pattern: CORSMiddleware for cross-origin resource sharing (web form embedding)

**Implementation**:
```python
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

app = FastAPI()

# CORS for web form
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    # Process Gmail webhook asynchronously
    message = await request.json()
    await process_in_background(message, background_tasks)

@app.post("/support/submit")
async def submit_support_form(submission: SupportFormSubmission):
    # Validate and create ticket
    ticket_id = await create_ticket(submission)

    # Publish to Kafka in background
    await publish_to_kafka("fte.tickets.incoming", message)

    return {"ticket_id": ticket_id, "message": "Thank you..."}
```

---

## Decision 6: Gmail Integration

### Selected: Gmail API with Pub/Sub Push Notifications

**Decision**: Use Gmail API with Pub/Sub push notifications (NOT polling)

**Rationale**:
- **Real-Time Updates**: Pub/Sub push notifications trigger immediate processing when new email arrives (vs polling every X minutes)
- **Efficiency**: Push-based architecture scales better than polling for email volume
- **Standard Pattern**: Google-recommended pattern for Gmail API integration
- **OAuth2**: Service account authentication (not individual user credentials) for security

**Tradeoffs**:
- **Polling Complexity**: Requires scheduling logic, incremental sync, handling failures, rate limiting
- **Latency**: Poll-based approach has inherent delay (polling interval vs immediate push)
- **API Quotas**: Gmail API has usage quotas that are easier to hit with frequent polling

**Alternatives Considered**:
- **IMAP/POP3**: Standard email access, but Gmail API provides more features (thread management)
- **Microsoft Graph API**: Alternative email integration, but team chose Gmail for brand consistency

**MCP Context7 Research**:
- No direct Gmail API documentation in MCP Context7, but Confirmed Google Cloud Pub/Sub standard pattern
- Pub/Sub push: Gmail sends POST request to webhook endpoint when new message matches filter (INBOX label, from:sender)
- Requires: User installs app / authorizes service account with Gmail API scopes

---

## Decision 7: WhatsApp Integration

### Selected: Twilio WhatsApp API (Sandbox for development)

**Decision**: Use Twilio API for WhatsApp integration

**Rationale**:
- **Official WhatsApp Business API**: Requires approval (Facebook), Twilio provides approved access
- **Sandbox**: Free testing environment (send WhatsApp messages to Twilio sandbox number)
- **Mature Platform**: Extensive documentation, proven reliability, multi-channel support (WhatsApp, SMS, Voice)
- **Request Validation**: `RequestValidator` with TWILIO_AUTH_TOKEN prevents webhook spoofing (CRITICAL for security)

**Tradeoffs**:
- **Cost**: Twilio charges per message (minimal for testing, but adds operational cost at scale)
- **Sandbox Limits**: Sandbox number can only send/receive from approved numbers
- **Direct WhatsApp API**: Not available without Facebook partnership

**Alternatives**:
- **MessageBird**: Alternative WhatsApp API, but Twilio is more mature
- **Azure Communication Services**: Microsoft's answer to Twilio, but team chose Twilio for ecosystem familiarity

**MCP Context7 Research**:
- Confirmed Twilio documentation patterns for webhook signature validation
- Sandbox testing sufficient for hackathon (no production WhatsApp Business account needed)

---

## Technology Stack Summary

| Component | Technology | Justification |
|-----------|-----------|--------------|
| **Backend** | FastAPI | Async web framework, auto OpenAPI docs |
| **Database** | PostgreSQL 16 + pgvector | CRM + vector search |
| **Streaming** | Apache Kafka | Event streaming with durability |
| **Orchestration** | Kubernetes | Production-grade orchestration |
| **Language** | Python 3.11+ | Async/await native |
| **Email** | Gmail API + Pub/Sub | Push notifications |
| **Messaging** | Twilio WhatsApp | Sandbox testing |
| **Web Form** | React/Next.js | Standalone component |

---

## Architecture Patterns

**1. Event-Driven Architecture**
- Channels publish events to `fte.tickets.incoming` topic
- Message processors consume events, run OpenAI Agent, publish responses
- Decouples channels from processing logic (webhook handlers just publish to Kafka)

**2. Repository Pattern**
- Data layer (PostgreSQL) as single source of truth
- Channel handlers are stateless (conversation state in database)
- Enables horizontal scaling (any pod can process any message)

**3. Circuit Breaker Pattern**
- When Gmail API fails → Continue WhatsApp + Web Form (graceful degradation)
- When Twilio fails → Continue Gmail + Web Form
- When both fail → Return service unavailable (503 errors)
- DLQ captures failures for human review and recovery

**4. Idempotent Producer**
- `enable.idempotence=True` enables Kafka producer to guarantee message delivery
- Exactly-once semantics: Transaction spans producer + consumer for complex workflows

---

## Performance Baselines

**Targets (from Constitution)**:
- **P95 Latency**: < 3 seconds (processing time from agent receives message to Kafka to response sent)
- **Throughput**: 100+ concurrent users (tested via Locust)
- **Escalation Rate**: <25% of conversations (pricing, refunds, legal, angry, search failures)
- **Cross-Channel ID**: >95% (email/phone → unified customer_id)

**Implementation Strategy**:
- Connection pooling (asyncpg min=5, max=20) prevents connection bottlenecks
- Kafka async I/O prevents event loop blocking
- Vector similarity search (pgvector HNSW index) optimized for < 50ms queries
- Horizontal scaling (Kubernetes HPA based on 70% CPU target)

---

## Security Considerations

**1. Webhook Signature Validation**
- **Gmail Pub/Sub**: Verify X-Goog-Signature header to prevent spoofing
- **Twilio**: `RequestValidator` with TWILIO_AUTH_TOKEN to validate X-Twilio-Signature
- **Attack Vector**: Prevents replay attacks, credential theft, SQL injection

**2. Input Sanitization**
- **Pydantic Strict**: EmailStr, strict length validation on form fields
- **asyncpg Parameterized**: All database queries use placeholders ($1, $2, etc.) prevents SQL injection
- **Message Length Limits**: Enforce at channel level (email ≤500 words, WhatsApp ≤ 300 chars)

**3. Data Protection**
- **PII Redaction**: Logs use customer_id (not email/phone) to protect privacy
- **Encryption at Rest**: PostgreSQL transparent data encryption (TDE) for data at rest
- **HTTPS Everywhere**: TLS enforced for all external communications

**4. Credential Management**
- **Kubernetes Secrets**: All API keys in `fte-secrets` (type: Opaque), never in code/repo
- **Environment Variables**: Injected from secrets into pods, never logged

---

## Operational Excellence

**24/7 Validation Strategy**:

1. **Pod Restart Testing**
   - Kill API pod → Verify: Remaining 2 pods handle traffic
   - Kill worker pod → Messages re-consumed from Kafka, no data loss
   - Kill all pods → PostgreSQL connection pool drains, gracefully restarts

2. **Chaos Testing**
   - Random pod termination (kubectl delete pod)
   - Channel failure simulation (disable Gmail webhook)
   - Partition failure (stop 1 of 3 Kafka brokers)
   - Validate: Auto-recovery, message ordering preserved

3. **Load Testing**
   - Locust: 100 users submitting forms (2-10s wait between)
   - Monitor: CPU, memory, latency < 3s P95
   - Scale up: Does HPA trigger? (3 → 20 pods)

4. **24-Hour Test**
   - 100 web submissions, 50 emails, 50 WhatsApp over 24 hours
   - Validate: Uptime > 99.9%, P95 latency < 3s, escalation < 25%
   - No message loss (DLQ empty, all Kafka messages processed)

**Success Criteria**:
- ✅ Pod restart survival (state in PostgreSQL)
- ✅ Horizontal scaling (3 → 20 pods under load)
- ✅ Graceful degradation (1 channel fails → others continue)
- ✅ Chaos tolerance (random pod kills)
- ✅ Metrics validation (all thresholds monitored)

---

## Open Questions & Risks

**Unresolved**:
- None - All technology decisions justified with tradeoffs documented

**Risks**:
- **Risk: Kafka Operational Complexity** - Confluent Cloud recommended for simplicity, but adds operational cost
  - **Mitigation**: Self-hosted Kafka acceptable for hackathon (minikube local, cloud for production)
- **Risk: asyncpg Maturity** - Smaller ecosystem than psycopg2, but async-native performance critical
  - **Mitigation**: MCP Context7 provided best practices for connection pooling and transaction management

**Next Research**:
- pgvector embedding generation (OpenAI text-embedding-3-small model, 1536 dimensions)
- Gmail API OAuth2 flow (service account setup)
- Twilio WhatsApp Business API upgrade path (sandbox → production)

---

## Migration Path: Incubation → Specialization

**Phase 1: Incubation (Hours 1-16)**: Use MCP prototype with Claude Code
- **Discovery**: This research.md documents technology decisions before Specialization
- **Output**: Working prototype (MCP server), discovery-log.md, crystallized spec.md

**Phase 2: Specialization (Hours 17-40): Transform to OpenAI SDK + PostgreSQL + Kafka
1. Extract discoveries from discovery-log.md
2. Transform MCP tools → @function_tool with Pydantic
3. Add error handling (try/catch → fallback)
4. Add database pooling (asyncpg instead of in-memory dicts)
5. Add Kafka producer/consumer with transactional semantics

**Phase 3: Production Deployment (Hours 41-48+)**:
- Database schema migrations
- Kafka topic creation (9 topics total)
- Channel handlers (Gmail, WhatsApp, Web Form)
- Kubernetes manifests (namespace, deployments, services, ingress, HPAs)
- 24-hour validation test

---

## References

- [Constitution](.specify/memory/constitution.md) - All 7 principles
- [Specification](spec.md) - Functional requirements, user stories, success criteria
- [Hackathon 5 Guide](hackathon_5.md) - Original problem statement
- MCP Context7: /apache/kafka, /kubernetes-client/python, /websites/fastapi_tiangolo
