"""
Seed script for Lebanese restaurants
Run: python -m app.db.seed_restaurants
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.restaurant import Restaurant, RestaurantCategory, Branch
from app.models.menu import Menu, Category, MenuItem, MenuItemVariant

# LBP to USD conversion rate
LBP_RATE = 90000

# Restaurant Categories - MATCHING THE ACTUAL DATABASE
# From add_categories.py - these already exist in production DB
CATEGORIES = [
    {"name": "Offers", "name_ar": "عروض", "icon": "🔥", "order": 1},
    {"name": "Snacks", "name_ar": "سناك", "icon": "�", "order": 2},
    {"name": "Shawarma", "name_ar": "شاورما", "icon": "�", "order": 3},
    {"name": "Sandwiches", "name_ar": "ساندويشات", "icon": "�", "order": 4},
    {"name": "Pizza", "name_ar": "بيتزا", "icon": "�", "order": 5},
    {"name": "Burgers", "name_ar": "برغر", "icon": "🍔", "order": 6},
    {"name": "Grills", "name_ar": "مشاوي", "icon": "�", "order": 7},
    {"name": "Home Food", "name_ar": "أكل بيتي", "icon": "�", "order": 8},
    {"name": "Sweets", "name_ar": "حلويات", "icon": "🍰", "order": 9},
    {"name": "Beverages", "name_ar": "مشروبات", "icon": "🥤", "order": 10},
]


# Size translations
SIZES = {
    "Small": "صغير",
    "Medium": "وسط", 
    "Large": "كبير",
    "S": "صغير",
    "M": "وسط",
    "L": "كبير",
    "20cm": "20 سم",
    "25cm": "25 سم",
}

def to_usd(price, currency="USD"):
    """Convert price to USD"""
    if currency == "LBP":
        return round(price / LBP_RATE, 2)
    return price

# Restaurant data with category assignments
RESTAURANTS_DATA = [
    {
        "name": "Callisto",
        "name_ar": "كاليستو",
        "category": "Pizza",
        "menu": {
            "Appetizers / مقبلات": [
                {"name": "Mozzarella Sticks", "name_ar": "أصابع موزاريلا", "price": 5.0, "desc": "Served with Thousand Island sauce", "desc_ar": "تقدم مع صوص ثاوزند آيلاند"},
                {"name": "Cheese Garlic Bread", "name_ar": "خبز بالثوم والجبنة", "price": 5.0},
                {"name": "Chicken Wings", "name_ar": "أجنحة دجاج", "price": 6.0, "desc": "BBQ-Buffalo-Dipsy"},
                {"name": "Cheesy Fries", "name_ar": "بطاطا بالجبنة", "price": 7.0},
                {"name": "Curly Fries", "name_ar": "بطاطا حلزونية", "price": 5.0},
                {"name": "French Fries", "name_ar": "بطاطا مقلية", "price": 3.0},
                {"name": "Truffle Fries", "name_ar": "بطاطا بالترافل", "price": 8.0},
                {"name": "Onion Rings", "name_ar": "حلقات البصل", "price": 4.0},
                {"name": "Callisto Combo", "name_ar": "كومبو كاليستو", "price": 12.0, "desc": "Mozzarella sticks, wings, onion rings, wedges"},
            ],
            "Salads / سلطات": [
                {"name": "Caesar Salad", "name_ar": "سلطة سيزر", "price": 6.0},
                {"name": "Caesar Salad with Chicken", "name_ar": "سلطة سيزر مع دجاج", "price": 8.0},
                {"name": "Greek Salad", "name_ar": "سلطة يونانية", "price": 7.0},
                {"name": "Rocca Salad", "name_ar": "سلطة روكا", "price": 7.0},
                {"name": "Crab Salad", "name_ar": "سلطة سلطعون", "price": 8.0},
            ],
            "Main Plates / أطباق رئيسية": [
                {"name": "Chicken Mushroom", "name_ar": "دجاج بالفطر", "price": 13.0},
                {"name": "Escalope", "name_ar": "اسكالوب", "price": 10.0},
                {"name": "Crispy Chicken", "name_ar": "دجاج مقرمش", "price": 9.0},
                {"name": "Steak au Poivre", "name_ar": "ستيك بالفلفل", "price": 15.0},
                {"name": "Truffle Chicken", "name_ar": "دجاج بالترافل", "price": 15.0},
                {"name": "Truffle Beef", "name_ar": "لحم بالترافل", "price": 17.0},
            ],
            "Beef Burgers / برغر لحم": [
                {"name": "Classic Burger", "name_ar": "برغر كلاسيك", "price": 5.0},
                {"name": "Mushroom Swiss Burger", "name_ar": "برغر فطر سويسري", "price": 7.0},
                {"name": "BBQ Burger", "name_ar": "برغر باربكيو", "price": 7.5},
                {"name": "Truffle Burger", "name_ar": "برغر ترافل", "price": 8.0},
                {"name": "Callisto Burger", "name_ar": "برغر كاليستو", "price": 5.5},
            ],
            "Chicken Burgers / برغر دجاج": [
                {"name": "Fried Chicken Burger", "name_ar": "برغر دجاج مقلي", "price": 6.5},
                {"name": "Ranch Chicken Burger", "name_ar": "برغر دجاج رانش", "price": 7.0},
                {"name": "Zinger Burger", "name_ar": "برغر زنجر", "price": 6.5},
            ],
            "Pizza / بيتزا": [
                {"name": "Margherita", "name_ar": "مارغريتا", "variants": [("Small", 5.0), ("Medium", 7.0), ("Large", 10.0)]},
                {"name": "Pepperoni", "name_ar": "بيبروني", "variants": [("Small", 8.0), ("Medium", 11.0), ("Large", 14.0)]},
                {"name": "Vegetarian", "name_ar": "نباتية", "variants": [("Small", 7.0), ("Medium", 10.0), ("Large", 14.0)]},
                {"name": "Supreme", "name_ar": "سوبريم", "variants": [("Small", 9.0), ("Medium", 12.0), ("Large", 15.0)]},
                {"name": "BBQ Chicken", "name_ar": "دجاج باربكيو", "variants": [("Small", 9.0), ("Medium", 12.0), ("Large", 16.0)]},
                {"name": "Hawaiian", "name_ar": "هاوايان", "variants": [("Small", 8.0), ("Medium", 11.0), ("Large", 14.0)]},
                {"name": "Truffle Pizza", "name_ar": "بيتزا ترافل", "variants": [("Small", 11.0), ("Medium", 12.0), ("Large", 16.0)]},
                {"name": "Callisto Pizza", "name_ar": "بيتزا كاليستو", "variants": [("Small", 11.0), ("Medium", 13.0), ("Large", 18.0)]},
            ],
            "Sandwiches / سندويشات": [
                {"name": "Chicken Sub", "name_ar": "تشيكن سب", "price": 6.0},
                {"name": "Fajita", "name_ar": "فاهيتا", "price": 7.0},
                {"name": "Tawouk", "name_ar": "طاووق", "price": 5.5},
                {"name": "Philadelphia", "name_ar": "فيلادلفيا", "price": 8.5},
            ],
            "Pasta / باستا": [
                {"name": "Fettuccini Alfredo", "name_ar": "فيتوتشيني ألفريدو", "price": 9.0},
                {"name": "Chicken Pesto", "name_ar": "دجاج بيستو", "price": 9.0},
                {"name": "Shrimp Pasta", "name_ar": "باستا قريدس", "price": 10.0},
                {"name": "Arabiata", "name_ar": "أرابياتا", "price": 7.5},
            ],
            "Drinks / مشروبات": [
                {"name": "Soft Drinks", "name_ar": "مشروبات غازية", "price": 1.2},
                {"name": "Water", "name_ar": "مياه", "price": 0.5},
                {"name": "Ice Tea", "name_ar": "شاي مثلج", "price": 1.5},
            ],
        }
    },
    {
        "name": "Soubra's",
        "name_ar": "صبرا",
        "category": "Burgers",
        "menu": {
            "Appetizers / مقبلات": [
                {"name": "Mozzarella Sticks", "name_ar": "أصابع موزاريلا", "price": 6.0},
                {"name": "Cheddar Bricks", "name_ar": "مكعبات شيدر", "price": 7.0},
                {"name": "Halloumi Sticks", "name_ar": "أصابع حلوم", "price": 7.0},
                {"name": "BBQ Wings", "name_ar": "أجنحة باربكيو", "price": 6.0},
                {"name": "Chicken Tenders", "name_ar": "تندرز دجاج", "price": 6.0},
                {"name": "Mini Burger", "name_ar": "ميني برغر", "price": 3.5},
            ],
            "Fries / بطاطا": [
                {"name": "Cheesy Fries", "name_ar": "بطاطا بالجبنة", "price": 8.0},
                {"name": "Legendary Cheesy Fries", "name_ar": "بطاطا أسطورية", "price": 11.0},
                {"name": "Fries Box", "name_ar": "علبة بطاطا", "price": 3.5},
                {"name": "Twister Fries", "name_ar": "بطاطا تويستر", "price": 6.5},
            ],
            "Shawarma / شاورما": [
                {"name": "Chicken Shawarma", "name_ar": "شاورما دجاج", "variants": [("Small", 3.0), ("Medium", 5.0), ("Large", 6.0)]},
                {"name": "Beef Shawarma", "name_ar": "شاورما لحم", "variants": [("Small", 3.0), ("Medium", 5.0), ("Large", 6.0)]},
                {"name": "Chicken Shawarma Plate", "name_ar": "صحن شاورما دجاج", "price": 12.0},
                {"name": "Beef Shawarma Plate", "name_ar": "صحن شاورما لحم", "price": 12.0},
                {"name": "Shawarma Mix Plate", "name_ar": "صحن شاورما مشكل", "price": 13.0},
            ],
            "Beef Burgers / برغر لحم": [
                {"name": "Lebanese Burger", "name_ar": "برغر لبناني", "price": 6.5},
                {"name": "Soubra's Classic", "name_ar": "صبرا كلاسيك", "price": 6.5},
                {"name": "Pablo Beef", "name_ar": "بابلو لحم", "price": 8.5},
                {"name": "Mushroom Beef", "name_ar": "برغر فطر لحم", "price": 8.5},
                {"name": "Honeymozz Beef", "name_ar": "هني موز لحم", "price": 9.0},
                {"name": "24K Burger", "name_ar": "برغر 24 قيراط", "price": 9.5},
            ],
            "Chicken Burgers / برغر دجاج": [
                {"name": "Classic Grilled Chicken", "name_ar": "دجاج مشوي كلاسيك", "price": 6.5},
                {"name": "Caesar Burger", "name_ar": "برغر سيزر", "price": 6.0},
                {"name": "Pablo Chicken", "name_ar": "بابلو دجاج", "price": 8.0},
                {"name": "Honeymozz Chicken", "name_ar": "هني موز دجاج", "price": 8.5},
            ],
            "Fried Chicken Burgers / برغر دجاج مقلي": [
                {"name": "Classic Fried", "name_ar": "مقلي كلاسيك", "price": 6.5},
                {"name": "Honey Bunny", "name_ar": "هني باني", "price": 8.5},
                {"name": "Crunchy", "name_ar": "كرانشي", "price": 7.0},
                {"name": "Zeus", "name_ar": "زيوس", "price": 7.5},
            ],
            "Sandwiches / سندويشات": [
                {"name": "Tawouk Sandwich", "name_ar": "سندويش طاووق", "price": 6.0},
                {"name": "Chicken Sub", "name_ar": "تشيكن سب", "price": 6.0},
                {"name": "Fajita", "name_ar": "فاهيتا", "price": 7.0},
                {"name": "Soubra's Steak", "name_ar": "ستيك صبرا", "price": 8.0},
            ],
            "Platters / أطباق": [
                {"name": "Tawouk Platter", "name_ar": "صحن طاووق", "price": 12.0},
                {"name": "Crispy Platter", "name_ar": "صحن كريسبي", "price": 10.0},
                {"name": "Entrecote Steak", "name_ar": "ستيك أنتريكوت", "price": 17.0},
                {"name": "Soubra's Majesty Steak", "name_ar": "ستيك ماجستي", "price": 25.0},
                {"name": "Fish & Chips", "name_ar": "فيش أند شيبس", "price": 10.0},
            ],
            "Drinks / مشروبات": [
                {"name": "Soft Drinks", "name_ar": "مشروبات غازية", "price": 1.5},
                {"name": "Water", "name_ar": "مياه", "price": 0.5},
                {"name": "Ayran", "name_ar": "عيران", "price": 1.5},
            ],
        }
    },
]


async def seed_categories(db: AsyncSession):
    """Seed restaurant categories - only creates missing ones"""
    from sqlalchemy import select
    
    # Get existing categories
    result = await db.execute(select(RestaurantCategory))
    existing = {c.name: c for c in result.scalars().all()}
    
    created = 0
    for cat_data in CATEGORIES:
        if cat_data["name"] not in existing:
            cat = RestaurantCategory(**cat_data)
            db.add(cat)
            created += 1
    
    await db.commit()
    print(f"✅ Categories: {created} created, {len(existing)} already existed")



async def seed_restaurants(db: AsyncSession):
    """Seed restaurants with menus"""
    # Get categories
    from sqlalchemy import select
    result = await db.execute(select(RestaurantCategory))
    categories = {c.name: c.id for c in result.scalars().all()}
    
    for rest_data in RESTAURANTS_DATA:
        # Create restaurant
        restaurant = Restaurant(
            name=rest_data["name"],
            name_ar=rest_data["name_ar"],
            category_id=categories.get(rest_data["category"]),
            is_active=True,
        )
        db.add(restaurant)
        await db.flush()
        
        # Create default branch
        branch = Branch(
            restaurant_id=restaurant.id,
            name="Main Branch",
            is_active=True,
        )
        db.add(branch)
        
        # Create menu
        menu = Menu(
            restaurant_id=restaurant.id,
            name="Main Menu",
            name_ar="القائمة الرئيسية",
        )
        db.add(menu)
        await db.flush()
        
        # Create categories and items
        cat_order = 0
        for cat_name, items in rest_data["menu"].items():
            # Split bilingual category name
            if " / " in cat_name:
                name_en, name_ar = cat_name.split(" / ")
            else:
                name_en = name_ar = cat_name
            
            category = Category(
                menu_id=menu.id,
                name=name_en,
                name_ar=name_ar,
                order=cat_order,
            )
            db.add(category)
            await db.flush()
            cat_order += 1
            
            # Add items
            item_order = 0
            for item_data in items:
                has_variants = "variants" in item_data
                
                if has_variants:
                    variants = item_data["variants"]
                    prices = [v[1] for v in variants]
                    price_min = min(prices)
                    price_max = max(prices)
                    
                    menu_item = MenuItem(
                        category_id=category.id,
                        name=item_data["name"],
                        name_ar=item_data["name_ar"],
                        description=item_data.get("desc"),
                        description_ar=item_data.get("desc_ar"),
                        has_variants=True,
                        price_min=price_min,
                        price_max=price_max,
                        order=item_order,
                    )
                    db.add(menu_item)
                    await db.flush()
                    
                    # Add variants
                    for var_order, (size_name, price) in enumerate(variants):
                        variant = MenuItemVariant(
                            menu_item_id=menu_item.id,
                            name=size_name,
                            name_ar=SIZES.get(size_name, size_name),
                            price=price,
                            order=var_order,
                        )
                        db.add(variant)
                else:
                    menu_item = MenuItem(
                        category_id=category.id,
                        name=item_data["name"],
                        name_ar=item_data["name_ar"],
                        description=item_data.get("desc"),
                        description_ar=item_data.get("desc_ar"),
                        price=item_data["price"],
                        has_variants=False,
                        order=item_order,
                    )
                    db.add(menu_item)
                
                item_order += 1
        
        print(f"✅ Seeded: {rest_data['name']}")
    
    await db.commit()


async def main():
    async with AsyncSessionLocal() as db:
        print("🚀 Starting seed...")
        await seed_categories(db)
        await seed_restaurants(db)
        print("✅ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
