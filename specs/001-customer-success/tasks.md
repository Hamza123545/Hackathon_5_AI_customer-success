# Tasks: Customer Success Digital FTE

**Input**: Design documents from `/specs/001-customer-success/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Tests are OPTIONAL for this hackathon - only include test tasks if explicitly requested during implementation. Tasks below focus on Red-Green-Refactor workflow per Constitution Principle V (Test-Driven Reliability).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Separated frontend/backend structure**:
  - `backend/` - All backend Python code (FastAPI, agent, channels, workers, database, tests, k8s)
  - `frontend/` - All frontend React/Next.js code (components, pages, lib, styles)
  - `docs/` - Shared documentation (deployment guides, API docs, runbooks)

**Folder Structure**:
  - **Backend**:
    - `backend/agent/` - Agent definition, tools, prompts, formatters
    - `backend/channels/` - Channel handlers (Gmail, WhatsApp, Web Form backend logic)
    - `backend/workers/` - Message processor, metrics collector
    - `backend/api/` - FastAPI application
    - `backend/database/` - Schema, migrations, queries
    - `backend/tests/` - All backend tests (unit, integration, E2E, load, chaos)
    - `backend/k8s/` - Kubernetes manifests for backend
    - `backend/Dockerfile` - Backend container image
    - `backend/docker-compose.yml` - Local development (PostgreSQL, Kafka)
    - `backend/requirements.txt` - Python dependencies
    - `backend/pyproject.toml` - Python project config

  - **Frontend**:
    - `frontend/src/` - Next.js source code
    - `frontend/src/components/` - React components (SupportForm.jsx)
    - `frontend/src/pages/` - Next.js pages (if needed)
    - `frontend/src/lib/` - Utilities, API client functions
    - `frontend/src/styles/` - CSS/Modules
    - `frontend/public/` - Static assets
    - `frontend/package.json` - Node dependencies
    - `frontend/next.config.js` - Next.js configuration
    - `frontend/Dockerfile` - Frontend container image
    - `frontend/.env.example` - Frontend environment variables

  - **Shared**:
    - `docs/` - Shared documentation
    - `docs/DEPLOYMENT_GUIDE.md` - Deployment instructions
    - `docs/API_DOCUMENTATION.md` - API documentation
    - `docs/RUNBOOK.md` - Incident response procedures
    - `docs/TRANSITION_GUIDE.md` - Incubation → Specialization guide

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create backend and frontend folder structures, initialize Python and Node.js projects with all required dependencies per Agent Maturity Model Phase 2 (Specialization).

### Backend Setup

- [x] T001 Create backend/ folder structure (agent/, channels/, workers/, api/, database/, tests/, k8s/)
- [x] T002 Initialize Python 3.11+ project with pyproject.toml in backend/
- [x] T003 [P] Create backend/requirements.txt with dependencies: fastapi, uvicorn, asyncpg, pgvector, aiokafka, openai, twilio, google-api-python-client, pydantic, pytest, pytest-asyncio, locust
- [x] T004 [P] Create backend/Dockerfile for multi-stage build (API + Worker images)
- [x] T005 [P] Create backend/docker-compose.yml for local development (PostgreSQL, Kafka, Redis)
- [x] T006 [P] Create backend/.env.example template with all required environment variables (OPENAI_API_KEY, POSTGRES_*, GMAIL_*, TWILIO_*, KAFKA_*)
- [x] T007 Create backend/tests/__init__.py and configure pytest with asyncio mode
- [x] T008 [P] Create backend/tests/conftest.py with asyncpg test database fixture and Kafka test container fixture

### Frontend Setup

- [x] T009 [P] Initialize Next.js project in frontend/ folder (npx create-next-app@latest or manual setup)
- [x] T010 [P] Create frontend/package.json with dependencies: react, next, axios, swr (optional), tailwindcss (optional)
- [x] T011 [P] Create frontend/next.config.js with API configuration (rewrites for API proxy if needed)
- [x] T012 [P] Create frontend/.env.example template with frontend environment variables (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_NAME)
- [x] T013 [P] Create frontend/Dockerfile for multi-stage build (node:18-alpine → build → nginx:alpine)
- [x] T014 [P] Create frontend/src/lib/ folder structure (apiClient.js, utils.js)
- [x] T015 [P] Create frontend/src/components/ folder for React components

### Shared Documentation Setup

- [x] T016 [P] Create docs/ folder
- [x] T017 [P] Create docs/README.md with project overview and folder structure explanation

**Checkpoint**: Backend and frontend project structures ready, dependencies declared, local development environments configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend infrastructure that MUST be complete before ANY user story can be implemented. Frontend API client setup also included.

### ⚠️ CRITICAL: No user story work can begin until this phase is complete

### Database Layer (PostgreSQL + pgvector)

- [x] T018 Create backend/database/schema.sql with all tables (customers, customer_identifiers, conversations, messages, tickets, knowledge_base, escalations, channel_configs, agent_metrics)
- [x] T019 [P] Create backend/database/migrations/001_initial_schema.sql with CREATE INDEX statements for performance (idx_customers_email, idx_customer_identifiers_value, idx_conversations_customer, idx_messages_conversation, idx_knowledge_embedding)
- [x] T020 [P] Create backend/database/queries.py with asyncpg connection pool singleton (get_db_pool() function)
- [x] T021 [P] Implement CustomerRepository in backend/database/queries.py (create_customer, get_customer_by_email, get_customer_by_phone, link_identifier)
- [x] T022 [P] Implement CustomerIdentifierRepository in backend/database/queries.py (create_identifier, get_identifiers_by_customer_id, verify_identifier)
- [x] T023 [P] Implement ConversationRepository in backend/database/queries.py (create_conversation, get_conversation_with_messages, get_active_conversation, update_conversation_status)
- [x] T024 [P] Implement MessageRepository in backend/database/queries.py (create_message, get_messages_by_conversation, get_last_20_messages_by_customer)
- [x] T025 [P] Implement TicketRepository in backend/database/queries.py (create_ticket, get_ticket_by_id, update_ticket_status)
- [x] T026 [P] Implement KnowledgeBaseRepository in backend/database/queries.py with pgvector similarity search (search_articles, seed_articles_with_embeddings)
- [x] T027 [P] Implement EscalationRepository in backend/database/queries.py (create_escalation, update_escalation_status)
- [x] T028 [P] Implement AgentMetricsRepository in backend/database/queries.py (record_metric, get_metrics_by_channel)

### Event Streaming (Kafka)

- [x] T029 Create backend/workers/kafka_config.py with topic definitions (TICKETS_INCOMING, ESCALATIONS, METRICS, DLQ) and bootstrap servers configuration
- [x] T030 [P] Implement KafkaProducerManager in backend/workers/kafka_config.py with AIOKafkaProducer, enable_idempotence=True, serialization
- [x] T031 [P] Implement KafkaConsumerManager in backend/workers/kafka_config.py with AIOKafkaConsumer, group_id="fte-message-processor", enable_auto_commit=False
- [x] T032 Implement publish_event() utility in backend/workers/kafka_config.py with error handling and retry logic (3 attempts with exponential backoff)

### Configuration & Secrets (Kubernetes)

- [x] T033 Create backend/k8s/namespace.yaml with customer-success-fte namespace
- [x] T034 [P] Create backend/k8s/configmap.yaml with environment variables (LOG_LEVEL, KAFKA_BOOTSTRAP_SERVERS, POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, channel configs)
- [x] T035 [P] Create backend/k8s/secrets.yaml template (ftype: Opaque) with placeholders for OPENAI_API_KEY, POSTGRES_PASSWORD, GMAIL_CREDENTIALS, TWILIO_*
- [x] T036 [P] Create backend/k8s/postgres-statefulset.yaml for PostgreSQL 16 with pgvector extension (PVC PersistentVolumeClaim)

### Error Handling & Logging

- [x] T037 Create backend/api/logging_config.py with structured JSON logger (timestamp, customer_id redacted, conversation_id, channel, event_type)
- [x] T038 [P] Implement error handlers in backend/api/errors.py (DatabaseConnectionError, KafkaPublishError, WebhookValidationError, rate limiting exceptions)
- [x] T039 [P] Implement CircuitBreaker in backend/api/errors.py for graceful degradation (Gmail API down, Twilio API down)

### Frontend API Client Setup

- [x] T040 [P] Create frontend/src/lib/apiClient.js with axios instance configured (baseURL from NEXT_PUBLIC_API_URL, timeout, headers)
- [x] T041 [P] Implement submitSupportForm() function in frontend/src/lib/apiClient.js (POST to /support/submit with formData, returns ticket_id)
- [x] T042 [P] Implement getTicketStatus() function in frontend/src/lib/apiClient.js (GET from /support/ticket/{ticket_id}, returns ticket with messages)
- [x] T043 [P] Implement error handling in frontend/src/lib/apiClient.js (try/catch, user-friendly error messages, loading states)

**Checkpoint**: Foundation ready - backend data layer, event streaming, orchestration, error handling complete. Frontend API client ready. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Multi-Channel Inquiry (Priority: P1) 🎯 MVP

**Goal**: Implement core multi-channel support (Gmail, WhatsApp, Web Form) with customer identification, knowledge base search, and intelligent escalation. This is the MVP - customers receive instant, accurate, channel-appropriate support 24/7.

**Independent Test**:
1. Send test email to support@company.com → Verify response received within SLA, format is formal/detailed, customer identified
2. Send test WhatsApp message → Verify response received within SLA, format is concise (≤300 chars), customer identified
3. Submit web form → Verify ticket_id returned, response received via status page, format is semi-formal
4. Verify returning customer (same email/phone) → System retrieves last 20 messages, acknowledges previous interaction
5. Ask simple FAQ question → Knowledge base searched, accurate answer provided
6. Ask pricing question → Immediate escalation triggered, appropriate response sent

### Implementation for User Story 1

#### Agent Tools (OpenAI Agents SDK with @function_tool)

- [x] T044 [P] [US1] Create backend/agent/tools.py with Pydantic input models (KnowledgeSearchInput, TicketInput, CustomerHistoryInput, EscalationInput, ResponseInput)
- [x] T045 [P] [US1] Implement search_knowledge_base tool with @function_tool decorator in backend/agent/tools.py (pgvector similarity search via KnowledgeBaseRepository)
- [x] T046 [P] [US1] Implement create_ticket tool with @function_tool decorator in backend/agent/tools.py (via TicketRepository, stores in tickets table)
- [x] T047 [P] [US1] Implement get_customer_history tool with @function_tool decorator in backend/agent/tools.py (via MessageRepository, retrieves last 20 messages across ALL channels)
- [x] T048 [P] [US1] Implement escalate_to_human tool with @function_tool decorator in backend/agent/tools.py (via EscalationRepository, publishes to fte.escalations topic)
- [x] T049 [P] [US1] Implement send_response tool with @function_tool decorator in backend/agent/tools.py (calls appropriate channel handler)

#### Agent Definition & System Prompt

- [x] T050 [US1] Create backend/agent/customer_success_agent.py with OpenAI Agents initialization (OpenAI() client, Agent definition)
- [x] T051 [US1] Create backend/agent/prompts.py with system prompt including channel awareness, escalation triggers (pricing, refund, legal, profanity, anger, human request), response length limits (Email ≤ 500 words, WhatsApp ≤ 300 chars, Web ≤ 300 words)
- [x] T052 [US1] Implement agent.run() method in backend/agent/customer_success_agent.py with tool binding and context variables (customer_id, conversation_id, channel, ticket_subject)
- [x] T053 [US1] Create backend/agent/formatters.py with format_response_for_channel() function (HTML email, plain text WhatsApp, formatted JSON web)
- [x] T054 [US1] Implement sentiment analysis in backend/agent/formatters.py (profanity detection, urgency keywords, sentiment_score -1.0 to 1.0)

#### Channel Handlers

- [x] T055 [P] [US1] Create backend/channels/gmail_handler.py with setup_push_notifications() function (Gmail API Pub/Sub webhook configuration)
- [x] T056 [P] [US1] Implement process_notification() in backend/channels/gmail_handler.py (fetch new messages via users.messages.list, parse sender/subject/body)
- [x] T057 [P] [US1] Implement send_reply() in backend/channels/gmail_handler.py (send via Gmail API with threading support, RE: [original subject])
- [x] T058 [US1] Implement _extract_body() in backend/channels/gmail_handler.py (parse base64 encoded email body)
- [x] T059 [US1] Implement Pub/Sub signature validation in backend/channels/gmail_handler.py (verify X-Goog-Signature header, reject 403 if invalid)

- [x] T060 [P] [US1] Create backend/channels/whatsapp_handler.py with validate_webhook() function (Twilio RequestValidator with TWILIO_AUTH_TOKEN)
- [x] T061 [P] [US1] Implement process_webhook() in backend/channels/whatsapp_handler.py (parse Twilio webhook: MessageSid, From, Body, ProfileName)
- [x] T062 [P] [US1] Implement send_message() in backend/channels/whatsapp_handler.py (send via Twilio API)
- [x] T063 [US1] Implement format_response() in backend/channels/whatsapp_handler.py (split long responses >300 chars into multiple messages with "..." + "Reply for more")

- [x] T064 [P] [US1] Create backend/channels/web_form_handler.py with Pydantic models (SupportFormSubmission, SupportFormResponse) validating Name (≥2 chars), Email (EmailStr), Subject (≥5 chars), Message (≥10 chars), Category (general/technical/billing/feedback/bug_report)
- [x] T065 [P] [US1] Implement submit_support_form() in backend/channels/web_form_handler.py (create ticket via TicketRepository, publish to Kafka fte.tickets.incoming, return ticket_id)
- [x] T066 [P] [US1] Implement get_ticket_status() in backend/channels/web_form_handler.py (retrieve ticket with messages via TicketRepository and MessageRepository)
- [x] T067 [US1] Implement CORS configuration for web form in backend/channels/web_form_handler.py (allow_origins=["*"] for development, configure for production)

#### Frontend Support Form Component

- [x] T068 [P] [US1] Create frontend/src/components/SupportForm.jsx with form fields (Name, Email, Subject, Category dropdown, Message textarea)
- [x] T069 [P] [US1] Implement form validation in frontend/src/components/SupportForm.jsx (client-side validation: name≥2, email format, subject≥5, message≥10, error messages)
- [x] T070 [US1] Implement form submission handler in frontend/src/components/SupportForm.jsx (call submitSupportForm(), show loading state, handle success/error, display ticket_id)
- [x] T071 [US1] Implement ticket status checking UI in frontend/src/components/SupportForm.jsx (input field for ticket_id, "Check Status" button calling getTicketStatus(), display messages)
- [x] T072 [US1] Add responsive styling to frontend/src/components/SupportForm.jsx (mobile-friendly, clean UI, loading spinners, success/error colors)
- [x] T073 [US1] Create frontend/src/pages/index.jsx (or app/page.jsx for Next.js App Router) to render SupportForm component
- [x] T074 [US1] Configure API URL in frontend/.env.local (NEXT_PUBLIC_API_URL=http://localhost:8000 for development)

#### API Gateway (FastAPI)

- [x] T075 [P] [US1] Create backend/api/main.py with FastAPI() application initialization
- [x] T076 [P] [US1] Implement POST /webhooks/gmail endpoint in backend/api/main.py (validate Pub/Sub signature, parse message, publish to Kafka, return 200 OK)
- [x] T077 [P] [US1] Implement POST /webhooks/whatsapp endpoint in backend/api/main.py (validate Twilio signature, parse form-data, publish to Kafka, return 200 OK with empty TwiML)
- [x] T078 [P] [US1] Implement POST /support/submit endpoint in backend/api/main.py (validate SupportFormSubmission via Pydantic, call submit_support_form(), return ticket_id)
- [x] T079 [P] [US1] Implement GET /support/ticket/{ticket_id} endpoint in backend/api/main.py (call get_ticket_status(), return messages JSON)
- [x] T080 [P] [US1] Implement GET /conversations/{conversation_id} endpoint in backend/api/main.py (retrieve conversation history with cross-channel context via ConversationRepository)
- [x] T081 [P] [US1] Implement GET /customers/lookup endpoint in backend/api/main.py (query params: email/phone, cross-channel lookup via CustomerIdentifierRepository)
- [x] T082 [P] [US1] Implement GET /metrics/channels endpoint in backend/api/main.py (return channel-specific metrics: response count, avg latency, escalation rate, avg sentiment via AgentMetricsRepository)
- [x] T083 [P] [US1] Implement GET /health endpoint in backend/api/main.py (return all channel status: email/active, whatsapp/active, web_form/active)
- [x] T084 [US1] Add CORSMiddleware to backend/api/main.py (allow_origins=["http://localhost:3000"] for development, configure for production)
- [x] T085 [US1] Implement structured JSON logging for all endpoints in backend/api/main.py (use logging_config.py, redact customer_id)

#### Message Processing Layer (Worker Pods)

- [ ] T086 [US1] Create backend/workers/message_processor.py with Kafka consumer initialization (consume fte.tickets.incoming topic)
- [ ] T087 [US1] Implement process_message() async function in backend/workers/message_processor.py (resolve/create customer via CustomerRepository, get/create conversation via ConversationRepository)
- [ ] T088 [US1] Implement retrieve_customer_history() in backend/workers/message_processor.py (call get_customer_history tool, pass last 20 messages to agent)
- [ ] T089 [US1] Implement run_agent() in backend/workers/message_processor.py (call agent.run() with tools, context variables, customer history)
- [ ] T090 [US1] Implement store_inbound_message() in backend/workers/message_processor.py (via MessageRepository with direction='inbound', role='customer')
- [ ] T091 [US1] Implement store_outbound_message() in backend/workers/message_processor.py (via MessageRepository with direction='outbound', role='agent', tokens_used, latency_ms)
- [ ] T092 [US1] Implement publish_response() in backend/workers/message_processor.py (call send_response tool, publish to appropriate outbound topic)
- [ ] T093 [US1] Implement error handling in backend/workers/message_processor.py (publish to fte.dlq topic on failure, log error, retry 3 times with exponential backoff)
- [ ] T094 [US1] Implement consumer offset commit in backend/workers/message_processor.py (commit only after successful processing, enable exactly-once semantics)

#### Kubernetes Deployment (API & Worker)

- [ ] T095 [P] [US1] Create backend/k8s/deployment-api.yaml with fte-api deployment (3 replicas, resources 512Mi/250m → 1Gi/500m, health checks liveness 10s delay, readiness 5s delay)
- [ ] T096 [P] [US1] Create backend/k8s/deployment-worker.yaml with fte-message-processor deployment (3 replicas, resources 512Mi/250m → 1Gi/500m, health checks)
- [ ] T097 [P] [US1] Create backend/k8s/service.yaml for fte-api (Service type ClusterIP, port 80 targetPort 8000)
- [ ] T098 [P] [US1] Create backend/k8s/hpa-api.yaml with Horizontal Pod Autoscaler for fte-api (min 3, max 20, target 70% CPU)
- [ ] T099 [P] [US1] Create backend/k8s/hpa-worker.yaml with Horizontal Pod Autoscaler for fte-message-processor (min 3, max 30, target 70% CPU)
- [ ] T100 [US1] Create backend/k8s/ingress.yaml with TLS (Let's Encrypt via cert-manager), host support-api.yourdomain.com, rules / path → fte-api:80

**Checkpoint**: User Story 1 complete - All 3 channels (Gmail, WhatsApp, Web Form) functional, customer identification across channels working, knowledge base search operational, escalation logic implemented. Frontend support form working. STOP and VALIDATE independently.

---

## Phase 4: User Story 2 - Cross-Channel Conversation Continuity (Priority: P1)

**Goal**: Ensure customers never repeat themselves when switching channels. System links email/phone to single customer_id, retrieves last 20 messages across ALL channels, agent acknowledges previous interactions.

**Independent Test**:
1. Customer A sends email about "API authentication failing" → Record conversation_id
2. Customer A follows up via WhatsApp 2 days later "Still having API issues" → Verify system identifies via phone number, retrieves email conversation, responds "I see you emailed about 401 errors 3 days ago. Are you still experiencing the same authentication issue?"
3. Customer A submits web form 1 week later with related detail → Verify system links to same conversation, shows full history
4. Verify all interactions linked to single customer_id (check database)
5. Verify agent acknowledges cross-channel context "I see you mentioned X in your email 2 days ago" in WhatsApp response
6. Verify customer with email john@example.com and phone +1-555-0100 correctly linked (both identifiers in customer_identifiers table)

### Implementation for User Story 2

#### Customer Identifier Linking

- [ ] T101 [P] [US2] Implement resolve_or_create_customer() in backend/workers/message_processor.py (query customer_identifiers table by email/phone, create if not exists, link multiple identifiers via CustomerIdentifierRepository)
- [ ] T102 [P] [US2] Implement link_customer_identifier() in backend/workers/message_processor.py (when customer uses new identifier, add to customer_identifiers table, set verified=True)
- [ ] T103 [US2] Implement get_customer_identifiers() in backend/workers/message_processor.py (retrieve all linked identifiers via CustomerIdentifierRepository, return email and phone if both exist)
- [ ] T104 [US2] Implement customer_merge_logic() in backend/workers/message_processor.py (if two customer records exist for same person, merge conversations/messages/tickets to single customer_id)

#### Cross-Channel Conversation Retrieval

- [ ] T105 [US2] Implement get_last_20_messages_by_customer() in backend/database/queries.py (JOIN conversations + messages across ALL channels, ORDER BY created_at DESC LIMIT 20, include channel metadata)
- [ ] T106 [US2] Implement get_conversation_history_by_customer() in backend/workers/message_processor.py (call get_customer_history tool with all identifiers, retrieve messages from email, WhatsApp, web combined)
- [ ] T107 [US2] Implement format_conversation_context() in backend/agent/formatters.py (prepend context to agent: "Customer History (last 20 messages across all channels): ..." with channel labels: [Email], [WhatsApp], [Web])
- [ ] T108 [US2] Implement log_channel_switch() in backend/workers/message_processor.py (when customer switches channels, log in conversations.metadata.channel_switches with timestamp)

#### Agent Prompt Enhancement

- [ ] T109 [US2] Update backend/agent/prompts.py system prompt with cross-channel awareness (agent MUST acknowledge previous interactions: "I see you contacted us about X last week via email. How can I help further?")
- [ ] T110 [US2] Add channel_switch_acknowledgment to backend/agent/formatters.py (detect channel switch from conversation history, prepend "Continuing our conversation from [previous_channel]..." to response)
- [ ] T111 [US2] Implement cross_channel_identifier_validation() in backend/agent/prompts.py (agent verifies identity if conflicting information across channels)

**Checkpoint**: User Story 2 complete - Cross-channel conversation continuity operational, customers never repeat themselves, agent acknowledges previous interactions across channels.

---

## Phase 5: User Story 3 - 24/7 Operational Resilience (Priority: P1)

**Goal**: System operates continuously through infrastructure disruptions (pod restarts, API failures, Kafka backlog). Customers experience no interruption, system heals automatically.

**Independent Test**:
1. Deploy 3 API pods and 3 worker pods to minikube
2. Randomly terminate 1 API pod → Verify remaining 2 pods handle traffic, Kubernetes schedules replacement, no customer-facing interruption
3. Simulate Gmail API failure (return 503 errors) → Verify WhatsApp and web form continue operating, Gmail errors logged, system auto-recovers when Gmail API returns
4. Simulate sudden load spike (50 simultaneous web form submissions) → Verify Kafka queues messages, no messages lost, all processed within SLA, consumer pods auto-scale
5. Kill worker pod during message processing → Verify unprocessed messages re-consumed from Kafka, conversation state preserved in PostgreSQL, customer experiences no interruption
6. Run 24-hour test with 100+ web submissions, 50+ emails, 50+ WhatsApp messages → Verify uptime > 99.9%, P95 latency < 3s, escalation < 25%, cross-channel ID > 95%, zero message loss

### Implementation for User Story 3

#### Pod Restart Survival (State in PostgreSQL)

- [ ] T112 [P] [US3] Implement conversation_state_validation() in backend/workers/message_processor.py (on pod restart, query conversations table for active conversations, resume from last message)
- [ ] T113 [P] [US3] Implement message_recovery_from_kafka() in backend/workers/message_processor.py (consumer starts with uncommitted offsets, re-consume unprocessed messages after restart)
- [ ] T114 [US3] Add livenessProbe to backend/k8s/deployment-api.yaml (exec /bin/sh -c "curl -f http://localhost:8000/health || exit 1", initialDelaySeconds 10, periodSeconds 10)
- [ ] T115 [US3] Add readinessProbe to backend/k8s/deployment-api.yaml (exec /bin/sh -c "curl -f http://localhost:8000/health || exit 1", initialDelaySeconds 5, periodSeconds 5)
- [ ] T116 [US3] Add livenessProbe to backend/k8s/deployment-worker.yaml (exec /bin/sh -c "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB || exit 1", initialDelaySeconds 10, periodSeconds 10)
- [ ] T117 [US3] Add readinessProbe to backend/k8s/deployment-worker.yaml (exec /bin/sh -c "kafka-console-producer --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --topic fte.healthcheck || exit 1", initialDelaySeconds 5, periodSeconds 5)

#### Horizontal Pod Autoscaling

- [ ] T118 [US3] Create backend/k8s/metrics-service.yaml for Kubernetes Metrics Server (required for HPA CPU-based scaling)
- [ ] T119 [US3] Configure HPA for fte-api in backend/k8s/hpa-api.yaml (scaleTargetRef.apiVersion=apps/v1, kind=Deployment, name=fte-api, minReplicas=3, maxReplicas=20, metrics=resource.cpu.targetAverageUtilization=70)
- [ ] T120 [US3] Configure HPA for fte-message-processor in backend/k8s/hpa-worker.yaml (scaleTargetRef.apiVersion=apps/v1, kind=Deployment, name=fte-message-processor, minReplicas=3, maxReplicas=30, metrics=resource.cpu.targetAverageUtilization=70)
- [ ] T121 [US3] Implement monitor_hpa_events() in backend/workers/metrics_collector.py (background task logs HPA scale events, tracks pod count over time)

#### Graceful Degradation (Channel Failure)

- [ ] T122 [P] [US3] Implement CircuitBreaker for Gmail API in backend/api/errors.py (track 503 errors, open circuit after 3 consecutive failures, redirect to /webhooks/gmail with 503 Unavailable)
- [ ] T123 [P] [US3] Implement CircuitBreaker for Twilio API in backend/api/errors.py (track failures, open circuit after 3 consecutive failures, redirect to /webhooks/whatsapp with 503 Unavailable)
- [ ] T124 [P] [US3] Implement continue_other_channels() in backend/workers/message_processor.py (when one channel circuit open, continue processing other channels, log errors)
- [ ] T125 [US3] Implement channel_health_monitor() in backend/workers/metrics_collector.py (background task checks Gmail API, Twilio API health every 30s, updates channel_configs.enabled, publishes to fte.metrics topic)
- [ ] T126 [US3] Add CircuitBreaker state logging in backend/api/logging_config.py (log circuit OPEN/CLOSE/HALF_OPEN events with timestamp, channel, failure_count)

#### Kafka Backlog Handling

- [ ] T127 [US3] Implement monitor_consumer_lag() in backend/workers/message_processor.py (query Kafka consumer offsets, calculate lag = current_offset - committed_offset, alert if lag > 100)
- [ ] T128 [US3] Implement scale_up_on_backlog() in backend/workers/message_processor.py (if lag > 100, trigger Kubernetes HPA scale-up via Kubernetes API client)
- [ ] T129 [US3] Implement dead_letter_queue_routing() in backend/workers/message_processor.py (if message processing fails 3 times, publish to fte.dlq topic with full context, error_reason, original_message)

#### Metrics Collection & Alerting

- [ ] T130 [P] [US3] Create backend/workers/metrics_collector.py with background task collecting metrics every 60s
- [ ] T131 [P] [US3] Implement collect_channel_metrics() in backend/workers/metrics_collector.py (count responses per channel, avg latency, escalation rate, avg sentiment via AgentMetricsRepository)
- [ ] T132 [P] [US3] Implement collect_agent_metrics() in backend/workers/metrics_collector.py (tool usage frequency, KB hit rate, token usage, error rate)
- [ ] T133 [P] [US3] Implement collect_system_metrics() in backend/workers/metrics_collector.py (pod health via Kubernetes API, Kafka consumer lag, PostgreSQL connection pool utilization, API error rate)
- [ ] T134 [P] [US3] Implement collect_business_metrics() in backend/workers/metrics_collector.py (tickets resolved, cross-channel ID rate, customer satisfaction trend)
- [ ] T135 [P] [US3] Implement alert_threshold_checks() in backend/workers/metrics_collector.py (if escalation_rate > 25%, alert; if P95_latency > 3s, alert; if pod_crash_loop > 3 in 10 min, alert; if kafka_lag > 100, alert)
- [ ] T136 [US3] Publish metrics to fte.metrics topic in backend/workers/metrics_collector.py (all metric levels: channel, agent, system, business)

#### Chaos Testing (Load Tests)

- [ ] T137 [P] [US3] Create backend/tests/load/test_web_form_load.py with Locust WebFormUser (100+ users submitting forms, wait 2-10s between)
- [ ] T138 [P] [US3] Create backend/tests/load/test_email_load.py with simulated Gmail traffic (50+ emails over 24 hours via Locust)
- [ ] T139 [P] [US3] Create backend/tests/load/test_whatsapp_load.py with simulated WhatsApp traffic (50+ messages over 24 hours via Locust)
- [ ] T140 [US3] Create backend/tests/chaos/test_pod_restart.py with random pod termination (kubectl delete pod for 1 of 3 API, 1 of 3 worker, verify no message loss)
- [ ] T141 [US3] Create backend/tests/chaos/test_channel_failure.py (disable Gmail webhook, verify WhatsApp + web form continue, validate uptime > 99.9%)
- [ ] T142 [US3] Create backend/tests/chaos/test_kafka_partition_failure.py (stop 1 of 3 Kafka brokers, verify other partitions continue, validate auto-recovery)

**Checkpoint**: User Story 3 complete - 24/7 operational resilience validated, pod restarts survived, graceful degradation implemented, horizontal autoscaling operational, chaos tests passing. All 3 user stories complete and independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, security hardening, documentation, frontend polish, and 24-hour validation test.

### Security Hardening

- [ ] T143 [P] Implement all credential management via Kubernetes Secrets in backend/k8s/secrets.yaml (OPENAI_API_KEY, POSTGRES_PASSWORD, GMAIL_CREDENTIALS, TWILIO_AUTH_TOKEN)
- [ ] T144 [P] Verify webhook signature validation for Gmail Pub/Sub (X-Goog-Signature) in backend/channels/gmail_handler.py (reject 403 if invalid, log security alert)
- [ ] T145 [P] Verify webhook signature validation for Twilio (RequestValidator with TWILIO_AUTH_TOKEN) in backend/channels/whatsapp_handler.py (reject 403 if invalid, log security alert)
- [ ] T146 [P] Implement PII redaction in backend/api/logging_config.py (logs use customer_id, NOT email/phone; redact PII: john@example.com → j***@example.com)
- [ ] T147 [P] Verify all database queries use parameterized queries (asyncpg placeholders $1, $2) in backend/database/queries.py (prevent SQL injection)
- [ ] T148 [P] Verify input validation via Pydantic models for all endpoints in backend/api/main.py (EmailStr, constr, length validation, prevent XSS)
- [ ] T149 [P] Implement rate limiting per customer (10 msgs/min) in backend/api/main.py (track message count by customer_id in Redis, return "Processing your messages... Please wait" if exceeded)

### Frontend Polish

- [ ] T150 [P] Add loading states to frontend/src/components/SupportForm.jsx (spinners during form submission, status checking)
- [ ] T151 [P] Add error boundaries to frontend/src/components/SupportForm.jsx (catch React errors, display user-friendly error messages)
- [ ] T152 [P] Implement form auto-save to localStorage in frontend/src/lib/utils.js (save draft form data, restore on page load)
- [ ] T153 [P] Add accessibility features to frontend/src/components/SupportForm.jsx (ARIA labels, keyboard navigation, screen reader support)
- [ ] T154 [P] Add unit tests for frontend components in frontend/src/components/__tests__/SupportForm.test.jsx (test form validation, submission, status checking)

### Documentation

- [ ] T155 [P] Create docs/DEPLOYMENT_GUIDE.md with step-by-step deployment instructions (minikube local, cloud production, secrets setup, kubectl apply commands, frontend/backend deployment)
- [ ] T156 [P] Create docs/API_DOCUMENTATION.md with all endpoints (POST /webhooks/gmail, POST /webhooks/whatsapp, POST /support/submit, GET /support/ticket/{id}, GET /conversations/{id}, GET /customers/lookup, GET /metrics/channels, GET /health), request/response examples, curl examples
- [ ] T157 [P] Create docs/RUNBOOK.md with incident response procedures (pod restart, channel failure, Kafka backlog, PostgreSQL connection failure, escalation spike, troubleshooting steps)
- [ ] T158 Create docs/TRANSITION_GUIDE.md (Incubation → Specialization artifacts: discovery-log.md, transition-checklist.md, test_transition.py, MCP server → OpenAI SDK transformation)

### Performance Optimization

- [ ] T159 [P] Add database indexes for performance in backend/database/migrations/002_performance_indexes.sql (verify idx_customers_email, idx_customer_identifiers_value, idx_conversations_customer, idx_messages_conversation, idx_knowledge_embedding exist)
- [ ] T160 [P] Implement PostgreSQL connection pool tuning in backend/database/queries.py (adjust min_size=5, max_size=20 based on load test results, monitor connection pool utilization)
- [ ] T161 [P] Implement Kafka producer batching in backend/workers/kafka_config.py (linger_ms=10, batch_size=100 for improved throughput)
- [ ] T162 [P] Add response caching for GET /customers/lookup in backend/api/main.py (cache customer identifiers in Redis for 60s, reduce database queries)
- [ ] T163 [P] Optimize frontend bundle size in frontend/next.config.js (enable SWC minification, tree shaking, code splitting, lazy loading)

### 24-Hour Validation Test

- [ ] T164 Create backend/tests/e2e/test_24_hour_operation.py with 24-hour continuous test scenario (100+ web submissions, 50+ emails, 50+ WhatsApp, random chaos every 2 hours)
- [ ] T165 Implement uptime_monitoring() in backend/tests/e2e/test_24_hour_operation.py (record uptime %, target > 99.9%)
- [ ] T166 Implement latency_monitoring() in backend/tests/e2e/test_24_hour_operation.py (record P95 latency per channel, target < 3s)
- [ ] T167 Implement escalation_rate_monitoring() in backend/tests/e2e/test_24_hour_operation.py (record escalation rate, target < 25%)
- [ ] T168 Implement cross_channel_id_monitoring() in backend/tests/e2e/test_24_hour_operation.py (record cross-channel customer ID accuracy, target > 95%)
- [ ] T169 Implement message_loss_validation() in backend/tests/e2e/test_24_hour_operation.py (verify fte.dlq empty, all Kafka messages processed, zero message loss)
- [ ] T170 Generate test report in backend/tests/e2e/test_24_hour_operation.py (uptime %, P95 latency per channel, escalation rate, cross-channel ID %, message loss count, PASS/FAIL all targets)

**Checkpoint**: Polish complete - All security measures implemented, frontend polished with accessibility and tests, documentation comprehensive, performance optimized, 24-hour test validates Constitution compliance.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (backend and frontend can be set up in parallel)
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - No dependencies on other stories (MVP SCOPE)
- **User Story 2 (Phase 4)**: Depends on Foundational completion + User Story 1 completion - Extends agent with cross-channel awareness
- **User Story 3 (Phase 5)**: Depends on Foundational completion + User Story 1 completion + User Story 2 completion - Adds resilience on top of working system
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Multi-Channel Inquiry**: Can start after Foundational (Phase 2) - No dependencies on other stories - **MVP SCOPE**
- **User Story 2 (P1) - Cross-Channel Conversation Continuity**: Depends on User Story 1 completion - Extends agent prompts and customer identification logic
- **User Story 3 (P1) - 24/7 Operational Resilience**: Depends on User Story 1 + User Story 2 completion - Adds resilience, HPA, chaos testing on top of working system

### Within Each User Story

- **User Story 1**: Backend Setup (T001-T008) + Frontend Setup (T009-T015) → Agent Tools (T044-T049 parallel) → Agent Definition (T050-T054 sequential) → Channel Handlers (T055-T067 parallel) → Frontend Component (T068-T074 sequential) → API Gateway (T075-T085 parallel) → Message Processing (T086-T094 sequential) → Kubernetes Deployment (T095-T100 parallel)
- **User Story 2**: Customer Identifier Linking (T101-T104 sequential) → Cross-Channel Retrieval (T105-T108 sequential) → Agent Prompt Enhancement (T109-T111 sequential)
- **User Story 3**: Pod Restart Survival (T112-T117 parallel) → Horizontal Pod Autoscaling (T118-T121 sequential) → Graceful Degradation (T122-T126 sequential) → Kafka Backlog Handling (T127-T129 sequential) → Metrics Collection (T130-T136 parallel) → Chaos Testing (T137-T142 parallel)

### Parallel Opportunities

- **Setup Phase**: T003, T004, T005, T006, T008, T009, T010, T011, T012, T013, T014, T015, T016, T017 can run in parallel
- **Foundational Phase**: T019, T020, T021-T028 (database repositories), T030, T031 (Kafka), T034, T035 (Kubernetes configs), T038, T039 (error handling), T040-T043 (frontend API client) can run in parallel
- **User Story 1**:
  - Backend Setup + Frontend Setup can run in parallel
  - Agent Tools: T045-T049 (all tools) can run in parallel
  - Channel Handlers: T055-T059 (Gmail), T060-T063 (WhatsApp), T064-T067 (Web Form) can run in parallel
  - Frontend Component: T068-T074 sequential
  - API Endpoints: T076-T083 (all endpoints) can run in parallel
  - Kubernetes Deployment: T095-T100 can run in parallel
- **User Story 2**: T101-T103 (identifier linking) can run in parallel
- **User Story 3**: T112-T117 (health probes), T122-T126 (circuit breakers), T130-T136 (metrics collectors), T137-T142 (chaos tests) can run in parallel
- **Polish Phase**: T143-T149 (security), T150-T154 (frontend polish), T155-T158 (documentation), T159-T163 (performance) can run in parallel

---

## Parallel Example: User Story 1 Backend Setup

```bash
# Launch all setup tasks together:
Task "T003 [P] Create backend/requirements.txt with dependencies"
Task "T004 [P] Create backend/Dockerfile for multi-stage build"
Task "T005 [P] Create backend/docker-compose.yml for local development"
Task "T006 [P] Create backend/.env.example template"
Task "T009 [P] Initialize Next.js project in frontend/ folder"
Task "T010 [P] Create frontend/package.json with dependencies"
Task "T011 [P] Create frontend/next.config.js with API configuration"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - RECOMMENDED FOR HACKATHON

1. Complete Phase 1: Setup (T001-T017) - Both backend and frontend
2. Complete Phase 2: Foundational (T018-T043) - **CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T044-T100)
4. **STOP AND VALIDATE**: Test User Story 1 independently
   - Send test email, WhatsApp message, web form submission
   - Verify responses received within SLA
   - Verify customer identification across channels
   - Verify knowledge base search works
   - Verify escalation triggers correctly
   - Test frontend support form (submission, status checking)
5. **Demo MVP**: User Story 1 complete (Multi-Channel Inquiry operational + Frontend working)

### Incremental Delivery

1. Complete Setup (Backend + Frontend) + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) ✅
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add Polish → Validate 24-hour test → Production ready
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T043)
2. Once Foundational is done:
   - Developer A: User Story 1 (T044-T100) - MVP FOCUS
   - Developer B: User Story 2 (T101-T111) - after US1 complete
   - Developer C: User Story 3 (T112-T142) - after US1 + US2 complete
3. Stories complete and integrate independently

---

## Summary

**Total Task Count**: 170 tasks (increased from 145 to include frontend-specific tasks)
- **Phase 1 (Setup)**: 17 tasks (8 backend + 9 frontend)
- **Phase 2 (Foundational)**: 26 tasks - BLOCKS all user stories
- **Phase 3 (User Story 1)**: 57 tasks - **MVP SCOPE**
- **Phase 4 (User Story 2)**: 11 tasks
- **Phase 5 (User Story 3)**: 31 tasks
- **Phase 6 (Polish)**: 28 tasks

