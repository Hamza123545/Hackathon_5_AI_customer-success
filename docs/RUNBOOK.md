# Customer Success FTE - Runbook & Incident Response

## Overview
This runbook provides procedures for handling common incidents and operational tasks for the Customer Success FTE system.

## Alerting & Metrics
- **Metrics Dashboard**: `http://localhost:8000/metrics` (or Grafana if configured)
- **Key Alerts**:
    - `API Error Rate > 5%`
    - `Kafka Consumer Lag > 100`
    - `Pod Restart Count > 5 per hour`
    - `Channel Circuit Breaker OPEN`

## Incident Procedures

### 1. High API Error Rate / Degradation
**Symptoms**: Users report errors, monitoring shows 5xx spikes.
**Actions**:
1. Check API logs: `kubectl logs -l app=fte-api -n fte-namespace`
2. Check Database connection: `kubectl logs -l app=postgres -n fte-namespace`
3. Restart API pods if stuck: `kubectl rollout restart deployment/fte-api -n fte-namespace`

### 2. Message Processing Stalled (Kafka Lag)
**Symptoms**: Support tickets not appearing, customers not getting replies.
**Actions**:
1. Check Consumer Lag metric.
2. Check Worker logs: `kubectl logs -l app=fte-message-processor -n fte-namespace`
3. Look for "Circuit Breaker OPEN" messages.
4. If stuck on a "poison pill" message, check DLQ (Dead Letter Queue).

### 3. Database Connection Failures
**Symptoms**: All services failing, frequent restarts.
**Actions**:
1. Check Postgres Pod status.
2. Verify credentials in Secrets.
3. Check PVC storage capacity.

### 4. Channel Failure (Gmail/Twilio/Web)
**Symptoms**: One specific channel not working.
**Actions**:
1. Check `GET /health` endpoint or metrics.
2. Verify external API status (e.g., is Gmail API down?).
3. Force reset circuit breaker (restart worker pods).

## Routine Maintenance

### Rotating Secrets
1. Update `backend/k8s/secrets.yaml`
2. Apply: `kubectl apply -f backend/k8s/secrets.yaml`
3. Restart pods to pick up new env vars.

### Scaling
Manually scale if HPA is insufficient:
```bash
kubectl scale deployment/fte-worker --replicas=5 -n fte-namespace
```

### Database Backup
```bash
kubectl exec -it <postgres-pod> -n fte-namespace -- pg_dump -U user fte_db > backup.sql
```
