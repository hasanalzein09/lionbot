"""
Standardized API response utilities.
Provides consistent response structure across all endpoints.
"""
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel
from fastapi.responses import JSONResponse


T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response structure.

    Success response:
    {
        "success": true,
        "data": {...},
        "meta": {...}  // optional pagination info
    }

    Error response:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": {}  // optional
        }
    }
    """
    success: bool = True
    data: Optional[T] = None
    meta: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""
    page: int = 1
    per_page: int = 20
    total: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200
) -> JSONResponse:
    """
    Create a standardized success response.

    Args:
        data: Response data (dict, list, or any serializable object)
        message: Optional success message
        meta: Optional metadata (pagination, etc.)
        status_code: HTTP status code (default 200)

    Returns:
        JSONResponse with standardized structure
    """
    content = {"success": True}

    if data is not None:
        content["data"] = data

    if message:
        content["message"] = message

    if meta:
        content["meta"] = meta

    return JSONResponse(content=content, status_code=status_code)


def created_response(
    data: Any = None,
    message: str = "Resource created successfully"
) -> JSONResponse:
    """Create a 201 Created response."""
    return success_response(data=data, message=message, status_code=201)


def no_content_response() -> JSONResponse:
    """Create a 204 No Content response."""
    return JSONResponse(content=None, status_code=204)


def error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        code: Error code (e.g., "VALIDATION_ERROR")
        message: Human-readable error message
        details: Optional error details
        status_code: HTTP status code (default 400)

    Returns:
        JSONResponse with standardized error structure
    """
    content = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }

    if details:
        content["error"]["details"] = details

    return JSONResponse(content=content, status_code=status_code)


def paginated_response(
    items: List[Any],
    total: int,
    page: int = 1,
    per_page: int = 20
) -> JSONResponse:
    """
    Create a paginated list response.

    Args:
        items: List of items for current page
        total: Total number of items across all pages
        page: Current page number (1-indexed)
        per_page: Items per page

    Returns:
        JSONResponse with data and pagination metadata
    """
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    meta = {
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

    return success_response(data=items, meta=meta)


# Common error responses
def not_found_response(entity: str, identifier: Any = None) -> JSONResponse:
    """Return a 404 Not Found response."""
    message = f"{entity} not found"
    details = {"entity": entity}
    if identifier is not None:
        details["identifier"] = str(identifier)
    return error_response("NOT_FOUND", message, details, 404)


def validation_error_response(message: str, field: str = None) -> JSONResponse:
    """Return a 422 Validation Error response."""
    details = {"field": field} if field else None
    return error_response("VALIDATION_ERROR", message, details, 422)


def unauthorized_response(message: str = "Authentication required") -> JSONResponse:
    """Return a 401 Unauthorized response."""
    return error_response("UNAUTHORIZED", message, status_code=401)


def forbidden_response(message: str = "Access denied") -> JSONResponse:
    """Return a 403 Forbidden response."""
    return error_response("FORBIDDEN", message, status_code=403)


def rate_limit_response(retry_after: int = 60) -> JSONResponse:
    """Return a 429 Rate Limit response."""
    return error_response(
        "RATE_LIMIT_EXCEEDED",
        f"Too many requests. Please try again in {retry_after} seconds.",
        {"retry_after": retry_after},
        429
    )


def server_error_response(message: str = "An unexpected error occurred") -> JSONResponse:
    """Return a 500 Internal Server Error response."""
    return error_response("INTERNAL_ERROR", message, status_code=500)


def service_unavailable_response(service: str) -> JSONResponse:
    """Return a 503 Service Unavailable response."""
    return error_response(
        "SERVICE_UNAVAILABLE",
        f"{service} is currently unavailable",
        {"service": service},
        503
    )
