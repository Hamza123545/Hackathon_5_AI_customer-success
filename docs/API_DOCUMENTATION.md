# Customer Success FTE - API Documentation

## Base URL
Development: `http://localhost:8000`
Production: `https://support-api.yourdomain.com`

## Authentication
Most endpoints are public or secured via channel-specific signatures (Gmail, Twilio). 
Internal management endpoints may require API Key (future).

## Endpoints

### 1. Webhooks (Channel Ingestion)

#### `POST /webhooks/gmail`
Receives push notifications from Gmail API Pub/Sub.
- **Headers**: `X-Goog-Signature`
- **Body**: JSON payload with `message.data` (base64 encoded)
- **Response**: `200 OK`

#### `POST /webhooks/whatsapp`
Receives webhook events from Twilio.
- **Headers**: `X-Twilio-Signature`
- **Body**: Form Data (`From`, `Body`, `ProfileName`)
- **Response**: `200 OK` (Empty TwiML)

### 2. Frontend Support Form

#### `POST /support/submit`
Submits a new support ticket from the web form.
- **Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Login Issue",
  "message": "I cannot login to my account...",
  "category": "technical"
}
```
- **Response**:
```json
{
  "ticket_id": "uuid-string",
  "status": "received"
}
```

#### `GET /support/ticket/{ticket_id}`
Retrieves the status and message history of a ticket.
- **Response**:
```json
{
  "id": "uuid-string",
  "status": "open",
  "messages": [
    {"role": "customer", "content": "Help me...", "created_at": "2023-10-27T10:00:00Z"},
    {"role": "agent", "content": "Hello John...", "created_at": "2023-10-27T10:00:05Z"}
  ]
}
```

### 3. Management & Insights

#### `GET /conversations/{conversation_id}`
Retrieves full conversation history.

#### `GET /customers/lookup?email=...&phone=...`
Looks up a customer by email or phone. Returns linked IDs.

#### `GET /metrics/channels`
Returns aggregated metrics per channel.
```json
{
  "gmail": {"count": 120, "avg_latency": 2500},
  "whatsapp": {"count": 450, "avg_latency": 1200}
}
```

#### `GET /health`
Health check endpoint for Kubernetes probes.
- **Response**: `{"status": "ok", "db": "connected", "kafka": "connected"}`
