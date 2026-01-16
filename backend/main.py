from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from contextlib import asynccontextmanager

# Initialize structured logging before other imports
from app.core.logging_config import setup_logging, get_logger
setup_logging()

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base_class import Base
from app.core.exceptions import (
    LionBotException, ValidationError, AuthenticationError,
    RateLimitError, RecordNotFoundError, DatabaseError, ExternalServiceError
)

logger = get_logger(__name__)

# Import all models to register them with Base
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant, Branch
from app.models.menu import Menu, Category, MenuItem
from app.models.order import Order, OrderStatus, OrderItem
from app.models.settings import SystemSettings
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from sqlalchemy import select, text
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.core.limiter import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.security_middleware import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    SQLInjectionProtectionMiddleware,
)

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables with retry logic for Cloud SQL socket
    logger.info("Creating database tables...")
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created!")
            break
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                logger.warning("Could not connect to database after retries. Continuing anyway.")

    # Order status enum migration (Cannot be in a transaction in Postgres)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'confirmed'"))
            await conn.commit()
    except Exception as e:
        logger.debug(f"Enum migration note: {e}")
    
    # Add missing columns (migration)
    try:
        async with engine.begin() as conn:
            # User table migrations
            await conn.execute(text("""
                ALTER TABLE "user" ADD COLUMN IF NOT EXISTS restaurant_id INTEGER REFERENCES restaurant(id);
            """))
            await conn.execute(text("""
                ALTER TABLE "user" ADD COLUMN IF NOT EXISTS default_address VARCHAR;
            """))
            await conn.execute(text("""
                ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_latitude FLOAT;
            """))
            await conn.execute(text("""
                ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_longitude FLOAT;
            """))
            
            # Restaurant table migrations - all potentially missing columns
            await conn.execute(text("""
                ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS description VARCHAR;
            """))
            await conn.execute(text("""
                ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS logo_url VARCHAR;
            """))
            await conn.execute(text("""
                ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS phone_number VARCHAR;
            """))
            await conn.execute(text("""
                ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
            """))
            await conn.execute(text("""
                ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR DEFAULT 'basic';
            """))
            await conn.execute(text("""
                ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS commission_rate FLOAT DEFAULT 0.0;
            """))
            
            # Menu migrations
            await conn.execute(text("""
                ALTER TABLE "menu" ADD COLUMN IF NOT EXISTS "order" INTEGER DEFAULT 0;
            """))
            
            # Category migrations
            await conn.execute(text("""
                ALTER TABLE "category" ADD COLUMN IF NOT EXISTS "order" INTEGER DEFAULT 0;
            """))
            
            # MenuItem migrations
            await conn.execute(text("""
                ALTER TABLE "menuitem" ADD COLUMN IF NOT EXISTS "order" INTEGER DEFAULT 0;
            """))
            await conn.execute(text("""
                ALTER TABLE "menuitem" ADD COLUMN IF NOT EXISTS "is_available" BOOLEAN DEFAULT TRUE;
            """))
            
        logger.info("Migration: Database columns ensured")
    except Exception as e:
        logger.debug(f"Migration note: {e}")
    
    # Create superuser if not exists
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.email == "admin@lionbot.com"))
            existing_user = result.scalars().first()

            if not existing_user:
                logger.info(f"Creating superuser: {settings.FIRST_SUPERUSER_EMAIL}...")
                superuser = User(
                    full_name="Super Admin",
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    phone_number=settings.FIRST_SUPERUSER_PHONE,
                    hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                    role=UserRole.SUPER_ADMIN,
                    is_active=True
                )
                db.add(superuser)
                await db.commit()
                logger.info("Superuser created successfully.")
            else:
                logger.debug("Superuser already exists")
    except Exception as e:
        logger.error(f"Error creating superuser: {e}")

    yield

    # Shutdown with proper error handling
    logger.info("Shutting down services...")
    from app.services.redis_service import redis_service
    from app.services.whatsapp_service import whatsapp_service

    try:
        await redis_service.close()
        logger.debug("Redis service closed")
    except Exception as e:
        logger.warning(f"Error closing Redis service: {e}")

    try:
        await whatsapp_service.close()
        logger.debug("WhatsApp service closed")
    except Exception as e:
        logger.warning(f"Error closing WhatsApp service: {e}")

    try:
        await engine.dispose()
        logger.debug("Database engine disposed")
    except Exception as e:
        logger.warning(f"Error disposing database engine: {e}")

    logger.info("Shutdown complete")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Lion Delivery BOT - WhatsApp Multi-Restaurant System",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Custom Exception Handlers - Using http_status_code from exception class
@app.exception_handler(LionBotException)
async def lionbot_exception_handler(request: Request, exc: LionBotException):
    """Handle all custom LionBot exceptions using their http_status_code"""
    # Log based on status code severity
    if exc.http_status_code >= 500:
        logger.error(f"Server error [{exc.code}]: {exc.message}")
    elif exc.http_status_code >= 400:
        logger.warning(f"Client error [{exc.code}]: {exc.message}")
    else:
        logger.info(f"Exception [{exc.code}]: {exc.message}")

    return JSONResponse(
        status_code=exc.http_status_code,
        content=exc.to_dict()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions - prevents internal details from leaking"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
    )

# CORS Middleware - Use configured origins
# In production, set CORS_ORIGINS environment variable to specific domains
cors_origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"],  # Only allow credentials with specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

# Proxy Headers for HTTPS behind Google Cloud Run Load Balancer
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# Security Middlewares (in reverse order - last added runs first)
if settings.ENABLE_SECURITY_HEADERS:
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestValidationMiddleware)
    if settings.ENVIRONMENT == "production":
        app.add_middleware(SQLInjectionProtectionMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Lion Delivery BOT API 🦁"}

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint with pool statistics"""
    from datetime import datetime
    from app.db.session import get_pool_stats

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "services": {},
        "pool_stats": {},
    }

    # Check database and get pool stats
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
        # Add connection pool statistics
        try:
            health_status["pool_stats"] = get_pool_stats()
        except Exception:
            pass  # Pool stats are optional
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)[:50]}"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        from app.services.redis_service import redis_service
        await redis_service._execute("PING")
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)[:50]}"
        # Redis failing doesn't make app unhealthy (has fallback)

    return health_status

# Root webhook for Meta verification (without /api/v1 prefix)
@app.get("/webhook")
async def verify_webhook_root(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
    """Root webhook verification for WhatsApp."""
    logger.info(f"Webhook verify: mode={mode}")

    if mode and token and challenge:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook verified!")
            return PlainTextResponse(content=challenge, status_code=200)

    return PlainTextResponse(content="Verification failed", status_code=403)

from app.controllers.bot_controller import bot_controller

@app.post("/webhook")
async def handle_webhook_root(request: Request):
    """Root webhook handler for WhatsApp messages."""
    try:
        body = await request.json()
        if settings.DEBUG:
            logger.debug(f"Webhook received: {body}")

        entries = body.get("entry", [])
        if entries:
            entry = entries[0]
            changes = entry.get("changes", [])
            if changes:
                value = changes[0].get("value", {})
                messages = value.get("messages", [])
                if messages:
                    message = messages[0]
                    phone_number = message.get("from")
                    if phone_number:
                        await bot_controller.handle_message(phone_number, message)

        return {"status": "received"}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        # Don't expose internal error details
        return {"status": "error"}

