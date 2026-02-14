import asyncio
import logging
import json
import time
from typing import Dict, Any
from database.queries import AgentMetricsRepository, get_db_pool
from workers.kafka_config import publish_event, TOPICS
from api.errors import gmail_circuit_breaker, twilio_circuit_breaker

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Background worker to collect and aggregate metrics.
    Collects system, agent, channel, and business metrics.
    """
    def __init__(self):
        self.running = False
        
    async def start(self):
        self.running = True
        pool = await get_db_pool()
        self.repo = AgentMetricsRepository(pool)
        
        logger.info("Metrics Collector started")
        
        while self.running:
            try:
                # 1. Channel Health (System Metrics)
                await self.collect_channel_health()
                
                # 2. Agent Metrics (Business/Performance)
                # In a real system, we'd query DB for counts/avgs in last minute
                # For now, we rely on what's pushed to agent_metrics table via API/Processor
                # But we can aggregate them here or just emit a heartbeat
                
                # 3. Kafka Consumer Lag (System)
                # Simulating check or using AdminClient
                # lag = await self.check_kafka_lag()
                # await self.publish_metric("kafka_lag", lag, {"topic": "fte.tickets.incoming"})
                
                await asyncio.sleep(60) # Run every minute
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        self.running = False

    async def collect_channel_health(self):
        """Checks circuit breaker states and publishes metrics."""
        health_status = {
            "gmail": "UP" if gmail_circuit_breaker.state == "CLOSED" else "DOWN",
            "twilio": "UP" if twilio_circuit_breaker.state == "CLOSED" else "DOWN",
            "web_form": "UP", # Always up unless API is down
            "timestamp": time.time()
        }
        
        # Log if any channel is down
        if health_status["gmail"] == "DOWN" or health_status["twilio"] == "DOWN":
            logger.warning(f"Channel Health Alert: {health_status}")
            
        # Publish health event
        await publish_event(TOPICS["metrics"], {
            "event_type": "channel_health",
            "metrics": health_status
        })
        
        # Publish distinct numeric metrics for dashboarding
        await self.publish_metric("channel_status", 1 if health_status["gmail"] == "UP" else 0, {"channel": "gmail"})
        await self.publish_metric("channel_status", 1 if health_status["twilio"] == "UP" else 0, {"channel": "twilio"})

    async def publish_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Helper to publish a single metric event"""
        event = {
            "event_type": "metric",
            "name": name,
            "value": value,
            "tags": tags or {},
            "timestamp": time.time()
        }
        await publish_event(TOPICS["metrics"], event)

if __name__ == "__main__":
    collector = MetricsCollector()
    asyncio.run(collector.start())
