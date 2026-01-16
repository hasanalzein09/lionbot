import asyncio
import logging
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as db:
        # Check if superuser exists
        # Note: In a real app, use a better check
        # For now, we just try to create one
        
        # Create Super User
        from app.core.config import settings
        superuser = User(
            full_name="Super Admin",
            email=settings.FIRST_SUPERUSER_EMAIL,
            phone_number=settings.FIRST_SUPERUSER_PHONE,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        
        try:
            db.add(superuser)
            await db.commit()
            logger.info("Superuser created successfully!")
        except Exception as e:
            logger.warning(f"Superuser might already exist or error: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())
