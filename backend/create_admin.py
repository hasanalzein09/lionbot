"""
Create super admin user in production database
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import hashlib
import secrets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Direct connection to Cloud SQL
DATABASE_URL = "postgresql+asyncpg://postgres:LionBot2024@34.165.115.23/lionbot"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def get_password_hash(password: str) -> str:
    """Simple password hashing (matching the backend's bcrypt-like format)"""
    # The backend uses passlib with bcrypt, but for insertion we can use a simple approach
    # Actually we need to use the same hashing as the backend
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


async def create_superuser():
    """Create super admin user."""
    async with AsyncSessionLocal() as session:
        # Check if user exists
        result = await session.execute(
            text("SELECT id FROM \"user\" WHERE email = :email"),
            {"email": "admin@lionbot.com"}
        )
        existing = result.fetchone()
        
        if existing:
            logger.info("✅ Super admin already exists!")
            return
        
        # Create password hash
        hashed_password = get_password_hash("admin123")
        
        # Insert superuser
        await session.execute(
            text("""
                INSERT INTO "user" (full_name, email, phone_number, hashed_password, role, is_active)
                VALUES (:name, :email, :phone, :password, :role, TRUE)
            """),
            {
                "name": "Super Admin",
                "email": "admin@lionbot.com",
                "phone": "+96170106083",
                "password": hashed_password,
                "role": "super_admin"
            }
        )
        await session.commit()
        logger.info("✅ Super admin created successfully!")
        logger.info("   Email: admin@lionbot.com")
        logger.info("   Password: admin123")


async def main():
    logger.info("🔑 Creating super admin user...")
    await create_superuser()
    logger.info("\n✨ Done!")


if __name__ == "__main__":
    asyncio.run(main())
