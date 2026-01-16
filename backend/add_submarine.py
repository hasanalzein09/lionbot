"""
Script to add Sub Marine restaurant with full menu to the database.
Restaurant: Sub Marine (ساب مارين)
Connects directly to Google Cloud SQL production database.
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Direct connection to Cloud SQL using external IP
# Instance: lionbot-db, Region: me-west1
DATABASE_URL = "postgresql+asyncpg://postgres:LionBot2024@34.165.115.23/lionbot"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Restaurant Info
RESTAURANT_DATA = {
    "name": "Sub Marine",
    "name_ar": "ساب مارين",
    "description": "Your Subconscious Favorite Taste!",
    "description_ar": "طعمك المفضل اللاواعي!",
    "phone_number": "+96171760313",  # From image: 71 76 03 13 - Saida
    "is_active": True,
    "subscription_tier": "pro",
    "commission_rate": 0.15
}

# Menu Categories and Items
MENU_DATA = {
    "name": "Main Menu",
    "name_ar": "القائمة الرئيسية",
    "categories": [
        {
            "name": "Sandwiches",
            "name_ar": "ساندويشات",
            "order": 1,
            "items": [
                {"name": "Spicy Steak", "name_ar": "ستيك حار", "price": 620000},
                {"name": "Chinese", "name_ar": "صيني", "price": 500000},
                {"name": "Mexican", "name_ar": "مكسيكي", "price": 540000},
                {"name": "Tawook", "name_ar": "طاووق", "price": 490000},
                {"name": "Francisco", "name_ar": "فرانسيسكو", "price": 550000},
                {"name": "Crab", "name_ar": "سلطعون", "price": 530000},
                {"name": "Shrimp", "name_ar": "قريدس", "price": 670000},
                {"name": "Crab & Shrimp", "name_ar": "سلطعون وقريدس", "price": 700000},
                {"name": "Supreme", "name_ar": "سوبريم", "price": 570000},
                {"name": "Makanek", "name_ar": "مقانق", "price": 520000},
                {"name": "Spicy Fajita", "name_ar": "فاهيتا حارة", "price": 650000},
                {"name": "Philadelphia", "name_ar": "فيلادلفيا", "price": 650000},
                {"name": "Escalope", "name_ar": "اسكالوب", "price": 500000},
                {"name": "Twister", "name_ar": "تويستر", "price": 550000},
                {"name": "Rosto", "name_ar": "روستو", "price": 550000},
                {"name": "Rosto & Cheese", "name_ar": "روستو وجبنة", "price": 600000},
                {"name": "Honey Mustard", "name_ar": "عسل وخردل", "price": 600000},
                {"name": "Chicken Sub", "name_ar": "ساب دجاج", "price": 550000},
                {"name": "Sojok", "name_ar": "سجق", "price": 520000},
                {"name": "Dynamite Chicken", "name_ar": "دجاج ديناميت", "price": 650000},
                {"name": "Truffle Steak", "name_ar": "ستيك ترافل", "price": 780000},
                {"name": "Dynamite Shrimp", "name_ar": "قريدس ديناميت", "price": 780000},
            ]
        },
        {
            "name": "Burgers",
            "name_ar": "برغر",
            "order": 2,
            "items": [
                {"name": "Lebanese", "name_ar": "لبناني", "price": 620000},
                {"name": "Submarine", "name_ar": "سابمارين", "price": 760000},
                {"name": "Classic Smash", "name_ar": "كلاسيك سماش", "price": 640000},
                {"name": "Mozzarella", "name_ar": "موزاريلا", "price": 760000},
                {"name": "Zinger", "name_ar": "زنجر", "price": 540000},
                {"name": "Hot Zinger", "name_ar": "زنجر حار", "price": 540000},
            ]
        },
        {
            "name": "Salads",
            "name_ar": "سلطات",
            "order": 3,
            "items": [
                {"name": "Tuna Pasta", "name_ar": "باستا تونا", "price": 560000},
                {"name": "Caesar", "name_ar": "سيزر", "price": 500000},
                {"name": "Chicken Caesar", "name_ar": "سيزر دجاج", "price": 640000},
                {"name": "Greek", "name_ar": "يوناني", "price": 440000},
                {"name": "Halloumi", "name_ar": "حلوم", "price": 500000},
                {"name": "Quinoa", "name_ar": "كينوا", "price": 700000},
            ]
        },
        {
            "name": "Plates",
            "name_ar": "أطباق",
            "order": 4,
            "items": [
                {"name": "Grilled Chicken", "name_ar": "دجاج مشوي", "price": 620000},
                {"name": "Crispy 4 PCS", "name_ar": "كريسبي ٤ قطع", "price": 800000},
                {"name": "Crispy 8 PCS", "name_ar": "كريسبي ٨ قطع", "price": 900000},
                {"name": "Escalopino", "name_ar": "اسكالوبينو", "price": 850000},
            ]
        },
        {
            "name": "Appetizer",
            "name_ar": "مقبلات",
            "order": 5,
            "items": [
                {"name": "Fries", "name_ar": "بطاطا مقلية", "price": 320000},
                {"name": "Curly Fries", "name_ar": "بطاطا كيرلي", "price": 470000},
                {"name": "Wedges", "name_ar": "ودجز", "price": 380000},
                {"name": "Mozz Sticks", "name_ar": "أصابع موزاريلا", "price": 430000},
                {"name": "Breaded Halloumi", "name_ar": "حلوم مقرمش", "price": 430000},
                {"name": "Chicken Tenders", "name_ar": "تندرز دجاج", "price": 550000},
            ]
        },
        {
            "name": "Beverages",
            "name_ar": "مشروبات",
            "order": 6,
            "items": [
                {"name": "Pepsi", "name_ar": "بيبسي", "price": 120000},
                {"name": "Pepsi Diet", "name_ar": "بيبسي دايت", "price": 120000},
                {"name": "7UP", "name_ar": "سفن أب", "price": 120000},
                {"name": "7UP Diet", "name_ar": "سفن أب دايت", "price": 120000},
                {"name": "Mirinda", "name_ar": "ميرندا", "price": 120000},
                {"name": "Mirinda Diet", "name_ar": "ميرندا دايت", "price": 120000},
                {"name": "Sparkling Water", "name_ar": "مياه غازية", "price": 120000},
                {"name": "Iced Tea", "name_ar": "شاي مثلج", "price": 120000},
                {"name": "Water", "name_ar": "مياه", "price": 50000},
            ]
        },
        {
            "name": "Add On",
            "name_ar": "إضافات",
            "order": 7,
            "items": [
                {"name": "Cheddar Slice", "name_ar": "شريحة شيدر", "price": 50000},
                {"name": "Chicken Portion", "name_ar": "حصة دجاج", "price": 200000},
                {"name": "Burger Patty 120g", "name_ar": "قرص برغر ١٢٠غ", "price": 250000},
                {"name": "Burger Patty 60g", "name_ar": "قرص برغر ٦٠غ", "price": 150000},
                {"name": "Turkey Slice", "name_ar": "شريحة حبش", "price": 90000},
                {"name": "Sauce Dip", "name_ar": "صوص جانبي", "price": 70000},
            ]
        },
    ]
}


async def ensure_columns():
    """Add bilingual columns if they don't exist."""
    migrations = [
        # Restaurant bilingual fields
        "ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS name_ar VARCHAR",
        "ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS description_ar VARCHAR",
        # Menu bilingual fields
        'ALTER TABLE "menu" ADD COLUMN IF NOT EXISTS name_ar VARCHAR',
        # Category bilingual fields
        'ALTER TABLE "category" ADD COLUMN IF NOT EXISTS name_ar VARCHAR',
        # MenuItem bilingual fields
        'ALTER TABLE "menuitem" ADD COLUMN IF NOT EXISTS name_ar VARCHAR',
        'ALTER TABLE "menuitem" ADD COLUMN IF NOT EXISTS description_ar TEXT',
    ]
    
    async with engine.begin() as conn:
        for sql in migrations:
            try:
                await conn.execute(text(sql))
            except Exception as e:
                logger.warning(f"Migration note: {e}")
        logger.info("✅ Ensured bilingual columns exist in database")


