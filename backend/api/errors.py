import asyncio
import logging
from typing import Callable, Any, Type, Optional
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
    def __init__(self, service: str, next_try_in: float):
        self.service = service
        self.next_try_in = next_try_in
        super().__init__(f"Circuit breaker open for {service}. Retry in {next_try_in:.1f}s", "CIRCUIT_BREAKER_OPEN")

class CircuitBreaker:
    def __init__(self, service_name: str, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exceptions: tuple = (Exception,)):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions
        
        self.failure_count = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time: Optional[datetime] = None

    async def call(self, func: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if self.last_failure_time and (datetime.now() - self.last_failure_time).total_seconds() > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info(f"Circuit {self.service_name} switching to HALF_OPEN (probing)")
            else:
                retry_in = self.recovery_timeout - (datetime.now() - self.last_failure_time).total_seconds()
                raise CircuitBreakerOpen(self.service_name, max(0.1, retry_in))
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info(f"Circuit {self.service_name} recovered. Switching to CLOSED")
            elif self.state == "CLOSED":
                self.failure_count = 0 # Reset on success for consecutive failure counting
                
            return result
            
        except self.expected_exceptions as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            logger.warning(f"Circuit {self.service_name} failure {self.failure_count}/{self.failure_threshold}: {str(e)}")
            
            if self.state == "HALF_OPEN" or self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit {self.service_name} OPENED due to failures")
            
            raise ExternalAPIError(self.service_name, str(e))

# Shared Circuit Breaker Instances
# These should be imported and used by channel handlers
gmail_circuit_breaker = CircuitBreaker("Gmail", failure_threshold=3, recovery_timeout=60)
twilio_circuit_breaker = CircuitBreaker("Twilio", failure_threshold=3, recovery_timeout=60)
