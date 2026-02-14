# Customer Success Digital FTE (Full-Time Employee) 🤖

## 🚀 Project Overview

The **Customer Success Digital FTE** is an advanced AI-driven support system designed to autonomously handle customer inquiries 24/7 across multiple communication channels. Built as the capstone project for **Panaversity Agent API Hackathon 5**, this system demonstrates the transition from a prototype AI agent to a production-grade, resilient, and scalable "AI Employee."

This project moves beyond simple chatbots by implementing a stateful, context-aware system that can:
-   **Remember** customers across different channels (Email, WhatsApp, Web).
-   **Reason** about complex queries using the **OpenAI Agents SDK** and **Gemini 1.5 Flash**.
-   **Act** on behalf of the user by creating tickets, searching knowledge bases, and escalating issues.
-   **Heal** itself from infrastructure failures using Kubernetes and Circuit Breakers.

## 💼 Business Value & Benefits

### The Problem
Running a 24/7 human customer support team is expensive and difficult to scale.
-   **High Costs**: Salaries, benefits, training, and management overhead (~$75k/year per agent).
-   **Slow Response Times**: Humans need sleep, breaks, and vacations.
-   **Inconsistency**: Different agents provide different answers.
-   **Data Silos**: Conversations are often lost when customers switch from email to chat.

### The Solution: AI Digital FTE
-   **Cost Efficiency**: Operates at a fraction of the cost of a human team (<$1k/year).
-   **24/7 Availability**: Instant responses at any time of day or night.
-   **Unified Context**: A "Single Customer View" that tracks interactions across Gmail, WhatsApp, and Web.
-   **Scalability**: Automatically handles traffic spikes (e.g., product launches) without hiring more staff.
-   **Consistency**: delivering accurate, policy-compliant answers drawn from a verified knowledge base.

## 🏗️ Technical Architecture

The system is built on a modern, event-driven microservices architecture:

### 1. Multi-Channel Intake Layer
-   **Gmail Integration**: Uses Google Pub/Sub push notifications for real-time email processing.
-   **WhatsApp Integration**: Uses Twilio Webhooks for instant messaging support.
-   **Web Form**: A custom Next.js frontend with a dedicated FastAPI endpoint.

### 2. Event Streaming & Decoupling
-   **Kafka**: All incoming messages are published to a Kafka topic (`fte.tickets.incoming`), decoupling ingestion from processing. This ensures no message is lost, even if the processing worker is down or overwhelmed.

### 3. The "Brain" (AI Agent)
-   **OpenAI Agents SDK**: Provides the framework for the agent's reasoning loop.
-   **Gemini 1.5 Flash**: The underlying Large Language Model (LLM) used for generating responses.
-   **Tools**: The agent is equipped with specific tools:
    -   `search_knowledge_base`: Semantic search via `pgvector`.
    -   `create_ticket`: Logs every interaction in the database.
    -   `get_customer_history`: Retrieves past conversations for context.
    -   `escalate_to_human`: Hands off complex or sensitive issues.

### 4. State & Knowledge Management
-   **PostgreSQL 16**: The central "CRM" database storing Customers, Conversations, Tickets, and Messages.
-   **pgvector**: An extension for storing and searching vector embeddings of the knowledge base.

### 5. Infrastructure & Resilience
-   **Kubernetes**: Orchestrates the application containers.
-   **Horizontal Pod Autoscaling (HPA)**: Automatically adds more API or Worker pods when CPU usage spikes.
-   **Circuit Breakers**: Protects the system from cascading failures if external APIs (Gmail/Twilio) go down.

## 🛠️ How It Works (The Flow)

1.  **Ingest**: A customer sends a message via Email, WhatsApp, or Web.
2.  **Normalize**: The Channel Handler validates the request and publishes a standardized event to Kafka.
3.  **Process**: The Async Worker consumes the event:
    -   Identifies the customer (linking email/phone to a single ID).
    -   Retrieves conversation history.
    -   Invokes the AI Agent.
4.  **Reason**: The Agent:
    -   Checks the Knowledge Base.
    -   Decides whether to answer or escalate.
    -   Formulates a response based on channel constraints (e.g., short for WhatsApp, formal for Email).
5.  **Respond**: The Worker sends the response back through the appropriate channel API.

## 📂 Repository Structure

```
Hackathon_5/
├── backend/                # The Core System
│   ├── agent/              # Agent Logic (Tools, Prompts, SDK)
│   ├── api/                # FastAPI Gateway (Webhooks, Frontend API)
│   ├── channels/           # Channel Adapters (Gmail, Twilio)
│   ├── database/           # PostgreSQL Schema & Queries
│   ├── k8s/                # Kubernetes Manifests (Deployment, HPA)
│   ├── workers/            # Kafka Consumers & Background Tasks
│   └── tests/              # Test Suite (Unit, E2E, Load)
├── frontend/               # User Interface
│   ├── src/components/     # React Components (SupportForm)
│   └── public/             # Static Assets
├── docs/                   # Documentation
│   ├── DEPLOYMENT_GUIDE.md # Production Deployment Instructions
│   ├── API_DOCUMENTATION.md# API Reference
│   ├── RUNBOOK.md          # Operational Runbook
│   └── TRANSITION_GUIDE.md # Development Journey
└── specs/                  # Project Requirements
```

## � Getting Started

### Prerequisites
-   Docker & Kubernetes (Docker Desktop or Minikube)
-   Python 3.11+
-   Node.js 18+
-   OpenAI API Key (or Google AI Studio Key for Gemini)

### Running Locally (Quick Start)

1.  **Backend Setup**:
    ```bash
    cd backend
    # Create .env from .env.example
    docker-compose up -d  # Starts Postgres, Kafka, Redis
    pip install -r requirements.txt
    python -m uvicorn api.main:app --reload
    ```

2.  **Frontend Setup**:
    ```bash
    cd frontend
    # Create .env.local from .env.example
    npm install
    npm run dev
    ```

3.  **Verify**:
    Open `http://localhost:3000` to see the Support Form.

### Deployment
Refer to [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed Kubernetes deployment steps.

## 🧪 Testing & Validation
-   Run unit tests: `pytest`
-   Run the 24-hour resilience simulation: `python backend/tests/e2e/test_24_hour_operation.py`

## 📜 License
This project is licensed under the MIT License. Created for educational purposes.
