"""
Rate limiting configuration with Redis support for distributed environments.
Uses in-memory storage as fallback when Redis is unavailable.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Get client IP with proxy support.
    Checks X-Forwarded-For header for clients behind proxies/load balancers.
    """
    # Check for X-Forwarded-For header (set by proxies)
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # Take the first IP (original client)
        return x_forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header (used by nginx)
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip

    # Fall back to direct client IP
    return get_remote_address(request)


def get_limiter_storage():
    """
    Get appropriate storage backend for rate limiting.
    Uses Redis in production, memory storage for development.
    """
    try:
        from app.core.config import settings
        if settings.UPSTASH_REDIS_REST_URL:
            # Use Upstash for serverless
            return f"redis+upstash://{settings.UPSTASH_REDIS_REST_URL}"
        elif settings.REDIS_URL:
            return settings.REDIS_URL
        elif settings.REDIS_HOST:
            return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    except Exception as e:
        logger.warning(f"Failed to configure Redis for rate limiting: {e}")

    # Fall back to in-memory storage
    logger.info("Using in-memory storage for rate limiting")
    return "memory://"


# Create limiter with proper storage
limiter = Limiter(
    key_func=get_client_ip,
    storage_uri=get_limiter_storage(),
    default_limits=["100/minute"],
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    logger.warning(
        f"Rate limit exceeded for {get_client_ip(request)} on {request.url.path}"
    )
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please slow down.",
            "retry_after": exc.detail.split("per")[0].strip() if exc.detail else "1 minute",
        },
        headers={"Retry-After": "60"},
    )


# Rate limit decorators for common patterns
def login_rate_limit():
    """Stricter rate limit for login endpoints (5 per minute)."""
    return limiter.limit("5/minute")


def api_rate_limit():
    """Standard rate limit for API endpoints (60 per minute)."""
    return limiter.limit("60/minute")


def webhook_rate_limit():
    """Higher rate limit for webhook endpoints (200 per minute)."""
    return limiter.limit("200/minute")