async def add_submarine_restaurant():
    """Add Sub Marine restaurant with all menu items using raw SQL."""
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if restaurant already exists
            result = await db.execute(
                text("SELECT id FROM restaurant WHERE name = :name"),
                {"name": "Sub Marine"}
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.warning(f"Sub Marine restaurant already exists with ID {existing}! Skipping...")
                return existing
            
            # Create Restaurant
            result = await db.execute(
                text("""
                    INSERT INTO restaurant (name, name_ar, description, description_ar, phone_number, is_active, subscription_tier, commission_rate)
                    VALUES (:name, :name_ar, :description, :description_ar, :phone_number, :is_active, :subscription_tier, :commission_rate)
                    RETURNING id
                """),
                RESTAURANT_DATA
            )
            restaurant_id = result.scalar_one()
            logger.info(f"✅ Created restaurant: {RESTAURANT_DATA['name']} / {RESTAURANT_DATA['name_ar']} (ID: {restaurant_id})")
            
            # Create Menu
            result = await db.execute(
                text("""
                    INSERT INTO "menu" (restaurant_id, name, name_ar, is_active, "order")
                    VALUES (:restaurant_id, :name, :name_ar, true, 0)
                    RETURNING id
                """),
                {
                    "restaurant_id": restaurant_id,
                    "name": MENU_DATA["name"],
                    "name_ar": MENU_DATA["name_ar"]
                }
            )
            menu_id = result.scalar_one()
            logger.info(f"✅ Created menu: {MENU_DATA['name']} / {MENU_DATA['name_ar']}")
            
            # Create Categories and Items
            total_items = 0
            for cat_data in MENU_DATA["categories"]:
                result = await db.execute(
                    text("""
                        INSERT INTO "category" (menu_id, name, name_ar, "order")
                        VALUES (:menu_id, :name, :name_ar, :order)
                        RETURNING id
                    """),
                    {
                        "menu_id": menu_id,
                        "name": cat_data["name"],
                        "name_ar": cat_data["name_ar"],
                        "order": cat_data["order"]
                    }
                )
                category_id = result.scalar_one()
                
                # Add items to category
                for idx, item_data in enumerate(cat_data["items"]):
                    await db.execute(
                        text("""
                            INSERT INTO "menuitem" (category_id, name, name_ar, price, is_available, "order")
                            VALUES (:category_id, :name, :name_ar, :price, true, :order)
                        """),
                        {
                            "category_id": category_id,
                            "name": item_data["name"],
                            "name_ar": item_data["name_ar"],
                            "price": item_data["price"],
                            "order": idx
                        }
                    )
                    total_items += 1
                
                logger.info(f"  📁 {cat_data['name']} ({cat_data['name_ar']}): {len(cat_data['items'])} items")
            
            await db.commit()
            
            logger.info(f"\n🎉 Successfully added Sub Marine restaurant!")
            logger.info(f"   Restaurant ID: {restaurant_id}")
            logger.info(f"   Total Categories: {len(MENU_DATA['categories'])}")
            logger.info(f"   Total Menu Items: {total_items}")
            
            return restaurant_id
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error adding restaurant: {e}")
            raise


async def main():
    """Add bilingual columns and insert restaurant data."""
    logger.info("🚀 Starting Sub Marine restaurant import...")
    logger.info(f"📍 Connecting to Cloud SQL: 34.165.115.23/lionbot")
    
    # Ensure bilingual columns exist
    await ensure_columns()
    
    # Add the restaurant
    restaurant_id = await add_submarine_restaurant()
    
    if restaurant_id:
        logger.info(f"\n✨ Done! Restaurant ID: {restaurant_id}")
        logger.info("🌐 The menu is now available in both English and Arabic!")


if __name__ == "__main__":
    asyncio.run(main())
