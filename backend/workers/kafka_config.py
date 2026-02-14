import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)

# Topic Definitions
TOPICS = {
    "tickets_incoming": "fte.tickets.incoming",
    "escalations": "fte.escalations",
    "metrics": "fte.metrics",
    "dlq": "fte.dlq",
    # Channel specific topics can be added as needed
    "email_outbound": "fte.channels.email.outbound",
    "whatsapp_outbound": "fte.channels.whatsapp.outbound",
}

class KafkaProducerManager:
    _producer: Optional[AIOKafkaProducer] = None

    @classmethod
    async def get_producer(cls) -> AIOKafkaProducer:
        if cls._producer is None:
            bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
            cls._producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                enable_idempotence=True,  # Ensure exactly-once semantics where possible
                acks="all",  # Wait for all replicas to acknowledge
                retry_backoff_ms=500,
                request_timeout_ms=20000,
            )
            await cls._producer.start()
            logger.info(f"Kafka Producer started on {bootstrap_servers}")
        return cls._producer

    @classmethod
    async def stop_producer(cls):
        if cls._producer:
            await cls._producer.stop()
            cls._producer = None
            logger.info("Kafka Producer stopped")

class KafkaConsumerManager:
    _consumers: Dict[str, AIOKafkaConsumer] = {}

    @classmethod
    async def create_consumer(cls, topic: str, group_id: str, auto_offset_reset: str = "earliest") -> AIOKafkaConsumer:
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            enable_auto_commit=False,  # We will commit manually after processing
            auto_offset_reset=auto_offset_reset,
        )
        await consumer.start()
        logger.info(f"Kafka Consumer started for topic {topic} in group {group_id}")
        return consumer

    @classmethod
    async def stop_consumer(cls, consumer: AIOKafkaConsumer):
        await consumer.stop()
        logger.info("Kafka Consumer stopped")

async def publish_event(topic: str, event: Dict[str, Any], max_retries: int = 3):
    """
    Publish an event to a Kafka topic with retries.
    """
    producer = await KafkaProducerManager.get_producer()
    retries = 0
    while retries < max_retries:
        try:
            await producer.send_and_wait(topic, event)
            logger.debug(f"Event published to {topic}: {event.get('event_type', 'unknown')}")
            return
        except KafkaError as e:
            retries += 1
            logger.warning(f"Failed to publish event to {topic} (attempt {retries}/{max_retries}): {e}")
            await asyncio.sleep(2 ** retries)  # Exponential backoff
    
    # If retries exhausted, log error and potentially send to DLQ (if this wasn't already a DLQ attempt)
    logger.error(f"Failed to publish event to {topic} after {max_retries} attempts.")
    if topic != TOPICS["dlq"]:
        # Try to send to DLQ as a last resort
        try:
            dlq_event = {
                "original_topic": topic,
                "original_event": event,
                "error": "Publish failed after retries"
            }
            await producer.send_and_wait(TOPICS["dlq"], dlq_event)
            logger.info(f"Event sent to DLQ: {topic}")
        except Exception as dlq_error:
            logger.critical(f"Failed to send to DLQ: {dlq_error}")
