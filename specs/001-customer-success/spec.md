## Context & Overview

**Purpose**: Build a 24/7 AI-powered Digital Full-Time Employee (FTE) that handles customer support inquiries across three communication channels (Gmail, WhatsApp, Web Form) with unified customer context, intelligent escalation, and operational excellence.

**Business Value**: Replace a $75,000/year human Customer Success Representative with a $1,000/year Digital FTE that operates continuously, scales horizontally, and provides consistent multi-channel support without breaks, sick days, or vacations.

**Success Definition**: Digital FTE operates 24/7, survives pod restarts and random failures, identifies customers across channels (>95%), maintains conversation continuity, escalates appropriately (<25% escalation rate), and responds within SLA (P95 < 3 seconds).

**Scope Boundaries**:
- **In Scope**: Multi-channel support (Gmail, WhatsApp, Web Form), PostgreSQL as CRM (no external CRM), cross-channel conversation continuity, 24/7 operation, escalation logic, observability
- **Out of Scope**: Full website (only web support form component), production WhatsApp Business account (Twilio Sandbox sufficient), external CRM integration, billing/payment processing

## User Scenarios & Testing

### User Story 1 - Multi-Channel Inquiry (Priority: P1)

A customer needs help with a product issue and reaches out via their preferred channel (email, WhatsApp, or web form). The Digital FTE responds appropriately for that channel (formal/detailed for email, concise/conversational for WhatsApp, semi-formal for web), recognizes the customer if they've contacted before via any channel, retrieves their conversation history, and provides helpful assistance or escalates when necessary.

**Why this priority**: This is the core value proposition - customers receive instant, accurate, channel-appropriate support 24/7 without waiting for human availability. Cross-channel continuity eliminates frustration of repeating information.

**Independent Test**: Can be fully tested by sending inquiries through each channel (email test message, WhatsApp test message, web form submission) and verifying:
1. Response received within SLA
2. Response format matches channel expectations
3. Customer correctly identified across channels (same email/phone)
4. Previous conversation history acknowledged in response
5. Simple questions answered accurately
6. Complex/policy questions escalated appropriately

**Acceptance Scenarios**:

1. **Given** a new customer (never contacted before), **When** they send "Hello, I need help with product setup" via email, WhatsApp, or web form, **Then** system creates new customer record, sends channel-appropriate greeting and setup guidance
2. **Given** a returning customer who emailed about pricing last week, **When** they message via WhatsApp "I'm ready to purchase", **Then** system identifies customer via phone number, retrieves last 20 messages across all channels, responds "I see you contacted us about pricing last week via email. I can help you complete your purchase now"
3. **Given** an angry customer uses profanity in web form message "This is bulls**t! Refund my money now!", **When** Digital FTE processes message, **Then** system detects sentiment (profanity, urgency keywords like "refund now"), triggers immediate escalation to human, acknowledges frustration "I understand you're upset. A human representative will contact you within 1 hour"
4. **Given** a customer asks a simple FAQ question "How do I reset my password?", **When** message arrives via any channel, **Then** Digital FTE searches knowledge base, finds answer, responds with channel-appropriate format (detailed step-by-step for email, brief link for WhatsApp, formatted instructions for web)
5. **Given** a customer asks pricing question "How much does Enterprise plan cost?", **When** Digital FTE processes, **Then** system recognizes pricing query (escalation trigger), responds "I'd be happy to discuss Enterprise pricing. Let me connect you with our sales team" and escalates

---

### User Story 2 - Cross-Channel Conversation Continuity (Priority: P1)

A customer starts a conversation via one channel (e.g., sends email about API authentication), continues via another channel (e.g., follows up on WhatsApp 2 days later), and potentially uses a third channel (e.g., submits web form with additional details a week later). The Digital FTE maintains complete context across all channels, never asking the customer to repeat information.

**Why this priority**: The #1 customer frustration with automated support is repeating themselves. Cross-channel continuity demonstrates true Digital FTE capability and provides disproportionate business value through superior customer experience.

**Independent Test**: Can be fully tested by:
1. Customer A sends email about topic X, records ticket/conversation IDs
2. Customer A follows up via WhatsApp 2 days later about same topic
3. Customer A submits web form 1 week later with related detail
4. System verifies all interactions linked to single customer_id
5. Last 20 messages from all channels retrieved in each response
6. Agent acknowledges "I see you mentioned X in your email 2 days ago" in WhatsApp response

**Acceptance Scenarios**:

