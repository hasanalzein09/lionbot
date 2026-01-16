"""
Security utilities for authentication and password hashing.
Follows OWASP password security recommendations.
"""
from datetime import datetime, timedelta
from typing import Any, Union, Optional, Tuple
import re
import logging
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure bcrypt with secure rounds (12 is recommended minimum)
# Higher rounds = more secure but slower
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # OWASP recommended minimum
)

ALGORITHM = "HS256"

# Password strength requirements
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128  # Prevent DoS via very long passwords


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Create JWT access token with expiration."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[int]:
    """
    Verify JWT token and return user ID.
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash using constant-time comparison.
    Passlib's verify handles timing attack protection internally.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Invalid hash format or other errors
        return False


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt with configured rounds."""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.
    Returns (is_valid, error_message).

    Requirements:
    - At least 8 characters
    - At most 128 characters (prevent DoS)
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Not a common weak password
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"

    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password must not exceed {MAX_PASSWORD_LENGTH} characters"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    # Check against common weak passwords
    weak_passwords = [
        "password", "123456", "12345678", "qwerty", "admin",
        "welcome", "password1", "Password1", "letmein", "monkey",
        "dragon", "master", "111111", "abc123", "login",
    ]
    if password.lower() in weak_passwords:
        return False, "Password is too common. Please choose a stronger password"

    return True, ""


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if password hash needs to be updated to current settings.
    Useful when increasing bcrypt rounds over time.
    """
    return pwd_context.needs_update(hashed_password)
