from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import uuid

from api.logging_config import configure_logging
from api.errors import FTEException, DatabaseConnectionError

# Configure logging
configure_logging()
logger = logging.getLogger("fte.api.main")

app = FastAPI(title="Customer Success Digital FTE", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
    )

@app.exception_handler(FTEException)
async def fte_exception_handler(request: Request, exc: FTEException):
    logger.error(f"FTE Exception: {exc.message} ({exc.code})")
    status_code = 500
    if isinstance(exc, DatabaseConnectionError):
        status_code = 503
    
    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "message": exc.message},
    )

# Middleware for structured logging (correlation ID, latency)
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Add correlation ID to logs via context var if using structured logging context
    # For simplicity here, we'll just log it
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(process_time, 2),
            "request_id": request_id
        }
    )
    
    return response

@app.get("/health")
async def health_check():
    return {"status": "ok"}
