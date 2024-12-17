# src/utils/logging.py

import structlog
import logging
import sys
from typing import Optional

def setup_logging(log_level: Optional[str] = None) -> None:
    """Configure structured logging for the application"""
    
    # Set log level
    level = getattr(logging, log_level or "INFO")
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = __name__):
    """Get a structured logger instance"""
    return structlog.get_logger(name)

class RequestContextMiddleware:
    """Middleware to add request context to logs"""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("request")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Extract request info
        method = scope.get("method", "")
        path = scope.get("path", "")
        
        # Bind context
        with structlog.contextvars.bound_contextvars(
            http_method=method,
            path=path,
            request_id=scope.get("headers", {}).get("x-request-id", [""])[0].decode()
        ):
            try:
                response = await self.app(scope, receive, send)
                return response
            except Exception as e:
                self.logger.error(
                    "request_error",
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise