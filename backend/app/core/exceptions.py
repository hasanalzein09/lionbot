"""
Custom Exception Classes for Lion Delivery Bot.
Provides specific exception types for different error scenarios.

All exceptions inherit from LionBotException and provide:
- Consistent error codes
- Structured error details
- HTTP status code mapping
- Serialization to dict for API responses
"""
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class LionBotException(Exception):
    """Base exception for all Lion Bot errors"""

    # HTTP status code for this exception type
    http_status_code: int = 400

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize exception to API response format."""
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def log(self, level: int = logging.ERROR) -> None:
        """Log this exception with appropriate level."""
        logger.log(level, str(self), extra={"error_code": self.code, "details": self.details})


@contextmanager
def handle_exceptions(operation: str, reraise: bool = True):
    """
    Context manager for consistent exception handling.

    Usage:
        with handle_exceptions("creating order"):
            # code that might raise exceptions
            order = create_order(data)

    Args:
        operation: Description of the operation for logging
        reraise: Whether to reraise exceptions after logging
    """
    try:
        yield
    except LionBotException:
        # Already a custom exception, just reraise
        raise
    except Exception as e:
        logger.error(f"Error during {operation}: {e}", exc_info=True)
        if reraise:
            raise DatabaseError(message=f"Failed to {operation}") from e


# ==================== Database Exceptions ====================
class DatabaseError(LionBotException):
    """Database operation failed"""
    http_status_code = 500

    def __init__(self, message: str = "Database operation failed", details: Optional[Dict] = None):
        super().__init__(message, "DATABASE_ERROR", details)


class RecordNotFoundError(DatabaseError):
    """Requested record not found in database"""
    http_status_code = 404

    def __init__(self, entity: str, identifier: Any = None):
        message = f"{entity} not found"
        details = {"entity": entity}
        if identifier is not None:
            details["identifier"] = str(identifier)
        super().__init__(message, details)
        self.code = "RECORD_NOT_FOUND"


class DuplicateRecordError(DatabaseError):
    """Duplicate record already exists"""
    http_status_code = 409

    def __init__(self, message: str = "Record already exists", entity: str = None, field: str = None, value: Any = None):
        details = {}
        if entity:
            details["entity"] = entity
            message = f"{entity} already exists"
        if field and value is not None:
            details["field"] = field
            details["value"] = str(value)
            message = f"{entity or 'Record'} with {field}='{value}' already exists"
        super().__init__(message, details)
        self.code = "DUPLICATE_RECORD"


class ConnectionError(DatabaseError):
    """Database connection failed"""

    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message)
        self.code = "DB_CONNECTION_ERROR"


# ==================== Validation Exceptions ====================
class ValidationError(LionBotException):
    """Input validation failed"""
    http_status_code = 422

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, "VALIDATION_ERROR", details)


class InvalidPhoneNumberError(ValidationError):
    """Phone number format is invalid"""

    def __init__(self, phone: str):
        super().__init__(f"Invalid phone number format: {phone}", "phone_number", phone)
        self.code = "INVALID_PHONE_NUMBER"


class InvalidQuantityError(ValidationError):
    """Quantity is out of valid range"""

    def __init__(self, quantity: int, min_qty: int = 1, max_qty: int = 99):
        super().__init__(
            f"Quantity must be between {min_qty} and {max_qty}",
            "quantity",
            quantity
        )
        self.code = "INVALID_QUANTITY"


class InvalidPriceError(ValidationError):
    """Price is invalid or negative"""

    def __init__(self, price: float):
        super().__init__(f"Invalid price: {price}", "price", price)
        self.code = "INVALID_PRICE"


class InvalidCoordinatesError(ValidationError):
    """GPS coordinates are invalid"""

    def __init__(self, lat: float, lng: float):
        super().__init__(
            f"Invalid coordinates: lat={lat}, lng={lng}",
            "coordinates",
            f"{lat},{lng}"
        )
        self.code = "INVALID_COORDINATES"


class InvalidAddressError(ValidationError):
    """Address is invalid or too short/long"""

    def __init__(self, address: str, reason: str = "Invalid address"):
        super().__init__(reason, "address", address[:50])
        self.code = "INVALID_ADDRESS"


# ==================== Authentication Exceptions ====================
class AuthenticationError(LionBotException):
    """Authentication failed"""
    http_status_code = 401

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class InvalidCredentialsError(AuthenticationError):
    """Invalid username or password"""

    def __init__(self):
        super().__init__("Invalid credentials")
        self.code = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthenticationError):
    """JWT token has expired"""

    def __init__(self):
        super().__init__("Token has expired")
        self.code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthenticationError):
    """JWT token is invalid"""

    def __init__(self):
        super().__init__("Invalid token")
        self.code = "INVALID_TOKEN"


class InsufficientPermissionsError(AuthenticationError):
    """User doesn't have required permissions"""
    http_status_code = 403

    def __init__(self, required_role: str = None):
        message = "Insufficient permissions"
        if required_role:
            message = f"Requires {required_role} role"
        super().__init__(message)
        self.code = "INSUFFICIENT_PERMISSIONS"


