"""
Database session management with optimized connection pooling.
Includes health monitoring, retry logic, and proper error handling.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError, DisconnectionError
from sqlalchemy import event
from app.core.config import settings
from app.core.exceptions import DatabaseError, DuplicateRecordError, ConnectionError as DBConnectionError
import logging
import time

logger = logging.getLogger(__name__)

# Connection pool statistics
_pool_stats = {
    "connections_created": 0,
    "connections_recycled": 0,
    "checkout_count": 0,
    "checkin_count": 0,
}


def get_engine_url():
    """Get database URL with appropriate driver."""
    url = settings.get_database_url()
    # Ensure we're using asyncpg for async operations
    if "postgresql://" in url and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    return url


# Create engine with optimized pool settings for production
engine = create_async_engine(
    get_engine_url(),
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Validate connections before use
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    # Additional optimizations
    pool_reset_on_return="rollback",  # Reset connection state on return to pool
    connect_args={
        "command_timeout": 30,  # Query timeout in seconds
        "server_settings": {
            "application_name": "lionbot_backend",
            "statement_timeout": "30000",  # 30 seconds max query time
        }
    } if "postgresql" in get_engine_url() else {},
)


# Event listeners for connection pool monitoring
@event.listens_for(engine.sync_engine, "connect")
def on_connect(dbapi_conn, connection_record):
    """Log when a new connection is created."""
    _pool_stats["connections_created"] += 1
    logger.debug(f"New database connection created (total: {_pool_stats['connections_created']})")


@event.listens_for(engine.sync_engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    """Track connection checkout from pool."""
    _pool_stats["checkout_count"] += 1
    connection_record.info["checkout_time"] = time.time()


@event.listens_for(engine.sync_engine, "checkin")
def on_checkin(dbapi_conn, connection_record):
    """Track connection return to pool and warn on long-held connections."""
    _pool_stats["checkin_count"] += 1
    checkout_time = connection_record.info.get("checkout_time")
    if checkout_time:
        duration = time.time() - checkout_time
        if duration > 5.0:  # Warn if connection held for more than 5 seconds
            logger.warning(f"Connection held for {duration:.2f} seconds")


def get_pool_stats() -> dict:
    """Get current connection pool statistics."""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_out": pool.checkedout(),
        "checked_in": pool.checkedin(),
        "overflow": pool.overflow(),
        "total_connections_created": _pool_stats["connections_created"],
        "total_checkouts": _pool_stats["checkout_count"],
        "total_checkins": _pool_stats["checkin_count"],
    }

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    """
    Dependency that provides a database session.
    Properly handles session lifecycle with error handling.

    Raises:
        DuplicateRecordError: On unique constraint violations
        DBConnectionError: On connection failures
        DatabaseError: On other database errors
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Database integrity error: {e}")
        # Check for duplicate key violations
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'unique constraint' in error_msg.lower() or 'duplicate key' in error_msg.lower():
            raise DuplicateRecordError(message="Record already exists")
        raise DatabaseError(message="Database integrity violation")
    except OperationalError as e:
        await session.rollback()
        logger.error(f"Database connection error: {e}")
        raise DBConnectionError(message="Database connection failed")
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database error: {e}")
        raise DatabaseError(message="Database operation failed")
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected database session error: {e}")
        raise
    finally:
        await session.close()


async def get_db_readonly():
    """
    Dependency for read-only operations.
    No commit on success, just close.

    Raises:
        DBConnectionError: On connection failures
        DatabaseError: On other database errors
    """
    session = AsyncSessionLocal()
    try:
        yield session
    except OperationalError as e:
        logger.error(f"Database connection error (readonly): {e}")
        raise DBConnectionError(message="Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error (readonly): {e}")
        raise DatabaseError(message="Database query failed")
    except Exception as e:
        logger.error(f"Unexpected database read error: {e}")
        raise
    finally:
        await session.close()