**Task Count per User Story**:
- **User Story 1 (Multi-Channel Inquiry)**: 57 tasks (T044-T100) - Includes frontend component
- **User Story 2 (Cross-Channel Continuity)**: 11 tasks (T101-T111)
- **User Story 3 (24/7 Operational Resilience)**: 31 tasks (T112-T142)

**Independent Test Criteria**:
- **US1**: Send test inquiries via email, WhatsApp, web form → Verify channel-appropriate responses, customer identification, knowledge base search, escalation triggers, frontend form submission and status checking work
- **US2**: Customer contacts via email → WhatsApp → Web → Verify linked to single customer_id, last 20 messages retrieved, agent acknowledges cross-channel context
- **US3**: Deploy 3 API + 3 worker pods → Randomly terminate pods → Verify no message loss, HPA scales, uptime > 99.9%, P95 < 3s

**Parallel Opportunities Identified**: 80+ tasks marked [P] can run in parallel (different files, no dependencies)

**Suggested MVP Scope**: User Story 1 (T001-T100) - Complete Setup (Backend + Frontend) + Foundational + User Story 1, then STOP and VALIDATE independently before proceeding to User Story 2.

**Format Validation**: ✅ ALL tasks follow checklist format (`- [ ] [ID] [P?] [Story?] Description with file path`)

---

## Notes

- **[P] tasks** = Different files, no dependencies on incomplete tasks, can run in parallel
- **[Story] label** = Maps task to specific user story (US1, US2, US3) for traceability
- **NO story label** = Setup phase, Foundational phase, Polish phase tasks
- **Frontend tasks** = Paths start with `frontend/` (React/Next.js code)
- **Backend tasks** = Paths start with `backend/` (Python/FastAPI code)
- **Each user story** is independently completable and testable (verified in checkpoints)
- **Constitution Principle V (Test-Driven Reliability)**: Red-Green-Refactor workflow enforced via task organization
- **Stop at any checkpoint** to validate story independently before proceeding
- **Avoid**: Vague tasks (missing file paths), same file conflicts (multiple tasks modifying same file), cross-story dependencies that break independence