1. **Given** customer emailed "API authentication failing with 401 error" 3 days ago, **When** they message via WhatsApp "Still having API issues", **Then** system identifies via phone number linked to email, retrieves conversation history, responds "I see you emailed about 401 errors 3 days ago. Are you still experiencing the same authentication issue?"
2. **Given** customer submitted web form about billing question yesterday, **When** they email from same address with more details, **Then** system recognizes email address, links to existing conversation, responds in email with channel-appropriate formal format "I received your web form submission yesterday about billing. Thank you for providing additional details via email. I can now help you with..."
3. **Given** customer has 15 interactions across channels over 2 weeks, **When** new message arrives, **Then** system retrieves last 20 messages (all channels combined), provides contextually aware response
4. **Given** customer uses email address john@example.com and phone +1-555-0100, **When** they contact via WhatsApp (phone) then email (address), **Then** system correctly links both identifiers to single customer record
5. **Given** customer switches channels mid-conversation (email → WhatsApp within 1 hour), **When** WhatsApp message arrives, **Then** system immediately shows conversation history from email 30 minutes ago

---

### User Story 3 - 24/7 Operational Resilience (Priority: P1)

The Digital FTE operates continuously through infrastructure disruptions: application pods restart randomly, one of three API pods fails, Kafka queues build up during high load, or a single channel (e.g., Gmail API) goes down. Customers experience no interruption in service, and the system heals automatically without human intervention.

**Why this priority**: 24/7 operation is the core value proposition vs human FTEs (40 hours/week with breaks). Operational resilience distinguishes a prototype from a production Digital FTE. Customers don't care about infrastructure - they care their questions are answered at 3 AM on Sunday.

**Independent Test**: Can be fully tested by:
1. Deploying 3 API pods and 3 worker pods in Kubernetes
2. Simulating pod kills (randomly terminate 1 of 3 API pods, verify 2 remaining pods handle traffic)
3. Simulating channel failure (disable Gmail webhook, verify WhatsApp and web form continue operating)
4. Load testing (100+ concurrent users via Locust)
5. Verifying no message loss (all Kafka messages processed)
6. Measuring uptime > 99.9% and P95 latency < 3 seconds throughout test

**Acceptance Scenarios**:

1. **Given** 3 API pods and 3 worker pods running normally, **When** 1 API pod is randomly terminated, **Then** remaining 2 API pods continue handling requests, Kubernetes schedules replacement pod, no customer-facing interruption
2. **Given** normal operation with all 3 channels active, **When** Gmail API webhook starts failing (503 errors), **Then** Digital FTE continues processing WhatsApp and web form messages, logs Gmail errors, retries Gmail connections, auto-recovers when Gmail API returns
3. **Given** sudden load spike (50 simultaneous web form submissions), **When** Kafka queues messages for processing, **Then** no messages lost, all submissions processed within SLA, consumer pods auto-scale to handle load
4. **Given** worker pod crash during message processing, **When** pod restarts, **Then** unprocessed messages re-consumed from Kafka, conversation state preserved in PostgreSQL, customer experiences no interruption
5. **Given** 24-hour continuous operation test with 100+ web submissions, 50+ emails, 50+ WhatsApp messages, **When** test completes, **Then** uptime > 99.9%, P95 latency < 3s, escalation rate < 25%, cross-channel ID > 95%, zero message loss confirmed

---

### Edge Cases

**Boundary Conditions**:
- What happens when customer provides invalid email format in web form? → Validation error returned, "Please enter valid email address"
- What happens when WhatsApp message exceeds 300 character response limit? → Response truncated at 300 chars with "..." and "Reply for more details"
- What happens when customer email exceeds 500 word response limit? → Response split into multiple emails if needed, or summarized with "Full details available at [link]"
- What happens when customer sends 10 messages within 1 minute (potential spam/flood)? → Rate limiting applied, "I'm processing your messages. Please wait for my response before sending more."
- What happens when knowledge base search returns no results? → Digital FTE acknowledges, "I couldn't find information about that. Let me escalate to our team" and escalates
- What happens when customer uses email address in web form but phone number in WhatsApp, and they're not linked? → System creates two customer records initially, later merges if customer confirms identity links both identifiers

**Error Scenarios**:
- How does system handle Gmail API 503 errors? → Retry with exponential backoff (3 attempts), queue message for retry, escalate to human if all retries fail
- How does system handle Twilio webhook signature validation failure? → Reject webhook request with 403 Forbidden, log security alert
- How does system handle PostgreSQL connection failure? → Retry connection, health check fails, Kubernetes restarts pod, no new messages processed until connection restored
- How does system handle Kafka publish timeout? → Store message in database with "pending" status, background job retries publishing
- How does system handle customer sending "I want to speak to human" explicitly? → Immediate escalation, "Connecting you with our team now"
- How does system handle empty web form submission (all fields blank)? → Validation error, "Please fill in all required fields"

