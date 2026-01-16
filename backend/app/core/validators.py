"""
Input Validators for Lion Delivery Bot.
Centralized validation functions for all user inputs.
"""
import re
from typing import Optional, Tuple
from app.core.constants import (
    PHONE_REGEX, MIN_QUANTITY, MAX_QUANTITY,
    MIN_PRICE, MAX_PRICE, MIN_ADDRESS_LENGTH, MAX_ADDRESS_LENGTH,
    LAT_MIN, LAT_MAX, LNG_MIN, LNG_MAX
)
from app.core.exceptions import (
    InvalidPhoneNumberError, InvalidQuantityError, InvalidPriceError,
    InvalidCoordinatesError, InvalidAddressError, ValidationError
)


def validate_phone_number(phone: str, raise_error: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format.
    Returns (is_valid, normalized_phone)
    """
    if not phone:
        if raise_error:
            raise InvalidPhoneNumberError("")
        return (False, None)

    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)

    # Check format
    if not re.match(PHONE_REGEX, cleaned):
        if raise_error:
            raise InvalidPhoneNumberError(phone)
        return (False, None)

    # Normalize to international format
    if cleaned.startswith('0'):
        cleaned = '961' + cleaned[1:]
    elif not cleaned.startswith('961') and not cleaned.startswith('+961'):
        cleaned = '961' + cleaned

    # Remove + if present
    cleaned = cleaned.replace('+', '')

    return (True, cleaned)


def validate_quantity(quantity: int, raise_error: bool = True) -> bool:
    """Validate item quantity is within valid range"""
    try:
        qty = int(quantity)
        if qty < MIN_QUANTITY or qty > MAX_QUANTITY:
            if raise_error:
                raise InvalidQuantityError(qty, MIN_QUANTITY, MAX_QUANTITY)
            return False
        return True
    except (ValueError, TypeError):
        if raise_error:
            raise InvalidQuantityError(quantity, MIN_QUANTITY, MAX_QUANTITY)
        return False


def validate_price(price: float, raise_error: bool = True) -> bool:
    """Validate price is positive and within valid range"""
    try:
        p = float(price) if price is not None else 0
        if p < MIN_PRICE or p > MAX_PRICE:
            if raise_error:
                raise InvalidPriceError(p)
            return False
        return True
    except (ValueError, TypeError):
        if raise_error:
            raise InvalidPriceError(price)
        return False


def validate_coordinates(
    lat: Optional[float],
    lng: Optional[float],
    raise_error: bool = True,
    strict: bool = False
) -> bool:
    """
    Validate GPS coordinates.
    If strict=True, validates that coordinates are within Lebanon bounds.
    """
    # None is allowed (text address instead of coordinates)
    if lat is None and lng is None:
        return True

    # Both must be provided
    if lat is None or lng is None:
        if raise_error:
            raise InvalidCoordinatesError(lat or 0, lng or 0)
        return False

    try:
        lat_f = float(lat)
        lng_f = float(lng)

        # Basic range check
        if lat_f < -90 or lat_f > 90 or lng_f < -180 or lng_f > 180:
            if raise_error:
                raise InvalidCoordinatesError(lat_f, lng_f)
            return False

        # Strict Lebanon bounds check
        if strict:
            if lat_f < LAT_MIN or lat_f > LAT_MAX or lng_f < LNG_MIN or lng_f > LNG_MAX:
                if raise_error:
                    raise InvalidCoordinatesError(lat_f, lng_f)
                return False

        return True

    except (ValueError, TypeError):
        if raise_error:
            raise InvalidCoordinatesError(lat, lng)
        return False


def validate_address(address: str, raise_error: bool = True) -> bool:
    """Validate delivery address"""
    if not address:
        if raise_error:
            raise InvalidAddressError("", "Address is required")
        return False

    address = address.strip()

    if len(address) < MIN_ADDRESS_LENGTH:
        if raise_error:
            raise InvalidAddressError(address, f"Address too short (min {MIN_ADDRESS_LENGTH} characters)")
        return False

    if len(address) > MAX_ADDRESS_LENGTH:
        if raise_error:
            raise InvalidAddressError(address, f"Address too long (max {MAX_ADDRESS_LENGTH} characters)")
        return False

    return True


def validate_email(email: str, raise_error: bool = True) -> bool:
    """Validate email format"""
    if not email:
        return True  # Email is optional

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        if raise_error:
            raise ValidationError(f"Invalid email format: {email}", "email", email)
        return False

    return True


def validate_name(name: str, raise_error: bool = True) -> bool:
    """Validate customer name"""
    if not name:
        if raise_error:
            raise ValidationError("Name is required", "name")
        return False

    name = name.strip()

    if len(name) < 2:
        if raise_error:
            raise ValidationError("Name too short (min 2 characters)", "name", name)
        return False

    if len(name) > 100:
        if raise_error:
            raise ValidationError("Name too long (max 100 characters)", "name", name)
        return False

    return True


def validate_rating(rating: int, raise_error: bool = True) -> bool:
    """Validate review rating (1-5)"""
    try:
        r = int(rating)
        if r < 1 or r > 5:
            if raise_error:
                raise ValidationError("Rating must be between 1 and 5", "rating", r)
            return False
        return True
    except (ValueError, TypeError):
        if raise_error:
            raise ValidationError("Invalid rating", "rating", rating)
        return False


def validate_order_status(current: str, new: str, raise_error: bool = True) -> bool:
    """Validate order status transition is valid"""
    valid_transitions = {
        "new": ["confirmed", "cancelled"],
        "confirmed": ["preparing", "cancelled"],
        "preparing": ["ready", "cancelled"],
        "ready": ["on_the_way", "cancelled"],
        "on_the_way": ["delivered", "cancelled"],
        "delivered": [],  # Final state
        "cancelled": []   # Final state
    }

    current_lower = current.lower()
    new_lower = new.lower()

    if current_lower not in valid_transitions:
        if raise_error:
            raise ValidationError(f"Invalid current status: {current}", "status", current)
        return False

    if new_lower not in valid_transitions[current_lower]:
        if raise_error:
            from app.core.exceptions import InvalidOrderStatusError
            raise InvalidOrderStatusError(current, new)
        return False

    return True


def validate_restaurant_id(restaurant_id: int, raise_error: bool = True) -> bool:
    """Validate restaurant ID is a positive integer"""
    try:
        rid = int(restaurant_id)
        if rid <= 0:
            if raise_error:
                raise ValidationError("Invalid restaurant ID", "restaurant_id", rid)
            return False
        return True
    except (ValueError, TypeError):
        if raise_error:
            raise ValidationError("Invalid restaurant ID", "restaurant_id", restaurant_id)
        return False


def validate_menu_item_id(item_id: int, raise_error: bool = True) -> bool:
    """Validate menu item ID is a positive integer"""
    try:
        iid = int(item_id)
        if iid <= 0:
            if raise_error:
                raise ValidationError("Invalid item ID", "item_id", iid)
            return False
        return True
    except (ValueError, TypeError):
        if raise_error:
            raise ValidationError("Invalid item ID", "item_id", item_id)
        return False


def sanitize_text(text: str, max_length: int = 500) -> str:
    """Sanitize text input by removing dangerous characters"""
    if not text:
        return ""

    # Remove null bytes
    text = text.replace('\x00', '')

    # Strip whitespace
    text = text.strip()

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    return text


def sanitize_phone_for_log(phone: str) -> str:
    """Mask phone number for logging (privacy)"""
    if not phone or len(phone) < 6:
        return "***"
    return phone[:3] + "****" + phone[-3:]


def sanitize_html(text: str) -> str:
    """
    Sanitize text to prevent XSS attacks.
    Escapes HTML special characters.
    """
    if not text:
        return ""

    # HTML escape characters
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }

    return "".join(html_escape_table.get(c, c) for c in text)


def validate_password_strength(password: str, raise_error: bool = True) -> bool:
    """
    Validate password meets minimum security requirements.
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    if not password:
        if raise_error:
            raise ValidationError("Password is required", "password")
        return False

    if len(password) < 8:
        if raise_error:
            raise ValidationError("Password must be at least 8 characters", "password")
        return False

    if not re.search(r'[A-Z]', password):
        if raise_error:
            raise ValidationError("Password must contain at least one uppercase letter", "password")
        return False

    if not re.search(r'[a-z]', password):
        if raise_error:
            raise ValidationError("Password must contain at least one lowercase letter", "password")
        return False

    if not re.search(r'\d', password):
        if raise_error:
            raise ValidationError("Password must contain at least one digit", "password")
        return False

    return True


def validate_positive_integer(value: int, field_name: str = "value", raise_error: bool = True) -> bool:
    """Validate that value is a positive integer"""
    try:
        v = int(value)
        if v <= 0:
            if raise_error:
                raise ValidationError(f"{field_name} must be a positive integer", field_name, v)
            return False
        return True
    except (ValueError, TypeError):
        if raise_error:
            raise ValidationError(f"Invalid {field_name}", field_name, value)
        return False


def validate_non_negative(value: float, field_name: str = "value", raise_error: bool = True) -> bool:
    """Validate that value is zero or positive"""
    try:
        v = float(value)
        if v < 0:
            if raise_error:
                raise ValidationError(f"{field_name} cannot be negative", field_name, v)
            return False
        return True
    except (ValueError, TypeError):
        if raise_error:
            raise ValidationError(f"Invalid {field_name}", field_name, value)
        return False
