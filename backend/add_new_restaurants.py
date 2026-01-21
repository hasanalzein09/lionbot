"""
Script to add new restaurants and menus to the database
Restaurants:
1. فرن القمر للجريش (Manakish category)
2. بيت النار على الحطب (Manakish category)
3. فول و ترويقة (Breakfast/Tarwi2a category)
4. KAAKÉ by meat chop (Breakfast/Tarwi2a category)

Also:
- Removes Snacks and Burgers categories
- Adds Manakish and Breakfast categories
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://lionbot:LionBot2024@163.245.208.160:5432/lionbot"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Exchange rate: 89,500 LBP = 1 USD
LBP_TO_USD = 89500

def lbp_to_usd(lbp_price: int) -> float:
    """Convert LBP to USD"""
    return round(lbp_price / LBP_TO_USD, 2)


async def update_categories(db):
    """Remove Snacks/Burgers, add Manakish/Breakfast categories."""
    logger.info("=" * 60)
    logger.info("🔧 STEP 1: Updating Restaurant Categories")
    logger.info("=" * 60)
    
    # Delete Snacks category
    await db.execute(text("DELETE FROM restaurant_category WHERE name = 'Snacks'"))
    logger.info("❌ Deleted category: Snacks")
    
    # Delete Burgers category
    await db.execute(text("DELETE FROM restaurant_category WHERE name = 'Burgers'"))
    logger.info("❌ Deleted category: Burgers")
    
    # Check and add Manakish
    result = await db.execute(text("SELECT id FROM restaurant_category WHERE name = 'Manakish'"))
    if not result.scalar_one_or_none():
        await db.execute(text("""
            INSERT INTO restaurant_category (name, name_ar, icon, "order", is_active)
            VALUES ('Manakish', 'مناقيش', '🫓', 2, true)
        """))
        logger.info("✅ Added category: Manakish / مناقيش")
    
    # Check and add Breakfast
    result = await db.execute(text("SELECT id FROM restaurant_category WHERE name = 'Breakfast'"))
    if not result.scalar_one_or_none():
        await db.execute(text("""
            INSERT INTO restaurant_category (name, name_ar, icon, "order", is_active)
            VALUES ('Breakfast', 'ترويقة', '🍳', 3, true)
        """))
        logger.info("✅ Added category: Breakfast / ترويقة")
    
    await db.commit()
    
    # Get category IDs
    result = await db.execute(text("SELECT id, name FROM restaurant_category"))
    rows = result.fetchall()
    cat_map = {row[1]: row[0] for row in rows}
    logger.info(f"📋 Current categories: {cat_map}")
    return cat_map


async def add_restaurant(db, data, category_id):
    """Add a restaurant if it doesn't exist."""
    result = await db.execute(
        text("SELECT id FROM restaurant WHERE name = :name"),
        {"name": data["name"]}
    )
    existing = result.scalar_one_or_none()
    if existing:
        logger.info(f"⏭️ Restaurant {data['name']} already exists (ID: {existing})")
        return existing
    
    result = await db.execute(
        text("""
            INSERT INTO restaurant (name, name_ar, description, description_ar, phone_number, is_active, subscription_tier, commission_rate, category_id)
            VALUES (:name, :name_ar, :description, :description_ar, :phone_number, :is_active, :subscription_tier, :commission_rate, :category_id)
            RETURNING id
        """),
        {**data, "category_id": category_id}
    )
    rest_id = result.scalar_one()
    logger.info(f"✅ Added restaurant: {data['name_ar']} (ID: {rest_id})")
    return rest_id


async def add_menu_with_items(db, restaurant_id, menu_data):
    """Add menu, categories, and items for a restaurant."""
    # Create Menu
    result = await db.execute(
        text("""
            INSERT INTO "menu" (restaurant_id, name, name_ar, is_active, "order")
            VALUES (:restaurant_id, :name, :name_ar, true, 0)
            RETURNING id
        """),
        {
            "restaurant_id": restaurant_id,
            "name": menu_data["name"],
            "name_ar": menu_data["name_ar"]
        }
    )
    menu_id = result.scalar_one()
    
    total_items = 0
    for cat_data in menu_data["categories"]:
        # Create Category
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
                "order": cat_data.get("order", 0)
            }
        )
        category_id = result.scalar_one()
        
        # Add Items
        for idx, item in enumerate(cat_data["items"]):
            await db.execute(
                text("""
                    INSERT INTO "menuitem" (category_id, name, name_ar, price, is_available, "order")
                    VALUES (:category_id, :name, :name_ar, :price, true, :order)
                """),
                {
                    "category_id": category_id,
                    "name": item["name"],
                    "name_ar": item["name_ar"],
                    "price": lbp_to_usd(item["price"]),
                    "order": idx
                }
            )
            total_items += 1
        
        logger.info(f"  📁 {cat_data['name_ar']}: {len(cat_data['items'])} items")
    
    return total_items