**Ambiguity Resolution**:
- Customer uses different names in different channels (John Smith vs J. Smith) → System links by email/phone, stores all names, uses most recent or asks for clarification if conflicting
- Customer asks question in different language (not English) → System detects language, attempts to respond in same language if supported, escalates if not
- Multiple customers share same email address (e.g., support@company.com used by multiple people) → System treats as single customer initially, can create separate records if human agent determines they're different

## Requirements

### Functional Requirements

**Customer Identification & Cross-Channel Continuity**:
- **FR-001**: System MUST identify customers by email address (email, web form) or phone number (WhatsApp) on every inbound message
- **FR-002**: System MUST query `customer_identifiers` table before creating new customer records to prevent duplicates
- **FR-003**: System MUST retrieve last 20 messages across ALL channels before generating response to ensure conversation continuity
- **FR-004**: System MUST link multiple identifiers (email, phone) to single customer record when confirmed
- **FR-005**: System MUST acknowledge previous interactions in responses: "I see you contacted us about X last week via email. How can I help further?"
- **FR-006**: System MUST log channel switches (email → WhatsApp) in `conversations` table with timestamp and metadata

**Multi-Channel Response Generation**:
- **FR-007**: System MUST generate channel-appropriate responses: Email (formal, detailed, ≤500 words), WhatsApp (concise, conversational, ≤300 chars), Web Form (semi-formal, ≤300 words)
- **FR-008**: System MUST validate response length limits before sending and truncate/split if exceeded
- **FR-009**: System MUST use conversation context (last 20 messages) as input to AI model for response generation
- **FR-010**: System MUST search knowledge base (PostgreSQL with pgvector) for relevant information before responding
- **FR-011**: System MUST format responses for channel (HTML email, plain text WhatsApp, formatted JSON for web form)

