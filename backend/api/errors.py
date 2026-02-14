import asyncio
import logging
from typing import Callable, Any, Type
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# --- Custom Exceptions ---

class FTEException(Exception):
    """Base exception for the application"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class DatabaseConnectionError(FTEException):
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message, "DB_CONNECTION_ERROR")

class KafkaPublishError(FTEException):
    def __init__(self, message: str = "Failed to publish event to Kafka"):
        super().__init__(message, "KAFKA_PUBLISH_ERROR")

class WebhookValidationError(FTEException):
    def __init__(self, message: str = "Webhook signature validation failed"):
        super().__init__(message, "WEBHOOK_VALIDATION_ERROR")

class ExternalAPIError(FTEException):
    def __init__(self, service: str, message: str):
        super().__init__(f"{service} API Error: {message}", f"{service.upper()}_API_ERROR")

class RateLimitExceeded(FTEException):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s", "RATE_LIMIT_EXCEEDED")

# --- Circuit Breaker ---

class CircuitBreakerOpen(FTEException):
    def __init__(self, service: str, remote_exception: Exception):
        super().__init__(f"Circuit breaker open for {service}", "CIRCUIT_BREAKER_OPEN")
        self.remote_exception = remote_exception

class CircuitBreaker:
    def __init__(self, service_name: str, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exceptions: tuple = (Exception,)):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions
        
        self.failure_count = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = None

    async def call(self, f: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if (datetime.now() - self.last_failure_time).total_seconds() > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info(f"Circuit {self.service_name} switching to HALF_OPEN")
            else:
                raise CircuitBreakerOpen(self.service_name, Exception("Circuit is OPEN"))
        
        try:
            result = await f(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info(f"Circuit {self.service_name} recovered. Switching to CLOSED")
            return result
        except self.expected_exceptions as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            logger.warning(f"Circuit {self.service_name} failure {self.failure_count}/{self.failure_threshold}: {e}")
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit {self.service_name} OPENED due to failures")
            
            raise ExternalAPIError(self.service_name, str(e))
