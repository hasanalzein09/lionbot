"""
Script to add restaurant categories and assign Sub Marine to a category.
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Direct connection to Cloud SQL
DATABASE_URL = "postgresql+asyncpg://postgres:LionBot2024@34.165.115.23/lionbot"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Restaurant Categories
CATEGORIES = [
    {"name": "Offers", "name_ar": "عروض", "icon": "🔥", "order": 1},
    {"name": "Snacks", "name_ar": "سناك", "icon": "🍿", "order": 2},
    {"name": "Shawarma", "name_ar": "شاورما", "icon": "🌯", "order": 3},
    {"name": "Sandwiches", "name_ar": "ساندويشات", "icon": "🥪", "order": 4},
    {"name": "Pizza", "name_ar": "بيتزا", "icon": "🍕", "order": 5},
    {"name": "Burgers", "name_ar": "برغر", "icon": "🍔", "order": 6},
    {"name": "Grills", "name_ar": "مشاوي", "icon": "🍖", "order": 7},
    {"name": "Home Food", "name_ar": "أكل بيتي", "icon": "🍲", "order": 8},
    {"name": "Sweets", "name_ar": "حلويات", "icon": "🍰", "order": 9},
    {"name": "Beverages", "name_ar": "مشروبات", "icon": "🥤", "order": 10},
]


async def ensure_table():
    """Create restaurant_category table if not exists."""
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS restaurant_category (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                name_ar VARCHAR NOT NULL,
                icon VARCHAR DEFAULT '🍽️',
                "order" INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE
            )
        """))
        
        # Add category_id to restaurant if not exists
        try:
            await conn.execute(text("""
                ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES restaurant_category(id)
            """))
        except Exception as e:
            logger.warning(f"Note: {e}")
        
        logger.info("✅ Table structure ready")


async def add_categories():
    """Add restaurant categories."""
    async with AsyncSessionLocal() as session:
        for cat in CATEGORIES:
            # Check if exists
            result = await session.execute(
                text("SELECT id FROM restaurant_category WHERE name = :name"),
                {"name": cat["name"]}
            )
            existing = result.fetchone()
            
            if not existing:
                await session.execute(
                    text("""
                        INSERT INTO restaurant_category (name, name_ar, icon, "order", is_active)
                        VALUES (:name, :name_ar, :icon, :order, TRUE)
                    """),
                    cat
                )
                logger.info(f"  ✅ Added: {cat['icon']} {cat['name']} / {cat['name_ar']}")
            else:
                logger.info(f"  ⏭️ Exists: {cat['name']}")
        
        await session.commit()


async def assign_submarine_category():
    """Assign Sub Marine to Sandwiches category."""
    async with AsyncSessionLocal() as session:
        # Get Sandwiches category ID
        result = await session.execute(
            text("SELECT id FROM restaurant_category WHERE name = 'Sandwiches'")
        )
        cat = result.fetchone()
        
        if cat:
            await session.execute(
                text("UPDATE restaurant SET category_id = :cat_id WHERE name = 'Sub Marine'"),
                {"cat_id": cat[0]}
            )
            await session.commit()
            logger.info(f"✅ Sub Marine assigned to Sandwiches category (ID: {cat[0]})")


async def main():
    logger.info("🚀 Adding restaurant categories...")
    
    await ensure_table()
    await add_categories()
    await assign_submarine_category()
    
    # Show summary
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM restaurant_category"))
        count = result.scalar()
        logger.info(f"\n📊 Total categories: {count}")
    
    logger.info("\n✨ Done!")


if __name__ == "__main__":
    asyncio.run(main())