**Escalation Logic**:
- **FR-012**: System MUST escalate immediately to human for triggers: pricing questions, refund requests, legal inquiries, profanity/directed anger, human request ("speak to human")
- **FR-013**: System MUST escalate after 2 failed knowledge base searches (customer's need cannot be satisfied with available information)
- **FR-014**: System MUST include full conversation context in escalation (all messages, channel history, customer identifiers)
- **FR-015**: System MUST notify human of escalation via configured mechanism (email, ticket system, alert)
- **FR-016**: System MUST respond to customer with escalation confirmation and expected response time ("A team member will contact you within 1 hour")

**Channel-Specific Message Processing**:
- **FR-017**: System MUST receive Gmail messages via Pub/Sub push webhook, validate signature, parse email content (sender, subject, body)
- **FR-018**: System MUST receive WhatsApp messages via Twilio webhook, validate signature, parse message content (sender phone, message text, profile name)
- **FR-019**: System MUST receive web form submissions via POST /support/submit, validate fields (name, email, subject, category, message)
- **FR-020**: System MUST persist all inbound messages to `messages` table with channel, customer_id, timestamp, content
- **FR-021**: System MUST publish message processing events to Kafka for asynchronous handling

**Response Delivery**:
- **FR-022**: System MUST send email responses via Gmail API with appropriate subject line (RE: [original subject])
- **FR-023**: System MUST send WhatsApp responses via Twilio API to customer's phone number
- **FR-024**: System MUST provide web form responses via GET /support/ticket/{ticket_id} endpoint (polling) or WebSocket (real-time)
- **FR-025**: System MUST mark conversation as "escalated" in database if human response required
- **FR-026**: System MUST update conversation status (open, processing, resolved, escalated) as state changes

**24/7 Operation & Resilience**:
- **FR-027**: System MUST operate continuously without human intervention for 24+ hours
- **FR-028**: System MUST survive pod restarts (Kubernetes terminates pods randomly) without message loss
- **FR-029**: System MUST maintain conversation state in PostgreSQL (pods are stateless)
- **FR-030**: System MUST support horizontal scaling (multiple API and worker pods via Kubernetes HPA)
- **FR-031**: System MUST implement dead letter queue (DLQ) for failed Kafka messages
- **FR-032**: System MUST provide /health endpoint returning status of all channels (email, WhatsApp, web form)
- **FR-033**: System MUST degrade gracefully if single channel fails (other channels continue operating)
- **FR-034**: System MUST retry failed operations with exponential backoff (3 attempts minimum)

**Observability & Monitoring**:
- **FR-035**: System MUST log all operations in structured JSON format with timestamp, customer_id (redacted), conversation_id, channel, event_type
- **FR-036**: System MUST expose metrics at /metrics/channels endpoint: response count, average latency, escalation rate, customer satisfaction (sentiment trend) by channel
- **FR-037**: System MUST track agent-level metrics: tool usage frequency, knowledge base hit rate, token usage per conversation, error rate
- **FR-038**: System MUST track system-level metrics: pod health, Kafka consumer lag, PostgreSQL connection pool utilization, API error rate (4xx/5xx)
- **FR-039**: System MUST trigger alerts: escalation rate > 25%, P95 latency > 3s, pod crash loop > 3 times in 10 min, Kafka lag > 100 messages

**Data Privacy & Security**:
- **FR-040**: System MUST store all credentials in Kubernetes Secrets, never in code or repository
- **FR-041**: System MUST validate webhook signatures (Gmail Pub/Sub, Twilio) to prevent spoofing
- **FR-042**: System MUST sanitize all inbound messages to prevent injection attacks (SQL, XSS, etc.)
- **FR-043**: System MUST redact customer PII (email, phone) from logs before logging, use customer_id instead
- **FR-044**: System MUST store customer data (emails, phones, conversations) securely in PostgreSQL with encryption at rest

### Key Entities

**Customer**: Represents a customer who can contact support via multiple channels
- Attributes: customer_id (unique), primary_identifier (email or phone), created_at, metadata (JSONB)
- Relationships: One-to-many with CustomerIdentifier, Conversation

**CustomerIdentifier**: Links customers to their contact methods (email, phone)
- Attributes: identifier_id (unique), customer_id (foreign key), identifier_type (email/phone), identifier_value, verified (boolean), created_at
- Relationships: Many-to-one with Customer

**Conversation**: Represents a support conversation/ticket
- Attributes: conversation_id (unique), customer_id (foreign key), channel (email/whatsapp/web), status (open/processing/resolved/escalated), subject, category, created_at, updated_at, metadata (JSONB)
- Relationships: Many-to-one with Customer, one-to-many with Message

**Message**: Represents a single message in a conversation
- Attributes: message_id (unique), conversation_id (foreign key), channel (inbound_email/outbound_email/inbound_whatsapp/outbound_whatsapp/inbound_web/outbound_web), direction (inbound/outbound), content, sent_at, created_at
- Relationships: Many-to-one with Conversation

**KnowledgeBaseArticle**: Represents support documentation/FAQ content
- Attributes: article_id (unique), title, content, category, embedding (vector using pgvector), created_at, updated_at
- Relationships: Used for similarity search when answering customer queries

**Escalation**: Represents human escalation events
- Attributes: escalation_id (unique), conversation_id (foreign key), reason (pricing/refund/legal/anger/search_failed/human_request), full_context (JSON), status (pending/in_progress/resolved), created_at, resolved_at
- Relationships: Many-to-one with Conversation

## Success Criteria

### Measurable Outcomes

**Customer Experience & Satisfaction**:
- **SC-001**: >95% of customers identified correctly across channels (same email/phone linked to single customer record)
- **SC-002**: P95 response time < 3 seconds (measured from customer message receipt to Digital FTE response sent)
- **SC-003**: <25% of conversations escalate to human (Digital FTE resolves >75% independently)
- **SC-004**: 90% of customers rate Digital FTE responses as helpful or better (via post-interaction sentiment analysis)
- **SC-005**: Zero customers report "I had to repeat myself" (cross-channel continuity verified)

**Operational Excellence**:
- **SC-006**: System uptime > 99.9% (excluding planned maintenance windows)
- **SC-007**: System survives 24-hour continuous operation test with 100+ web submissions, 50+ emails, 50+ WhatsApp messages
- **SC-008**: System survives random pod kills (1 of 3 API pods, 1 of 3 worker pods) without message loss
- **SC-009**: System degrades gracefully when single channel fails (other channels continue, no crashes)
- **SC-010**: All Kafka messages processed (DLQ empty or reviewed) after 24-hour test
- **SC-011**: P95 latency < 3 seconds for all channels (web form, email, WhatsApp)

**Business Value & Cost Efficiency**:
- **SC-012**: Digital FTE operating cost < $1,000/year (vs $75,000/year human FTE baseline)
- **SC-013**: Digital FTE handles 100+ customer inquiries per day (scaling tested via load test)
- **SC-014**: Digital FTE reduces human support workload by >80% (only 20% of conversations escalate)
- **SC-015**: Digital FTE operates 168 hours/week (vs 40 hours/week for human FTE = 4.2x coverage improvement)

**Quality & Reliability**:
- **SC-016**: All testable edge cases from incubation phase have automated tests (minimum 10 per channel)
- **SC-017**: Load test passes with 100+ concurrent users (via Locust simulation)
- **SC-018**: All unit tests pass, all integration tests pass (multi-channel E2E tests)
- **SC-019**: Web Support Form component validated, embeddable, submission successful, status check functional
- **SC-020**: Documentation complete (deployment guide, API documentation, runbook for incident response)

## Assumptions

**Technology Assumptions**:
- Python 3.11+ for backend (FastAPI, async/await patterns)
- PostgreSQL 16 with pgvector extension for CRM and knowledge base vector search
- Apache Kafka for event streaming (Confluent Cloud acceptable for simplicity)
- Kubernetes for orchestration (minikube for local, any cloud provider for production)
- Gmail API with Pub/Sub push notifications for email integration
- Twilio WhatsApp Sandbox for development (production WhatsApp Business API not required)
- React/Next.js for Web Support Form component (standalone, embeddable)
- OpenAI Agents SDK for production agent implementation (with @function_tool decorators)
- Model Context Protocol (MCP) for incubation phase prototyping

**Data Assumptions**:
- Knowledge base contains 100+ support articles covering common topics (setup, billing, API, troubleshooting)
- Customer data starts empty (no historical migration needed)
- Conversation history retained indefinitely (no automatic deletion for MVP)
- Vector embeddings generated using OpenAI text-embedding-3-small model

**Operational Assumptions**:
- Development environment uses Twilio WhatsApp Sandbox (free testing)
- Production deployment targets 3 API pods + 3 worker pods minimum (horizontal scaling)
- Alerts configured to send to project team (email/Slack/PagerDuty as available)
- Log aggregation available (Loki, ELK, or CloudWatch)
- 24-hour test performed in development environment before production deployment

**Business Assumptions**:
- Digital FTE represents single Customer Success Representative role (not team management)
- Escalations go to existing human support team (no new hiring)
- Web Support Form embedded on existing company website (not building new website)
- Pricing inquiries escalate to sales team (not handled by Digital FTE)
- Legal inquiries escalate to legal team (not handled by Digital FTE)

**Scope Exclusions (Explicitly Out of Scope)**:
- Full website development (only web form component required)
- External CRM integration (Salesforce, HubSpot - PostgreSQL IS the CRM)
- Production WhatsApp Business account (Twilio Sandbox sufficient for hackathon)
- Billing or payment processing (escalated, not handled)
- Live chat or phone voice support (only email, WhatsApp, web form)
- Multilingual support (assumes English-only for MVP)
- Video or file sharing capabilities (text-only for MVP)
- Social media integration (Twitter, Facebook Messenger not required)
- Mobile app (web-responsive form sufficient)

## Dependencies

**Internal Dependencies**:
- Constitution (.specify/memory/constitution.md) - All 7 principles must be upheld (Multi-Channel Design, Agent Maturity Model, 24/7 Operational Excellence, Cross-Channel Continuity, Test-Driven Reliability, Data Privacy & Security, Observability & Metrics)
- Plan (to be created via /sp.plan) - Architecture decisions, component design, data model
- Tasks (to be created via /sp.tasks) - Implementation tasks with dependencies

**External Dependencies**:
- OpenAI API access (GPT-4o model for agent reasoning)
- Gmail API credentials (OAuth2 service account for webhook push)
- Twilio account (WhatsApp Sandbox free tier for development)
- PostgreSQL 16 server with pgvector extension installed
- Kafka cluster (Confluent Cloud free tier or self-hosted)
- Kubernetes cluster (minikube for local, cloud provider for production)

**Development Tools**:
- Claude Code (primary development tool throughout hackathon)
- VS Code (for manual code editing)
- Docker Desktop (for local PostgreSQL, Kafka, Kubernetes)
- Git (version control)

**Documentation Dependencies**:
- OpenAI Agents SDK documentation (function_tool, assistants API)
- FastAPI documentation (async webhooks, background tasks)
- pgvector documentation (vector similarity search)
- Gmail API documentation (Pub/Sub push notifications)
- Twilio WhatsApp API documentation (webhook format, signature validation)
