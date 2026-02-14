<!--
SYNC IMPACT REPORT
==================
Version Change: 0.0.0 → 1.0.0
Rationale: MAJOR version - Initial constitution creation for Customer Success Digital FTE project

Modified Principles:
- N/A (initial creation)

Added Sections:
- I. Multi-Channel Customer-Centric Design
- II. Agent Maturity Model (Incubation → Specialization → Production)
- III. 24/7 Operational Excellence
- IV. Cross-Channel Conversation Continuity
- V. Test-Driven Reliability (NON-NEGOTIABLE)
- VI. Data Privacy & Security
- VII. Observability & Metrics

Removed Sections:
- N/A

Template Updates:
- ✅ plan-template.md - Aligned with Agent Maturity Model phases
- ✅ spec-template.md - Verified multi-channel user scenarios included
- ✅ tasks-template.md - Confirmed TDD and phased implementation
- ✅ commands/sp.plan.md - Aligns with Incubation → Specialization workflow
- ✅ commands/sp.implement.md - Supports gradual rollout and validation
- ⚠ README.md - Needs creation after project structure established
- ⚠ docs/architecture.md - To be created during Phase 0 (plan command)

Follow-up TODOs:
- None - All placeholders filled with concrete governance rules
-->

# Customer Success Digital FTE Constitution

## Core Principles

### I. Multi-Channel Customer-Centric Design

Every feature MUST serve customers across **all three channels** (Gmail, WhatsApp, Web Form) with channel-appropriate experiences. No channel is "second-class" - each receives equal design consideration, testing investment, and operational support.

**Rules:**
- ALL user stories MUST specify behavior for Email (formal, detailed), WhatsApp (concise, conversational), and Web Form (semi-formal)
- Response length limits ARE hard constraints: Email ≤ 500 words, WhatsApp ≤ 300 chars, Web ≤ 300 words
- Cross-channel customer identification IS required: Email address or phone number MUST resolve to unified customer_id
- Channel switching IS a first-class scenario: Customers who start on email and continue via WhatsApp MUST see their conversation history preserved

**Rationale:** Digital FTEs succeed when customers experience seamless support regardless of their preferred communication method. Channel-specific formatting prevents friction (long emails on WhatsApp, short texts in email). Unified customer identification prevents "I already told you this" frustration.

### II. Agent Maturity Model (Incubation → Specialization → Production)

Features MUST evolve through three distinct stages with explicit transitions. Skipping stages or blurring boundaries IS prohibited. Each stage has defined inputs, outputs, and exit criteria.

**Incubation (Hours 1-16):**
- Input: Problem statement + context folder (company profile, product docs, sample tickets)
- Output: Working prototype, MCP server, discovery log, agent skills manifest
- Method: Use Claude Code interactively to explore requirements and iterate rapidly
- Exit Criteria: Prototype handles 20+ test cases, edge cases documented, performance baseline measured
- Artifacts: `specs/discovery-log.md`, `specs/customer-success-fte-spec.md`, MCP server with 5+ tools

**Specialization (Hours 17-40):**
- Input: Complete incubation artifacts + transition checklist
- Output: Production code (OpenAI SDK, FastAPI, PostgreSQL schema, Kafka setup, Kubernetes manifests)
- Method: Transform prototype into hardened, autonomous system using Claude Code as development tool
- Exit Criteria: All unit tests pass, integration tests pass, deployment to local K8s succeeds, 24-hour test survived
- Artifacts: `production/` folder with complete implementation

**Production Deployment (Hours 41-48+):**
- Input: Complete specialized system
- Output: Deployed, monitored, 24/7-operational Digital FTE
- Method: Gradual rollout with monitoring, validation gates at each stage
- Validation: 24-hour continuous operation test (100+ web submissions, 50+ emails, 50+ WhatsApp, chaos testing)

**Rationale:** The Agent Maturity Model is the core framework distinguishing AI prototypes from production Digital FTEs. Enforcing stages prevents "premature optimization" (building infrastructure before understanding requirements) and "feature creep" during incubation (adding production concerns before discovery completes).

### III. 24/7 Operational Excellence

The Digital FTE MUST operate continuously without human intervention for 24+ hours. System design MUST assume failures WILL occur and handle them gracefully. No single point of failure IS acceptable.