# ============================================
# RESTAURANT DATA
# ============================================

RESTAURANTS = [
    {
        "info": {
            "name": "Forn Al Qamar",
            "name_ar": "فرن القمر للجريش",
            "description": "Traditional Lebanese manakish and ghrish bakery",
            "description_ar": "فرن تقليدي للمناقيش والجريش",
            "phone_number": "+96170616054",
            "is_active": True,
            "subscription_tier": "basic",
            "commission_rate": 10.0
        },
        "category": "Manakish",
        "menu": {
            "name": "Main Menu",
            "name_ar": "القائمة الرئيسية",
            "categories": [
                {
                    "name": "Manakish", "name_ar": "مناقيش", "order": 1,
                    "items": [
                        {"name": "Zaatar", "name_ar": "زعتر", "price": 50000},
                        {"name": "Zaatar with Vegetables", "name_ar": "زعتر مع خضار", "price": 80000},
                        {"name": "Cheese", "name_ar": "جبنة", "price": 150000},
                        {"name": "Half & Half", "name_ar": "نص بنص", "price": 100000},
                        {"name": "Cheese & Kashkaval", "name_ar": "جبنة و قشقوان", "price": 200000},
                        {"name": "Kishek", "name_ar": "كشك", "price": 150000},
                        {"name": "Labneh", "name_ar": "لبنة", "price": 150000},
                        {"name": "Onion & Tomato", "name_ar": "بصل وبندورة", "price": 150000},
                        {"name": "Onion Tomato Cheese", "name_ar": "بصل وبندورة مع جبنة", "price": 200000},
                        {"name": "Meat", "name_ar": "لحمة", "price": 200000},
                        {"name": "Sausage & Cheese", "name_ar": "سجق وجبنة", "price": 250000},
                        {"name": "Mortadella & Cheese", "name_ar": "مرتديلا وجبنة", "price": 250000},
                        {"name": "Cheese Loaf", "name_ar": "رغيف جبنة", "price": 200000},
                        {"name": "Tawook", "name_ar": "طاووق", "price": 300000},
                        {"name": "Fajita", "name_ar": "فاهيتا", "price": 300000},
                    ]
                },
                {
                    "name": "Ghrish", "name_ar": "جريش", "order": 2,
                    "items": [
                        {"name": "Zaatar Ghrish", "name_ar": "زعتر جريش", "price": 70000},
                        {"name": "Cheese Ghrish", "name_ar": "جبنة جريش", "price": 180000},
                        {"name": "Kishek Ghrish", "name_ar": "كشك جريش", "price": 100000},
                        {"name": "Labneh Ghrish", "name_ar": "لبنة جريش", "price": 100000},
                        {"name": "Onion Tomato Ghrish", "name_ar": "بصل وبندورة جريش", "price": 100000},
                        {"name": "Sausage Cheese Ghrish", "name_ar": "سجق وجبنة جريش", "price": 250000},
                        {"name": "Mortadella Cheese Ghrish", "name_ar": "مرتديلا وجبنة جريش", "price": 250000},
                    ]
                },
                {
                    "name": "Pizza", "name_ar": "بيتزا", "order": 3,
                    "items": [
                        {"name": "Veggie Pizza", "name_ar": "بيتزا خضرا", "price": 400000},
                        {"name": "Mortadella Pizza", "name_ar": "بيتزا مرتديلا", "price": 500000},
                        {"name": "Sausage Pizza", "name_ar": "بيتزا سجق", "price": 500000},
                        {"name": "Chicken Pizza", "name_ar": "بيتزا دجاج", "price": 550000},
                    ]
                },
                {
                    "name": "Kaak Traboulsi", "name_ar": "كعك طرابلسي", "order": 4,
                    "items": [
                        {"name": "Traboulsi Kaak", "name_ar": "كعك طرابلسية", "price": 50000},
                        {"name": "Traboulsi with Cheese", "name_ar": "طرابلسية مع جبنة", "price": 150000},
                        {"name": "Traboulsi Extra Cheese", "name_ar": "طرابلسية جبنة اكسترا", "price": 220000},
                        {"name": "Traboulsi with Mortadella", "name_ar": "طرابلسية مع مرتديلا", "price": 200000},
                    ]
                },
            ]
        }
    },
    {
        "info": {
            "name": "Beit Al Nar",
            "name_ar": "بيت النار على الحطب",
            "description": "Wood-fired manakish and bakery",
            "description_ar": "مناقيش على الحطب",
            "phone_number": "+96176723596",
            "is_active": True,
            "subscription_tier": "basic",
            "commission_rate": 10.0
        },
        "category": "Manakish",
        "menu": {
            "name": "Main Menu",
            "name_ar": "القائمة الرئيسية",
            "categories": [
                {
                    "name": "Manakish Regular", "name_ar": "مناقيش عادية", "order": 1,
                    "items": [
                        {"name": "Zaatar", "name_ar": "زعتر", "price": 40000},
                        {"name": "Cheese", "name_ar": "جبنة", "price": 120000},
                        {"name": "Kishek", "name_ar": "كشك", "price": 100000},
                        {"name": "Onion & Tomato", "name_ar": "بصل وبندورة", "price": 100000},
                        {"name": "Onion Tomato Cheese", "name_ar": "بصل وبندورة وجبنة", "price": 170000},
                        {"name": "Half & Half", "name_ar": "نص نص", "price": 100000},
                        {"name": "Labneh with Veggies", "name_ar": "لبنة مع خضرة", "price": 100000},
                        {"name": "Sausage", "name_ar": "سجق", "price": 150000},
                        {"name": "Mortadella", "name_ar": "مرتديلا", "price": 150000},
                        {"name": "Tawook", "name_ar": "طاووق", "price": 250000},
                        {"name": "Fajita", "name_ar": "فاهيتا", "price": 250000},
                        {"name": "Meat", "name_ar": "لحمة", "price": 200000},
                        {"name": "Pepperoni", "name_ar": "بيروني", "price": 200000},
                        {"name": "Awarma", "name_ar": "قاورما", "price": 200000},
                        {"name": "Halloumi", "name_ar": "حلوم", "price": 120000},
                        {"name": "Bacon", "name_ar": "بيكون", "price": 150000},
                        {"name": "Cheese Loaf", "name_ar": "رغيف جبنة", "price": 150000},
                        {"name": "Croissant", "name_ar": "كرواسون", "price": 50000},
                    ]
                },
                {
                    "name": "Manakish Special", "name_ar": "مناقيش سبيسيال", "order": 2,
                    "items": [
                        {"name": "Zaatar Special", "name_ar": "زعتر بلدي سبيسيال", "price": 75000},
                        {"name": "Cheese Special", "name_ar": "جبنة سبيسيال", "price": 200000},
                        {"name": "Kishek Special", "name_ar": "كشك سبيسيال", "price": 150000},
                        {"name": "Sausage Special", "name_ar": "سجق سبيسيال", "price": 300000},
                        {"name": "Mortadella Special", "name_ar": "مرتديلا سبيسيال", "price": 300000},
                        {"name": "Tawook Special", "name_ar": "طاووق سبيسيال", "price": 400000},
                        {"name": "Fajita Special", "name_ar": "فاهيتا سبيسيال", "price": 400000},
                        {"name": "Meat Special", "name_ar": "لحمة سبيسيال", "price": 400000},
                        {"name": "Awarma Special", "name_ar": "قاورما سبيسيال", "price": 400000},
                    ]
                },
                {
                    "name": "Pizza", "name_ar": "بيتزا", "order": 3,
                    "items": [
                        {"name": "Veggie Pizza", "name_ar": "بيتزا خضرة", "price": 250000},
                        {"name": "Sausage Pizza", "name_ar": "بيتزا سجق", "price": 300000},
                        {"name": "Mortadella Pizza", "name_ar": "بيتزا مرتديلا", "price": 300000},
                        {"name": "Awarma Pizza", "name_ar": "بيتزا قاورما", "price": 350000},
                        {"name": "Pepperoni Pizza", "name_ar": "بيتزا بيبروني", "price": 350000},
                    ]
                },
            ]
        }
    },
    {
        "info": {
            "name": "Foul w Tarwi2a",
            "name_ar": "فول و ترويقة",
            "description": "Traditional Lebanese breakfast - Foul, Hummus, Falafel",
            "description_ar": "ترويقة لبنانية تقليدية - فول، حمص، فلافل",
            "phone_number": "",
            "is_active": True,
            "subscription_tier": "basic",
            "commission_rate": 10.0
        },
        "category": "Breakfast",
        "menu": {
            "name": "Main Menu",
            "name_ar": "القائمة الرئيسية",
            "categories": [
                {
                    "name": "Foul & Hummus", "name_ar": "الأصناف", "order": 1,
                    "items": [
                        {"name": "Large Foul Bowl", "name_ar": "صحن فول كبير", "price": 300000},
                        {"name": "Clay Foul Bowl", "name_ar": "صحن فول فخار", "price": 200000},
                        {"name": "Large Hummus Bowl", "name_ar": "صحن حمص كبير", "price": 300000},
                        {"name": "Clay Hummus Bowl", "name_ar": "صحن حمص فخار", "price": 200000},
                        {"name": "Large Balila Bowl", "name_ar": "صحن بليلة كبير", "price": 300000},
                        {"name": "Clay Balila Bowl", "name_ar": "صحن بليلة فخار", "price": 200000},
                        {"name": "Large Fatteh Platter", "name_ar": "جاط فتة كبير", "price": 650000},
                        {"name": "Small Fatteh Platter", "name_ar": "جاط فتة صغير", "price": 450000},
                        {"name": "Half Dozen Falafel", "name_ar": "نص دزينة فلافل", "price": 250000},
                        {"name": "Dozen Falafel", "name_ar": "دزينة فلافل", "price": 500000},
                    ]
                },
                {
                    "name": "Breakfast", "name_ar": "ترويقة", "order": 2,
                    "items": [
                        {"name": "Labneh with Service", "name_ar": "صحن لبنة مع سرفيس", "price": 250000},
                        {"name": "Cheese with Service", "name_ar": "صحن جبنة مع سرفيس", "price": 250000},
                        {"name": "Eggs with Service", "name_ar": "صحن بيض مع سرفيس", "price": 250000},
                        {"name": "Sausage with Service", "name_ar": "صحن سجق مع سرفيس", "price": 450000},
                        {"name": "Awarma with Service", "name_ar": "صحن قورما مع سرفيس", "price": 450000},
                        {"name": "Hummus with Meat Large", "name_ar": "حمص مع لحمة كبير", "price": 650000},
                        {"name": "Hummus with Awarma Large", "name_ar": "حمص مع قورما كبير", "price": 700000},
                    ]
                },
            ]
        }
    },
    {
        "info": {
            "name": "KAAKE by meat chop",
            "name_ar": "كعكي",
            "description": "Kaak and Saj with various fillings",
            "description_ar": "كعك وصاج بحشوات متنوعة",
            "phone_number": "",
            "is_active": True,
            "subscription_tier": "basic",
            "commission_rate": 10.0
        },
        "category": "Breakfast",
        "menu": {
            "name": "Main Menu",
            "name_ar": "القائمة الرئيسية",
            "categories": [
                {
                    "name": "Kaak & Saj", "name_ar": "كعك وصاج", "order": 1,
                    "items": [
                        {"name": "Zaatar", "name_ar": "زعتر", "price": 90000},
                        {"name": "Keshek", "name_ar": "كشك", "price": 150000},
                        {"name": "Bandoura w Bassal", "name_ar": "بندورة وبصل", "price": 90000},
                        {"name": "Keshek w Jebneh", "name_ar": "كشك مع جبنة", "price": 220000},
                        {"name": "Keshek Awarma Cheese", "name_ar": "كشك مع قورما وجبنة", "price": 360000},
                        {"name": "Jebneh 3ekawi", "name_ar": "جبنة عكاوي", "price": 180000},
                        {"name": "3ekawi w Mozzarella", "name_ar": "عكاوي مع موزاريلا", "price": 200000},
                        {"name": "3 Cheese", "name_ar": "جبنة 3 أنواع", "price": 250000},
                        {"name": "4 Cheese", "name_ar": "4 أجبان", "price": 300000},
                        {"name": "Jebneh Bolghari", "name_ar": "جبنة بلغاري", "price": 180000},
                        {"name": "Cheese & Chips", "name_ar": "جبنة وشيبس", "price": 200000},
                        {"name": "Haloum Pesto", "name_ar": "حلوم بيستو", "price": 300000},
                        {"name": "Labni", "name_ar": "لبني", "price": 150000},
                        {"name": "Labni w Zaatar", "name_ar": "لبني زعتر", "price": 180000},
                        {"name": "Labni Harra", "name_ar": "لبني حرة", "price": 180000},
                        {"name": "Picon", "name_ar": "بيكون", "price": 200000},
                        {"name": "Basterma w Jebneh", "name_ar": "بسطرمة وجبنة", "price": 440000},
                        {"name": "Basterma w Eggs", "name_ar": "بسطرمة وبيض", "price": 440000},
                        {"name": "Sojok w Jebneh", "name_ar": "سجق وجبنة", "price": 440000},
                        {"name": "Sojok w Eggs", "name_ar": "سجق وبيض", "price": 440000},
                        {"name": "Kafta w Jebneh", "name_ar": "كفتة وجبنة", "price": 440000},
                        {"name": "2awarma w Jebneh", "name_ar": "قورما وجبنة", "price": 440000},
                        {"name": "2awarma w Eggs", "name_ar": "قورما وبيض", "price": 440000},
                        {"name": "Kaaki Burger", "name_ar": "كعكي برغر", "price": 440000},
                        {"name": "Turkey Cheese", "name_ar": "جبنة تركي", "price": 300000},
                        {"name": "Fajitas", "name_ar": "فاهيتا", "price": 440000},
                        {"name": "Pepperoni", "name_ar": "بيبروني", "price": 440000},
                        {"name": "Chicken Sub", "name_ar": "تشيكن صب", "price": 390000},
                        {"name": "Tawook", "name_ar": "طاووق", "price": 390000},
                        {"name": "Nutella Banana", "name_ar": "نوتيلا موز", "price": 270000},
                        {"name": "Nutella Halawi Banana", "name_ar": "نوتيلا حلاوة موز", "price": 320000},
                    ]
                },
                {
                    "name": "Drinks", "name_ar": "مشروبات", "order": 2,
                    "items": [
                        {"name": "Soft Drinks", "name_ar": "مشروبات غازية", "price": 150000},
                        {"name": "Water", "name_ar": "مياه", "price": 50000},
                        {"name": "Sparkling Water", "name_ar": "مياه فوارة", "price": 150000},
                        {"name": "Ice Tea", "name_ar": "آيس تي", "price": 150000},
                    ]
                },
            ]
        }
    },
]


