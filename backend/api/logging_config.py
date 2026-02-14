import logging
import sys
import json
import os
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
        }

        # Add dictionary attributes from extra={}
        if hasattr(record, "customer_id"):
            log_entry["customer_id"] = record.customer_id # type: ignore
        if hasattr(record, "conversation_id"):
            log_entry["conversation_id"] = record.conversation_id # type: ignore
        if hasattr(record, "channel"):
            log_entry["channel"] = record.channel # type: ignore
        if hasattr(record, "event_type"):
            log_entry["event_type"] = record.event_type # type: ignore

        # Handle exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

def configure_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplication
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    
    root_logger.addHandler(handler)
    
    # Set external libraries logging to WARNING to reduce noise
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Initialize logging on import
configure_logging()
logger = logging.getLogger("fte.api")
