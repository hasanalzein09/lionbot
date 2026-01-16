from datetime import timedelta
from typing import Any
import logging
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.limiter import limiter, login_rate_limit
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, User as UserSchema
from app.services.audit_service import get_audit_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
@login_rate_limit()  # 5 attempts per minute - protects against brute force
async def login_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Rate limited to 5 attempts per minute to prevent brute force attacks.
    """
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)

    # We use username field for phone_number or email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    # Initialize audit service
    audit = get_audit_service(db)

    # Use constant-time comparison to prevent timing attacks
    if not user:
        # Still verify password to prevent timing-based user enumeration
        security.verify_password("dummy", "$2b$12$dummyhashtopreventtiming")
        logger.warning(f"Failed login attempt for unknown user: {form_data.username} from {client_ip}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not security.verify_password(form_data.password, user.hashed_password or ""):
        logger.warning(f"Failed login attempt (wrong password) for user: {form_data.username} from {client_ip}")
        # Log failed login attempt
        await audit.log_login(user=user, success=False, request=request)
        await db.commit()
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {form_data.username} from {client_ip}")
        raise HTTPException(status_code=400, detail="Inactive user")

    # Successful login - log it
    logger.info(f"Successful login for user: {form_data.username} from {client_ip}")
    await audit.log_login(user=user, success=True, request=request)
    await db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