async def main():
    """Main function to add all restaurants."""
    logger.info("🚀 Starting import of 4 new restaurants...")
    logger.info(f"📍 Connecting to Cloud SQL: 163.245.208.160/lionbot")
    
    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Update categories
            cat_map = await update_categories(db)
            
            # Step 2: Add restaurants and menus
            logger.info("\n" + "=" * 60)
            logger.info("🏪 STEP 2: Adding Restaurants & Menus")
            logger.info("=" * 60)
            
            total_items = 0
            for rest_data in RESTAURANTS:
                cat_id = cat_map.get(rest_data["category"])
                if not cat_id:
                    logger.error(f"❌ Category not found: {rest_data['category']}")
                    continue
                
                rest_id = await add_restaurant(db, rest_data["info"], cat_id)
                
                # Check if menu already exists
                result = await db.execute(
                    text('SELECT id FROM "menu" WHERE restaurant_id = :rid'),
                    {"rid": rest_id}
                )
                if result.scalar_one_or_none():
                    logger.info(f"  ⏭️ Menu already exists for {rest_data['info']['name_ar']}")
                    continue
                
                items = await add_menu_with_items(db, rest_id, rest_data["menu"])
                total_items += items
            
            await db.commit()
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("✨ ALL DONE!")
            logger.info("=" * 60)
            
            result = await db.execute(text("SELECT COUNT(*) FROM restaurant WHERE is_active = true"))
            rest_count = result.scalar()
            result = await db.execute(text('SELECT COUNT(*) FROM "menuitem"'))
            item_count = result.scalar()
            
            logger.info(f"📊 Total Active Restaurants: {rest_count}")
            logger.info(f"📊 Total Menu Items: {item_count}")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error: {e}")
            raise
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