# ==================== Rate Limiting Exceptions ====================
class RateLimitError(LionBotException):
    """Rate limit exceeded"""
    http_status_code = 429

    def __init__(self, action: str = "request", retry_after: int = 60):
        super().__init__(
            f"Rate limit exceeded for {action}. Try again in {retry_after} seconds.",
            "RATE_LIMIT_EXCEEDED",
            {"action": action, "retry_after": retry_after}
        )


# ==================== External Service Exceptions ====================
class ExternalServiceError(LionBotException):
    """External service call failed"""
    http_status_code = 503

    def __init__(self, service: str, message: str = "Service unavailable"):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", {"service": service})


class WhatsAppAPIError(ExternalServiceError):
    """WhatsApp API call failed"""

    def __init__(self, message: str = "WhatsApp API error", status_code: int = None):
        super().__init__("WhatsApp", message)
        self.code = "WHATSAPP_API_ERROR"
        if status_code:
            self.details["status_code"] = status_code


class AIServiceError(ExternalServiceError):
    """AI service (Gemini) call failed"""

    def __init__(self, message: str = "AI service error"):
        super().__init__("AI/Gemini", message)
        self.code = "AI_SERVICE_ERROR"


class RedisError(ExternalServiceError):
    """Redis operation failed"""

    def __init__(self, message: str = "Redis error", operation: str = None):
        super().__init__("Redis", message)
        self.code = "REDIS_ERROR"
        if operation:
            self.details["operation"] = operation


# ==================== Business Logic Exceptions ====================
class BusinessLogicError(LionBotException):
    """Business rule violation"""

    def __init__(self, message: str, code: str = "BUSINESS_ERROR"):
        super().__init__(message, code)


class CartEmptyError(BusinessLogicError):
    """Cart is empty when trying to checkout"""

    def __init__(self):
        super().__init__("Cart is empty", "CART_EMPTY")


class CartItemNotFoundError(BusinessLogicError):
    """Item not found in cart"""

    def __init__(self, item_id: int):
        super().__init__(f"Item {item_id} not in cart", "CART_ITEM_NOT_FOUND")
        self.details["item_id"] = item_id


class RestaurantClosedError(BusinessLogicError):
    """Restaurant is closed or inactive"""

    def __init__(self, restaurant_id: int):
        super().__init__("Restaurant is currently closed", "RESTAURANT_CLOSED")
        self.details["restaurant_id"] = restaurant_id


class ItemUnavailableError(BusinessLogicError):
    """Menu item is unavailable"""

    def __init__(self, item_id: int, item_name: str = None):
        message = f"Item {item_name or item_id} is currently unavailable"
        super().__init__(message, "ITEM_UNAVAILABLE")
        self.details["item_id"] = item_id


class OrderNotFoundError(BusinessLogicError):
    """Order not found"""

    def __init__(self, order_id: int):
        super().__init__(f"Order #{order_id} not found", "ORDER_NOT_FOUND")
        self.details["order_id"] = order_id


class InvalidOrderStatusError(BusinessLogicError):
    """Invalid order status transition"""

    def __init__(self, current_status: str, requested_status: str):
        super().__init__(
            f"Cannot change order status from {current_status} to {requested_status}",
            "INVALID_ORDER_STATUS"
        )
        self.details["current_status"] = current_status
        self.details["requested_status"] = requested_status


class InsufficientPointsError(BusinessLogicError):
    """Not enough loyalty points"""

    def __init__(self, required: int, available: int):
        super().__init__(
            f"Insufficient points. Required: {required}, Available: {available}",
            "INSUFFICIENT_POINTS"
        )
        self.details["required"] = required
        self.details["available"] = available


class MinimumOrderError(BusinessLogicError):
    """Order doesn't meet minimum amount"""

    def __init__(self, minimum: float, current: float):
        super().__init__(
            f"Minimum order amount is ${minimum:.2f}. Current: ${current:.2f}",
            "MINIMUM_ORDER_NOT_MET"
        )
        self.details["minimum"] = minimum
        self.details["current"] = current


# ==================== Webhook Exceptions ====================
class WebhookError(LionBotException):
    """Webhook processing error"""

    def __init__(self, message: str = "Webhook error"):
        super().__init__(message, "WEBHOOK_ERROR")


class WebhookSignatureError(WebhookError):
    """Webhook signature verification failed"""

    def __init__(self):
        super().__init__("Invalid webhook signature")
        self.code = "INVALID_WEBHOOK_SIGNATURE"


class WebhookPayloadError(WebhookError):
    """Webhook payload is malformed"""

    def __init__(self, reason: str = "Malformed payload"):
        super().__init__(reason)
        self.code = "INVALID_WEBHOOK_PAYLOAD"
