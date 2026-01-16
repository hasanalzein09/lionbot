"""
Security middleware for FastAPI.
Adds security headers and protections to all responses.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    Follows OWASP security header recommendations.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS filter (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(self), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )

        # Content Security Policy for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"

        # Cache control for sensitive endpoints
        if any(path in request.url.path for path in ["/login", "/token", "/auth"]):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"

        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate incoming requests.
    Blocks suspicious or malformed requests.
    """

    # Maximum allowed content length (10MB)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    # Blocked user agents (common attack tools)
    BLOCKED_USER_AGENTS = [
        "sqlmap",
        "nikto",
        "nessus",
        "havij",
        "acunetix",
    ]

    async def dispatch(self, request: Request, call_next) -> Response:
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_CONTENT_LENGTH:
            logger.warning(f"Request too large from {request.client.host}: {content_length} bytes")
            return Response(
                content='{"detail": "Request too large"}',
                status_code=413,
                media_type="application/json",
            )

        # Check for blocked user agents (in production)
        user_agent = request.headers.get("user-agent", "").lower()
        for blocked in self.BLOCKED_USER_AGENTS:
            if blocked in user_agent:
                logger.warning(f"Blocked user agent: {user_agent} from {request.client.host}")
                return Response(
                    content='{"detail": "Access denied"}',
                    status_code=403,
                    media_type="application/json",
                )

        return await call_next(request)


class SQLInjectionProtectionMiddleware(BaseHTTPMiddleware):
    """
    Basic SQL injection pattern detection in query parameters.
    Note: This is a defense-in-depth measure. Parameterized queries are the primary protection.
    """

    SQL_PATTERNS = [
        "union select",
        "' or '1'='1",
        "'; drop table",
        "1=1--",
        "or 1=1",
        "' or ''='",
        "exec(",
        "execute(",
    ]

    async def dispatch(self, request: Request, call_next) -> Response:
        # Check query parameters
        query_string = str(request.query_params).lower()

        for pattern in self.SQL_PATTERNS:
            if pattern in query_string:
                logger.warning(
                    f"Potential SQL injection detected from {request.client.host}: {pattern}"
                )
                return Response(
                    content='{"detail": "Invalid request"}',
                    status_code=400,
                    media_type="application/json",
                )

        return await call_next(request)