**Rules:**
- Pod restarts ARE expected: State persists in PostgreSQL, conversations resume from last message
- Horizontal scaling IS required: Multiple API and worker pods MUST run concurrently (Kubernetes HPA configured)
- Dead letter queue (DLQ) IS mandatory: Failed Kafka messages MUST be captured for human review
- Health checks MUST be implemented: `/health` endpoint returns status of all channels
- Response time SLA: P95 latency < 3 seconds (processing), < 30 seconds (delivery)
- Uptime target: > 99.9% (except during planned maintenance windows)
- Graceful degradation: If a channel fails (e.g., Gmail API down), other channels MUST continue operating

**Rationale:** Human FTEs work 40 hours/week with breaks, sick days, and vacations. Digital FTEs provide value through continuous operation. Operational excellence distinguishes a prototype from a production employee. Customers don't care about infrastructure - they care that their questions are answered at 3 AM on a Sunday.

### IV. Cross-Channel Conversation Continuity

Customer conversations MUST persist across channels, time, and agent instances. A customer who emails today, sends WhatsApp tomorrow, and uses the web form next week MUST see their complete history. Context switching IS a first-class feature.

**Rules:**
- Customer identification IS mandatory on EVERY inbound message (email address OR phone number)
- `customer_identifiers` table MUST be queried before creating new customers
- Conversation history retrieval (last 20 messages across ALL channels) MUST occur before agent generates response
- Channel switches MUST be logged in `conversations` table with metadata
- Agent MUST acknowledge previous interactions: "I see you contacted us about X last week via email. How can I help further?"
- Response generation MUST use conversation context from `messages` table, not just current message

**Rationale:** The #1 customer frustration with automated support is repeating themselves. Cross-channel continuity is technically challenging (unifying email, phone, and web identities) but provides disproportionate business value. This capability separates basic bots from true Digital FTEs.

### V. Test-Driven Reliability (NON-NEGOTIABLE)

Red-Green-Refactor cycle IS strictly enforced for ALL production code. Tests MUST be written BEFORE implementation. NO feature is considered complete without passing tests. Edge cases discovered during incubation MUST have test cases.

**Rules:**
- Integration tests (E2E multi-channel) MUST be written first and FAIL before implementing any user story
- Edge cases from `specs/discovery-log.md` MUST become test cases (minimum 10 per channel)
- Channel-specific response length tests ARE mandatory: Verify email responses are detailed, WhatsApp responses are concise
- Escalation logic tests ARE mandatory: Pricing, refund, legal, and angry customers MUST trigger escalation
- Load tests (Locust) MUST pass before production deployment: 100+ concurrent users across all channels
- Chaos tests (random pod kills) MUST pass: System survives losing 1 of 3 API pods and 1 of 3 worker pods

**Rationale:** AI agents have non-deterministic outputs (LLM responses vary). Testing is the ONLY guarantee of consistent behavior. Writing tests first ensures developers think about edge cases before implementation. Load and chaos tests validate 24/7 readiness.

### VI. Data Privacy & Security

Customer data MUST be protected according to industry best practices. No secrets, credentials, or sensitive customer information in code or repositories. ALL credentials stored in environment variables or Kubernetes Secrets.

**Rules:**
- `.env` files NEVER committed to Git (in `.gitignore`)
- Secrets stored in Kubernetes Secrets (`k8s/secrets.yaml`) with environment variable injection
- Customer emails, phone numbers, and conversation history stored securely in PostgreSQL (encrypted at rest)
- No customer PII in logs: Redact email/phone before logging, use customer_id instead
- Webhook signature validation IS mandatory for Gmail and WhatsApp (prevent spoofing)
- Input sanitization on ALL inbound messages (prevent injection attacks)
- No hardcoded API keys, tokens, or credentials in ANY file

**Rationale:** Customer support involves sensitive data (email addresses, phone numbers, product questions, sometimes account issues). A data breach or security incident destroys trust immediately. Security practices must be habits, not afterthoughts.

### VII. Observability & Metrics

Digital FTE behavior MUST be measurable at every level. "It seems to work" IS NOT acceptable. Metrics, logs, and alerts ARE required for confident operations.

**Required Metrics:**
- **Channel-level**: Response count, average latency, escalation rate, customer satisfaction (sentiment trend)
- **Agent-level**: Tool usage frequency, knowledge base hit rate, token usage per conversation, error rate
- **System-level**: Pod health, Kafka consumer lag, PostgreSQL connection pool utilization, API error rate (4xx/5xx)
- **Business-level**: Tickets resolved without human intervention, cross-channel identification success rate

**Logging Requirements:**
- Structured logs (JSON format) with: timestamp, customer_id (redacted if needed), conversation_id, channel, event_type
- Log levels: ERROR (escalations, failures), WARN (retries, edge cases), INFO (normal operations), DEBUG (detailed tracing)
- Centralized logging: Logs shipped to observability platform (e.g., Loki, ELK, CloudWatch)

**Alerting Thresholds:**
- Escalation rate > 25% (indicates agent struggling)
- P95 latency > 3 seconds for any channel (SLA breach)
- Pod crash loop > 3 times in 10 minutes (unhealthy deployment)
- Kafka consumer lag > 100 messages (processing backlog)

**Rationale:** You cannot improve what you cannot measure. Observability enables confident operations, rapid debugging, and continuous improvement. Alerts turn firefighting ("customer complained it's broken") into proactive response.

## Development Workflow

### Feature Development Process

1. **Incubation Discovery** (Claude Code-led exploration)
   - Provide context in `context/` folder (company profile, product docs, sample tickets)
   - Use Claude Code to explore requirements, build prototype, discover edge cases
   - Document discoveries in `specs/discovery-log.md`
   - Create crystallized spec in `specs/customer-success-fte-spec.md`

2. **Transition Planning**
   - Complete `specs/transition-checklist.md`: Extract working prompts, edge cases, tool definitions
   - Map prototype code to production structure
   - Create transition test suite (verify behavior matches incubation discoveries)

3. **Specialization Implementation**
   - Transform MCP tools to OpenAI SDK `@function_tool` with Pydantic validation
   - Implement channel handlers (Gmail, WhatsApp, Web Form)
   - Build PostgreSQL schema (customers, conversations, tickets, messages, knowledge_base)
   - Set up Kafka topics for event streaming
   - Create Kubernetes manifests (deployments, services, HPA)

4. **Integration Testing**
   - Run E2E tests for all channels
   - Execute load tests (Locust) with 100+ concurrent users
   - Perform chaos testing (random pod kills)
   - Validate 24-hour continuous operation

5. **Production Deployment**
   - Deploy to Kubernetes with gradual rollout (10% → 50% → 100%)
   - Monitor metrics and alerts at each stage
   - Validate response times, escalation rates, and customer satisfaction

### Code Review Gates

Every pull request MUST verify:
- ✅ Constitution compliance (multi-channel design, TDD, observability)
- ✅ Tests pass (unit, integration, load, chaos)
- ✅ No secrets committed (`.env` check, credential scan)
- ✅ Documentation updated (API docs, runbooks, architecture diagrams)
- ✅ Performance validated (P95 latency < 3s, memory < 1GB per pod)
- ✅ Security review (webhook validation, input sanitization, PII redaction)

### Amendment Process

This constitution governs ALL development practices. Amendments require:
1. Documented rationale in ADR (Architecture Decision Record)
2. Approval from project lead
3. Migration plan for existing code/infrastructure
4. Update to this constitution with version bump (MAJOR.MINOR.PATCH)

## Technology Stack Constraints

**Required Technologies:**
- **Agent Framework**: OpenAI Agents SDK (production), MCP (incubation)
- **Backend**: Python 3.11+, FastAPI, uvicorn
- **Database**: PostgreSQL 16 with pgvector extension (serves as CRM)
- **Streaming**: Apache Kafka (Confluent Cloud recommended)
- **Orchestration**: Kubernetes (minikube local, any cloud for production)
- **Email**: Gmail API with Pub/Sub push notifications
- **Messaging**: Twilio WhatsApp API (Sandbox for development)
- **Web Form**: React/Next.js component (standalone, embeddable)

**Technology Bans:**
- ❌ External CRM integration (Salesforce, HubSpot) - PostgreSQL IS your CRM
- ❌ Full website development - Only support form component required
- ❌ Synchronous API calls in agent workers - All I/O MUST be async
- ❌ Direct database access from frontend - All access via FastAPI endpoints

## Success Criteria

A Digital FTE is considered production-ready when:
1. **Multi-Channel Support**: All three channels (Email, WhatsApp, Web) operational with equal quality
2. **Cross-Channel Continuity**: > 95% of customers identified correctly across channels
3. **24/7 Operation**: Survives 24-hour continuous test with 100+ web submissions, 50+ emails, 50+ WhatsApp messages
4. **Operational Excellence**: P95 latency < 3s, uptime > 99.9%, escalation rate < 25%
5. **Chaos Tolerance**: System survives random pod restarts and single channel failures
6. **Cost Efficiency**: Operating cost < $1,000/year (vs $75,000/year human FTE)
7. **Test Coverage**: All edge cases from incubation have tests, load/chaos tests pass

**Version**: 1.0.0 | **Ratified**: 2025-02-12 | **Last Amended**: 2025-02-12
