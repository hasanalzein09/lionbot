"""
Seed Lebanese Restaurants to Cloud Database
Run: python3 seed_cloud_restaurants.py
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cloud SQL Connection
DATABASE_URL = "postgresql+asyncpg://lionbot:LionBot2024@163.245.208.160:5432/lionbot"

engine = create_async_engine(DATABASE_URL, echo=False, pool_timeout=60)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# LBP to USD Rate
LBP_RATE = 90000

# Size translations
SIZES = {
    "Small": "صغير", "Medium": "وسط", "Large": "كبير",
    "S": "صغير", "M": "وسط", "L": "كبير",
    "20cm": "٢٠ سم", "25cm": "٢٥ سم",
}

# ===========================================
# RESTAURANT DATA - 26 Lebanese Restaurants
# ===========================================

RESTAURANTS = [
    # ========== PIZZA ==========
    {
        "name": "Callisto", "name_ar": "كاليستو", "category": "Pizza",
        "menu": {
            "Appetizers / مقبلات": [
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 5.0},
                {"n": "Cheese Garlic Bread", "ar": "خبز بالثوم والجبنة", "p": 5.0},
                {"n": "Chicken Wings", "ar": "أجنحة دجاج", "p": 6.0},
                {"n": "Cheesy Fries", "ar": "بطاطا بالجبنة", "p": 7.0},
                {"n": "French Fries", "ar": "بطاطا مقلية", "p": 3.0},
                {"n": "Truffle Fries", "ar": "بطاطا بالترافل", "p": 8.0},
                {"n": "Onion Rings", "ar": "حلقات البصل", "p": 4.0},
                {"n": "Callisto Combo", "ar": "كومبو كاليستو", "p": 12.0},
            ],
            "Salads / سلطات": [
                {"n": "Caesar Salad", "ar": "سلطة سيزر", "p": 6.0},
                {"n": "Caesar with Chicken", "ar": "سيزر مع دجاج", "p": 8.0},
                {"n": "Greek Salad", "ar": "سلطة يونانية", "p": 7.0},
                {"n": "Crab Salad", "ar": "سلطة سلطعون", "p": 8.0},
            ],
            "Pizza / بيتزا": [
                {"n": "Margherita", "ar": "مارغريتا", "v": [("Small", 5.0), ("Medium", 7.0), ("Large", 10.0)]},
                {"n": "Pepperoni", "ar": "بيبروني", "v": [("Small", 8.0), ("Medium", 11.0), ("Large", 14.0)]},
                {"n": "Vegetarian", "ar": "نباتية", "v": [("Small", 7.0), ("Medium", 10.0), ("Large", 14.0)]},
                {"n": "Supreme", "ar": "سوبريم", "v": [("Small", 9.0), ("Medium", 12.0), ("Large", 15.0)]},
                {"n": "BBQ Chicken", "ar": "دجاج باربكيو", "v": [("Small", 9.0), ("Medium", 12.0), ("Large", 16.0)]},
                {"n": "Hawaiian", "ar": "هاوايان", "v": [("Small", 8.0), ("Medium", 11.0), ("Large", 14.0)]},
                {"n": "Truffle Pizza", "ar": "بيتزا ترافل", "v": [("Small", 11.0), ("Medium", 12.0), ("Large", 16.0)]},
            ],
            "Burgers / برغر": [
                {"n": "Classic Burger", "ar": "برغر كلاسيك", "p": 5.0},
                {"n": "BBQ Burger", "ar": "برغر باربكيو", "p": 7.5},
                {"n": "Truffle Burger", "ar": "برغر ترافل", "p": 8.0},
                {"n": "Zinger Burger", "ar": "برغر زينجر", "p": 6.5},
            ],
            "Pasta / باستا": [
                {"n": "Fettuccini Alfredo", "ar": "فيتوتشيني ألفريدو", "p": 9.0},
                {"n": "Chicken Pesto", "ar": "دجاج بيستو", "p": 9.0},
                {"n": "Shrimp Pasta", "ar": "باستا قريدس", "p": 10.0},
            ],
            "Drinks / مشروبات": [
                {"n": "Soft Drinks", "ar": "مشروبات غازية", "p": 1.2},
                {"n": "Water", "ar": "مياه", "p": 0.5},
            ],
        }
    },
    {
        "name": "Papa Joe", "name_ar": "بابا جو", "category": "Pizza",
        "menu": {
            "Pizza / بيتزا": [
                {"n": "Margarita", "ar": "مارغريتا", "v": [("S", 7.0), ("M", 8.0), ("L", 10.0)]},
                {"n": "Four Cheese", "ar": "أربع أجبان", "v": [("S", 8.0), ("M", 10.0), ("L", 12.0)]},
                {"n": "Pepperoni", "ar": "بيبروني", "v": [("S", 10.0), ("M", 12.0), ("L", 15.0)]},
                {"n": "Chicken BBQ", "ar": "دجاج باربكيو", "v": [("S", 9.0), ("M", 12.0), ("L", 14.0)]},
                {"n": "Teriyaki Chicken", "ar": "دجاج تيرياكي", "v": [("S", 10.0), ("M", 13.0), ("L", 16.0)]},
                {"n": "Philly Steak", "ar": "فيلي ستيك", "v": [("S", 11.0), ("M", 14.0), ("L", 17.0)]},
            ],
            "Appetizers / مقبلات": [
                {"n": "French Fries", "ar": "بطاطا مقلية", "p": 3.0},
                {"n": "Wedges", "ar": "ويدجز", "p": 4.0},
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 7.0},
                {"n": "Chicken Wings", "ar": "أجنحة دجاج", "p": 7.0},
                {"n": "Crispy Chicken", "ar": "دجاج مقرمش", "p": 8.0},
            ],
            "Salads / سلطات": [
                {"n": "Greek Salad", "ar": "سلطة يونانية", "p": 5.0},
                {"n": "Caesar Salad", "ar": "سلطة سيزر", "p": 5.0},
                {"n": "Chicken Caesar", "ar": "سيزر مع دجاج", "p": 8.0},
            ],
        }
    },
    
    # ========== BURGERS ==========
    {
        "name": "Soubra's", "name_ar": "صبرا", "category": "Burgers",
        "menu": {
            "Appetizers / مقبلات": [
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 6.0},
                {"n": "Cheddar Bricks", "ar": "مكعبات شيدر", "p": 7.0},
                {"n": "Halloumi Sticks", "ar": "أصابع حلوم", "p": 7.0},
                {"n": "BBQ Wings", "ar": "أجنحة باربكيو", "p": 6.0},
                {"n": "Chicken Tenders", "ar": "تندرز دجاج", "p": 6.0},
            ],
            "Fries / بطاطا": [
                {"n": "Cheesy Fries", "ar": "بطاطا بالجبنة", "p": 8.0},
                {"n": "Legendary Fries", "ar": "بطاطا أسطورية", "p": 11.0},
                {"n": "Fries Box", "ar": "علبة بطاطا", "p": 3.5},
            ],
            "Shawarma / شاورما": [
                {"n": "Chicken Shawarma", "ar": "شاورما دجاج", "v": [("Small", 3.0), ("Medium", 5.0), ("Large", 6.0)]},
                {"n": "Beef Shawarma", "ar": "شاورما لحم", "v": [("Small", 3.0), ("Medium", 5.0), ("Large", 6.0)]},
            ],
            "Beef Burgers / برغر لحم": [
                {"n": "Lebanese Burger", "ar": "برغر لبناني", "p": 6.5},
                {"n": "Soubra's Classic", "ar": "صبرا كلاسيك", "p": 6.5},
                {"n": "Pablo Beef", "ar": "بابلو لحم", "p": 8.5},
                {"n": "Mushroom Beef", "ar": "برغر فطر لحم", "p": 8.5},
                {"n": "24K Burger", "ar": "برغر ٢٤ قيراط", "p": 9.5},
            ],
            "Chicken Burgers / برغر دجاج": [
                {"n": "Classic Grilled", "ar": "دجاج مشوي كلاسيك", "p": 6.5},
                {"n": "Honey Bunny", "ar": "هني باني", "p": 8.5},
                {"n": "Crunchy", "ar": "كرانشي", "p": 7.0},
            ],
            "Platters / أطباق": [
                {"n": "Tawouk Platter", "ar": "صحن طاووق", "p": 12.0},
                {"n": "Crispy Platter", "ar": "صحن كريسبي", "p": 10.0},
                {"n": "Entrecote Steak", "ar": "ستيك أنتريكوت", "p": 17.0},
            ],
        }
    },
    {
        "name": "Burgero", "name_ar": "برغيرو", "category": "Burgers",
        "menu": {
            "Beef Burgers / برغر لحم": [
                {"n": "Classic Burger", "ar": "برغر كلاسيك", "p": 6.5},
                {"n": "The Lebanese", "ar": "اللبناني", "p": 6.5},
                {"n": "The Burgero", "ar": "البرغيرو", "p": 8.5},
                {"n": "Mushroom Vibes", "ar": "فطر فايبز", "p": 9.0},
                {"n": "Truffle Burger", "ar": "برغر ترافل", "p": 10.0},
                {"n": "The Smash", "ar": "السماش", "p": 9.0},
                {"n": "Giant Burger", "ar": "البرغر العملاق", "p": 10.0},
            ],
            "Fried Chicken / دجاج مقلي": [
                {"n": "Classic Fried", "ar": "مقلي كلاسيك", "p": 6.5},
                {"n": "Fried Honey Bun", "ar": "هني بن مقلي", "p": 9.0},
                {"n": "Buffalo Bomb", "ar": "بافلو بومب", "p": 9.0},
            ],
            "Appetizers / مقبلات": [
                {"n": "French Fries", "ar": "بطاطا مقلية", "p": 4.5},
                {"n": "Curly Fries", "ar": "بطاطا حلزونية", "p": 5.0},
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 5.5},
                {"n": "Chicken Wings", "ar": "أجنحة دجاج", "p": 3.5},
                {"n": "Onion Rings", "ar": "حلقات البصل", "p": 3.5},
            ],
            "Desserts / حلويات": [
                {"n": "NY Cheesecake", "ar": "تشيزكيك نيويورك", "p": 7.0},
                {"n": "Brownies Ice Cream", "ar": "براوني مع آيس كريم", "p": 7.0},
                {"n": "Milkshakes", "ar": "ميلك شيك", "p": 5.5},
            ],
        }
    },
    {
        "name": "Al Ghali", "name_ar": "الغالي", "category": "Burgers",
        "menu": {
            "Burgers / برغر": [
                {"n": "Crunchy Burger", "ar": "كرنشي برغر", "p": 3.9},
                {"n": "Al Ghali Burger", "ar": "برغر الغالي", "p": 4.4},
                {"n": "Classico Burger", "ar": "كلاسيكو برغر", "p": 4.4},
                {"n": "Lebanese Burger", "ar": "برغر لبناني", "p": 3.3},
                {"n": "Mushroom Burger", "ar": "برغر فطر", "p": 5.0},
                {"n": "Honey Butter", "ar": "هاني باتر", "p": 5.0},
            ],
            "Sandwiches / سندويشات": [
                {"n": "Fajita", "ar": "فاهيتا", "p": 4.2},
                {"n": "Chicken Sub", "ar": "تشيكن سب", "p": 3.9},
                {"n": "Steak Sub", "ar": "ستيك سب", "p": 4.2},
                {"n": "Crispy", "ar": "كريسبي", "p": 3.3},
            ],
            "Appetizers / مقبلات": [
                {"n": "French Fries Large", "ar": "بطاطا كبير", "p": 3.3},
                {"n": "French Fries Small", "ar": "بطاطا صغير", "p": 2.2},
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 3.9},
            ],
            "Grills / مشاوي": [
                {"n": "Grilled Chicken", "ar": "دجاج مشوي", "p": 7.8},
                {"n": "Scallopini", "ar": "سكالوبيني", "p": 7.8},
                {"n": "Mixed Grill 1kg", "ar": "مشاوي مشكل كيلو", "p": 13.9},
            ],
        }
    },
    {
        "name": "Heartache", "name_ar": "هارتايك", "category": "Burgers",
        "menu": {
            "Appetizers / مقبلات": [
                {"n": "Fries", "ar": "بطاطا", "p": 2.2},
                {"n": "Cheese Fries", "ar": "بطاطا بالجبنة", "p": 3.3},
                {"n": "Crispy Loaded Fries", "ar": "بطاطا محملة كريسبي", "p": 5.0},
            ],
            "Sandwiches / سندويشات": [
                {"n": "Escalope", "ar": "اسكالوب", "p": 3.3},
                {"n": "Tawook", "ar": "طاووق", "p": 3.1},
                {"n": "Francisco", "ar": "فرانسيسكو", "p": 4.1},
                {"n": "Fajita", "ar": "فاهيتا", "p": 4.7},
                {"n": "Chicken Sub", "ar": "تشيكن سب", "p": 4.4},
            ],
            "Burgers / برغر": [
                {"n": "Mushroom Burger", "ar": "برغر فطر", "p": 5.0},
                {"n": "Lebanese Burger", "ar": "برغر لبناني", "p": 4.1},
                {"n": "Zinger", "ar": "زينجر", "p": 4.6},
                {"n": "Smashed Burger", "ar": "سماشد برغر", "p": 4.7},
            ],
        }
    },
    {
        "name": "Abou Afif", "name_ar": "أبو عفيف", "category": "Sandwiches",
        "menu": {
            "Sandwiches / سندويشات": [
                {"n": "Abou Afif Beef", "ar": "أبو عفيف لحم", "v": [("20cm", 4.4), ("25cm", 5.6)]},
                {"n": "Abou Afif Chicken", "ar": "أبو عفيف دجاج", "v": [("20cm", 4.4), ("25cm", 5.6)]},
                {"n": "Francisco", "ar": "فرانسيسكو", "v": [("20cm", 4.4), ("25cm", 5.6)]},
                {"n": "Chicken Sub", "ar": "تشيكن سب", "v": [("20cm", 4.4), ("25cm", 5.6)]},
                {"n": "Escalope", "ar": "اسكالوب", "v": [("20cm", 4.4), ("25cm", 5.6)]},
                {"n": "Tawouk", "ar": "طاووق", "v": [("20cm", 4.4), ("25cm", 5.6)]},
            ],
            "Burgers / برغر": [
                {"n": "Cheese Burger", "ar": "تشيز برغر", "p": 5.0},
                {"n": "Escalope Bun", "ar": "اسكالوب بن", "p": 5.0},
            ],
            "Sweet / حلو": [
                {"n": "Nutella", "ar": "نوتيلا", "v": [("20cm", 4.4), ("25cm", 5.6)]},
                {"n": "Halawa Butter", "ar": "حلاوة وزبدة", "v": [("20cm", 4.4), ("25cm", 5.6)]},
            ],
        }
    },
    
    # ========== SHAWARMA ==========
    {
        "name": "Farid Al Shawarma", "name_ar": "فريد الشاورما", "category": "Shawarma",
        "menu": {
            "Sandwiches / سندويشات": [
                {"n": "Chicken Shawarma", "ar": "شاورما دجاج", "v": [("Small", 2.2), ("Medium", 2.8), ("Large", 3.3)]},
                {"n": "Beef Shawarma", "ar": "شاورما لحم", "v": [("Small", 2.8), ("Medium", 3.3), ("Large", 3.9)]},
                {"n": "Mixed Grill", "ar": "مشاوي مشكل", "v": [("Small", 2.2), ("Medium", 2.8), ("Large", 3.3)]},
            ],
            "Kilos / كيلو": [
                {"n": "Beef Shawarma Half Kilo", "ar": "شاورما لحم نص كيلو", "p": 15.0},
                {"n": "Beef Shawarma 1 Kilo", "ar": "شاورما لحم كيلو", "p": 30.0},
                {"n": "Chicken Shawarma Half Kilo", "ar": "شاورما دجاج نص كيلو", "p": 11.0},
                {"n": "Chicken Shawarma 1 Kilo", "ar": "شاورما دجاج كيلو", "p": 22.0},
            ],
            "Fries / بطاطا": [
                {"n": "Fries Plate", "ar": "صحن بطاطا", "p": 3.9},
                {"n": "Fries Box", "ar": "علبة بطاطا", "p": 2.2},
            ],
        }
    },
    
    # ========== SNACKS ==========
    {
        "name": "Spuntino", "name_ar": "سبونتينو", "category": "Snacks",
        "menu": {
            "Burgers / برغر": [
                {"n": "Beef BBQ", "ar": "لحم باربكيو", "p": 6.5},
                {"n": "Mushroom Burger", "ar": "برغر فطر", "p": 8.5},
                {"n": "Zinger", "ar": "زينجر", "p": 5.5},
                {"n": "Mighty Zinger", "ar": "مايتي زينجر", "p": 8.5},
                {"n": "Mozzarella Burger", "ar": "برغر موزاريلا", "p": 8.5},
                {"n": "Spuntino Burger", "ar": "برغر سبونتينو", "p": 6.5},
            ],
            "Sandwiches / سندويشات": [
                {"n": "Chicken Sub", "ar": "تشيكن سب", "p": 5.5},
                {"n": "Fajita", "ar": "فاهيتا", "p": 7.5},
                {"n": "Twister", "ar": "تويستر", "p": 4.9},
                {"n": "Crispy Sandwich", "ar": "سندويش كريسبي", "p": 5.5},
            ],
            "Fried Chicken / دجاج مقلي": [
                {"n": "Family Crispy 10pcs", "ar": "عائلي كريسبي ١٠ قطع", "p": 21.8},
                {"n": "Family Crispy 15pcs", "ar": "عائلي كريسبي ١٥ قطع", "p": 32.5},
                {"n": "Crispy Meal 3pcs", "ar": "وجبة كريسبي ٣ قطع", "p": 8.9},
                {"n": "Crispy Meal 5pcs", "ar": "وجبة كريسبي ٥ قطع", "p": 10.6},
            ],
            "Appetizers / مقبلات": [
                {"n": "Curly Fries", "ar": "بطاطا حلزونية", "p": 4.8},
                {"n": "Wedges", "ar": "ويدجز", "p": 4.0},
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 4.5},
                {"n": "Wings 8pcs", "ar": "أجنحة ٨ قطع", "p": 7.5},
            ],
        }
    },
    {
        "name": "Boneless", "name_ar": "بونلس", "category": "Snacks",
        "menu": {
            "Wraps / راب": [
                {"n": "BBQ Wrap", "ar": "راب باربكيو", "p": 5.5},
                {"n": "Buffalo Wrap", "ar": "راب بافلو", "p": 5.5},
                {"n": "Honey Mustard Wrap", "ar": "راب هني مستارد", "p": 5.5},
            ],
            "Boxes / بوكسات": [
                {"n": "French Fries Box", "ar": "بوكس بطاطا", "p": 3.0},
                {"n": "Wedges Box", "ar": "بوكس ويدجز", "p": 3.5},
                {"n": "Curly Fries", "ar": "بطاطا حلزونية", "p": 4.0},
                {"n": "Loaded Fries", "ar": "بطاطا محملة", "p": 5.0},
                {"n": "Boneless Box", "ar": "بوكس بونلس", "p": 5.5},
                {"n": "The Big Deal", "ar": "ذا بيغ ديل", "p": 7.5},
            ],
        }
    },
    
    # ========== HOME FOOD (BAKERY) ==========
    {
        "name": "Mr. Croissant", "name_ar": "مستر كرواسون", "category": "Home Food",
        "menu": {
            "Salty / مالح": [
                {"n": "Zaatar", "ar": "زعتر", "p": 0.56},
                {"n": "Akkawi Cheese", "ar": "جبنة عكاوي", "p": 1.3},
                {"n": "Kashkaval", "ar": "قشقوان", "p": 1.8},
                {"n": "Mozzarella", "ar": "موزاريلا", "p": 1.8},
                {"n": "Halloumi", "ar": "حلوم", "p": 1.8},
                {"n": "Two Cheeses", "ar": "جبنتين", "p": 2.2},
                {"n": "Tawouk Cheese", "ar": "طاووق وجبنة", "p": 3.6},
                {"n": "Fajita Croissant", "ar": "كرواسون فاهيتا", "p": 3.9},
            ],
            "Pizza Croissant / بيتزا كرواسون": [
                {"n": "Pepperoni Cheese", "ar": "بيبروني وجبنة", "p": 3.6},
                {"n": "Veggie Pizza", "ar": "بيتزا خضار", "p": 3.0},
                {"n": "Sojok Pizza", "ar": "بيتزا سجق", "p": 3.9},
            ],
            "Sweet / حلو": [
                {"n": "Plain Croissant", "ar": "كرواسون سادة", "p": 0.78},
                {"n": "Chocolate", "ar": "شوكولا", "p": 1.1},
                {"n": "Nutella", "ar": "نوتيلا", "p": 1.8},
                {"n": "Oreo", "ar": "أوريو", "p": 1.8},
                {"n": "Lotus", "ar": "لوتس", "p": 1.8},
                {"n": "Kinder", "ar": "كيندر", "p": 1.8},
                {"n": "Pistachio", "ar": "فستق", "p": 2.8},
                {"n": "Kunafa", "ar": "كنافة", "p": 3.3},
            ],
        }
    },
    {
        "name": "King Croissant", "name_ar": "كينغ كرواسون", "category": "Home Food",
        "menu": {
            "Salty / مالح": [
                {"n": "Zaatar", "ar": "زعتر", "p": 0.67},
                {"n": "Akkawi Cheese", "ar": "جبنة عكاوي", "p": 1.3},
                {"n": "Cheese Turkey", "ar": "جبنة وحبش", "p": 2.8},
                {"n": "Pizza Croissant", "ar": "بيتزا كرواسون", "p": 3.3},
                {"n": "Sojok Cheese", "ar": "سجق وجبنة", "p": 3.6},
                {"n": "Tawouk Cheese", "ar": "طاووق وجبنة", "p": 3.9},
                {"n": "Fajita", "ar": "فاهيتا", "p": 4.2},
            ],
            "Sweet / حلو": [
                {"n": "Chocolate", "ar": "شوكولا", "p": 1.1},
                {"n": "Nutella", "ar": "نوتيلا", "p": 2.0},
                {"n": "Lotus", "ar": "لوتس", "p": 2.4},
                {"n": "Oreo", "ar": "أوريو", "p": 2.2},
                {"n": "Kinder", "ar": "كيندر", "p": 2.8},
                {"n": "Pistachio", "ar": "فستق", "p": 3.3},
                {"n": "Kunafa Croissant", "ar": "كرواسون كنافة", "p": 3.9},
                {"n": "Giant Croissant", "ar": "كرواسون عملاق", "p": 10.6},
            ],
            "Drinks / مشروبات": [
                {"n": "Fresh Orange Juice", "ar": "عصير برتقال طازج", "p": 1.7},
                {"n": "Soft Drinks", "ar": "مشروبات غازية", "p": 1.1},
            ],
        }
    },
    {
        "name": "Neswan Al Forn", "name_ar": "نسوان الفرن", "category": "Home Food",
        "menu": {
            "Bakery / مخبوزات": [
                {"n": "Zaatar", "ar": "زعتر", "p": 0.67},
                {"n": "Akkawi Cheese", "ar": "جبنة عكاوي", "p": 2.0},
                {"n": "Kishk", "ar": "كشك", "p": 1.3},
                {"n": "Zaatar Cheese Mix", "ar": "زعتر وجبنة", "p": 1.6},
                {"n": "Spinach Fatayer", "ar": "فطاير سبانخ", "p": 0.56},
                {"n": "Veggie Pizza", "ar": "بيتزا خضار", "p": 3.9},
                {"n": "Lahm Bi Ajeen", "ar": "لحم بعجين", "p": 2.2},
            ],
        }
    },
    {
        "name": "Foron Al Sheikh", "name_ar": "فرن الشيخ", "category": "Home Food",
        "menu": {
            "Bakery / مخبوزات": [
                {"n": "Cheese", "ar": "جبنة", "p": 2.0},
                {"n": "Cheese Stretched", "ar": "جبنة مشروحة", "p": 3.3},
                {"n": "Kishk Cheese", "ar": "كشك وجبنة", "p": 2.4},
                {"n": "Mortadella", "ar": "مرتديلا", "p": 2.9},
                {"n": "Sojok", "ar": "سجق", "p": 2.9},
                {"n": "Meat", "ar": "لحمة", "p": 2.9},
                {"n": "Zaatar", "ar": "زعتر", "p": 0.56},
                {"n": "Halloumi Kashkaval", "ar": "حلوم وقشقوان", "p": 3.6},
                {"n": "Tawouk Mix", "ar": "طاووق مشكل", "p": 3.8},
                {"n": "Pepperoni Mix", "ar": "بيبروني مشكل", "p": 3.9},
            ],
        }
    },
    {
        "name": "Forn Yassin", "name_ar": "فرن ياسين", "category": "Home Food",
        "menu": {
            "Bakery / مخبوزات": [
                {"n": "Cheese", "ar": "جبنة", "p": 1.7},
                {"n": "Zaatar", "ar": "زعتر", "p": 0.67},
                {"n": "Kishk", "ar": "كشك", "p": 1.1},
                {"n": "Cheese Kashkaval", "ar": "جبنة قشقوان", "p": 2.8},
                {"n": "Pizza Small", "ar": "بيتزا صغير", "p": 4.4},
                {"n": "Pizza Medium", "ar": "بيتزا وسط", "p": 7.8},
                {"n": "Pizza Large", "ar": "بيتزا كبير", "p": 10.0},
                {"n": "Sojok", "ar": "سجق", "p": 2.8},
                {"n": "Turkey", "ar": "حبش", "p": 3.3},
                {"n": "Shawarma", "ar": "شاورما", "p": 3.3},
            ],
        }
    },
    
    # ========== SANDWICHES ==========
    {
        "name": "Sandwich Bar", "name_ar": "ساندويش بار", "category": "Sandwiches",
        "menu": {
            "Sandwiches / سندويشات": [
                {"n": "Philadelphia", "ar": "فيلادلفيا", "p": 8.0},
                {"n": "Steak Sub", "ar": "ستيك سب", "p": 7.5},
                {"n": "Roast Beef", "ar": "روست بيف", "p": 5.5},
                {"n": "Sojok", "ar": "سجق", "p": 5.0},
                {"n": "Francisco", "ar": "فرانسيسكو", "p": 6.5},
                {"n": "Fajita", "ar": "فاهيتا", "p": 6.5},
                {"n": "Chicken Sub", "ar": "تشيكن سب", "p": 6.0},
                {"n": "Escalope", "ar": "اسكالوب", "p": 5.5},
                {"n": "Tawouk", "ar": "طاووق", "p": 5.0},
            ],
            "Burgers / برغر": [
                {"n": "Classic Burger", "ar": "برغر كلاسيك", "p": 5.5},
                {"n": "Cheese Burger", "ar": "تشيز برغر", "p": 6.5},
                {"n": "Chicken Burger", "ar": "برغر دجاج", "p": 6.0},
            ],
            "Appetizers / مقبلات": [
                {"n": "French Fries", "ar": "بطاطا مقلية", "p": 3.0},
                {"n": "Curly Fries", "ar": "بطاطا حلزونية", "p": 4.5},
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 5.0},
                {"n": "Chicken Wings", "ar": "أجنحة دجاج", "p": 6.0},
            ],
        }
    },
    {
        "name": "Snack 88", "name_ar": "سناك ٨٨", "category": "Sandwiches",
        "menu": {
            "Sandwiches / سندويشات": [
                {"n": "Chicken Francisco", "ar": "فرانسيسكو دجاج", "p": 6.5},
                {"n": "Escalope", "ar": "اسكالوب", "p": 6.0},
                {"n": "Fajita", "ar": "فاهيتا", "p": 7.0},
                {"n": "Philadelphia", "ar": "فيلادلفيا", "p": 8.5},
            ],
            "Burgers / برغر": [
                {"n": "Classic Burger", "ar": "برغر كلاسيك", "p": 6.0},
                {"n": "Mozzarella Burger", "ar": "برغر موزاريلا", "p": 8.0},
            ],
            "Appetizers / مقبلات": [
                {"n": "French Fries", "ar": "بطاطا مقلية", "p": 3.0},
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 5.5},
            ],
        }
    },
    {
        "name": "Favorite", "name_ar": "فيفوريت", "category": "Sandwiches",
        "menu": {
            "Sandwiches / سندويشات": [
                {"n": "Classic Burger", "ar": "برغر كلاسيك", "p": 6.5},
                {"n": "Favorite Submarine", "ar": "صب مارين فيفوريت", "p": 8.0},
                {"n": "Chicken Francisco", "ar": "فرانسيسكو دجاج", "p": 7.0},
            ],
            "Appetizers / مقبلات": [
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 5.5},
                {"n": "Chicken Wings", "ar": "أجنحة دجاج", "p": 6.5},
            ],
        }
    },
    {
        "name": "Doener House", "name_ar": "دونر هاوس", "category": "Sandwiches",
        "menu": {
            "Doner / دونر": [
                {"n": "Chicken Doner Sandwich", "ar": "سندويش دونر دجاج", "p": 5.0},
                {"n": "Beef Doner Sandwich", "ar": "سندويش دونر لحم", "p": 6.5},
                {"n": "Mix Doner Sandwich", "ar": "سندويش دونر مشكل", "p": 6.0},
                {"n": "Doner Box with Fries", "ar": "بوكس دونر مع بطاطا", "p": 7.5},
                {"n": "Doner Plate Chicken", "ar": "صحن دونر دجاج", "p": 12.0},
                {"n": "Doner Plate Beef", "ar": "صحن دونر لحم", "p": 14.0},
            ],
        }
    },
    {
        "name": "Hayat Doner", "name_ar": "حياة دونر", "category": "Sandwiches",
        "menu": {
            "Turkish Doner / دونر تركي": [
                {"n": "Tombik Doner Chicken", "ar": "تومبيك دونر دجاج", "p": 5.0},
                {"n": "Tombik Doner Beef", "ar": "تومبيك دونر لحم", "p": 6.5},
                {"n": "Durum Wrap Chicken", "ar": "دوروم دجاج", "p": 4.5},
                {"n": "Durum Wrap Beef", "ar": "دوروم لحم", "p": 6.0},
                {"n": "Iskender Kebab", "ar": "اسكندر كباب", "p": 13.0},
            ],
        }
    },
    
    # ========== SWEETS ==========
    {
        "name": "Dulce", "name_ar": "دولتشي", "category": "Sweets",
        "menu": {
            "Desserts / حلويات": [
                {"n": "Classic Pain Perdu", "ar": "بان بيردو كلاسيك", "p": 10.0},
                {"n": "Nutella Pain Perdu", "ar": "بان بيردو نوتيلا", "p": 12.0},
                {"n": "Fettuccine Crepe", "ar": "كريب فيتوتشيني", "p": 9.5},
                {"n": "Sushi Crepe", "ar": "كريب سوشي", "p": 11.0},
                {"n": "Dulce Waffle", "ar": "وافل دولتشي", "p": 8.5},
            ],
            "Food / أكل": [
                {"n": "Fettuccine Alfredo", "ar": "فيتوتشيني ألفريدو", "p": 11.0},
                {"n": "Chicken Escalope", "ar": "اسكالوب دجاج", "p": 10.0},
                {"n": "Classic Beef Burger", "ar": "برغر لحم كلاسيك", "p": 8.5},
            ],
            "Drinks / مشروبات": [
                {"n": "Oreo Milkshake", "ar": "ميلك شيك أوريو", "p": 5.0},
                {"n": "Fresh Orange Juice", "ar": "عصير برتقال طازج", "p": 3.5},
                {"n": "Iced Spanish Latte", "ar": "لاتيه إسباني مثلج", "p": 5.5},
            ],
        }
    },
    {
        "name": "Brunch", "name_ar": "برانش", "category": "Sweets",
        "menu": {
            "Breakfast / فطور": [
                {"n": "Scrambled Eggs", "ar": "بيض مخفوق", "p": 5.0},
                {"n": "Omelette Cheese", "ar": "أومليت جبنة", "p": 6.0},
                {"n": "Avocado Toast", "ar": "توست أفوكادو", "p": 8.5},
                {"n": "Classic Pancake", "ar": "بانكيك كلاسيك", "p": 7.0},
                {"n": "Chocolate Pancake", "ar": "بانكيك شوكولا", "p": 8.5},
                {"n": "French Toast", "ar": "فرنش توست", "p": 9.0},
            ],
            "Drinks / مشروبات": [
                {"n": "Fresh Orange Juice", "ar": "عصير برتقال طازج", "p": 3.5},
                {"n": "Hot Latte", "ar": "لاتيه ساخن", "p": 4.0},
            ],
        }
    },
    
    # ========== GRILLS ==========
    {
        "name": "Akleh", "name_ar": "أكلة", "category": "Grills",
        "menu": {
            "Lebanese / لبناني": [
                {"n": "Hummus", "ar": "حمص", "p": 4.5},
                {"n": "Moutabal", "ar": "متبل", "p": 4.5},
                {"n": "Tabbouleh", "ar": "تبولة", "p": 5.0},
                {"n": "Fattoush", "ar": "فتوش", "p": 5.0},
                {"n": "Mixed Grill Platter", "ar": "صحن مشاوي مشكل", "p": 16.0},
                {"n": "Tawouk Platter", "ar": "صحن طاووق", "p": 12.0},
                {"n": "Kafta Platter", "ar": "صحن كفتة", "p": 13.0},
            ],
        }
    },
    {
        "name": "Smoking Hub", "name_ar": "سموكينغ هب", "category": "Grills",
        "menu": {
            "Food / أكل": [
                {"n": "Crispy Chicken Platter", "ar": "صحن دجاج مقرمش", "p": 10.5},
                {"n": "Beef Steak", "ar": "ستيك لحم", "p": 15.0},
                {"n": "Pasta Alfredo", "ar": "باستا ألفريدو", "p": 9.5},
                {"n": "Chicken Wings", "ar": "أجنحة دجاج", "p": 7.0},
                {"n": "Nachos", "ar": "ناتشوز", "p": 8.0},
            ],
            "Shisha / أراكيل": [
                {"n": "Regular Shisha", "ar": "أركيلة عادية", "p": 7.0},
                {"n": "Special Mix", "ar": "خلطة خاصة", "p": 9.0},
                {"n": "Ajami", "ar": "عجمي", "p": 10.0},
            ],
        }
    },
]


async def ensure_tables(session):
    """Ensure menuitemvariant table exists"""
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS menuitemvariant (
            id SERIAL PRIMARY KEY,
            menu_item_id INTEGER REFERENCES menuitem(id) ON DELETE CASCADE,
            name VARCHAR NOT NULL,
            name_ar VARCHAR,
            price FLOAT NOT NULL,
            "order" INTEGER DEFAULT 0
        )
    """))
    
    # Add new columns to menuitem if not exist
    try:
        await session.execute(text("ALTER TABLE menuitem ADD COLUMN IF NOT EXISTS price_min FLOAT"))
        await session.execute(text("ALTER TABLE menuitem ADD COLUMN IF NOT EXISTS price_max FLOAT"))
        await session.execute(text("ALTER TABLE menuitem ADD COLUMN IF NOT EXISTS has_variants BOOLEAN DEFAULT FALSE"))
    except Exception as e:
        logger.warning(f"Column may already exist: {e}")
    
    await session.commit()
    logger.info("✅ Tables ready")


async def get_categories(session):
    """Get category name to ID mapping"""
    result = await session.execute(text("SELECT id, name FROM restaurant_category"))
    return {row[1]: row[0] for row in result.fetchall()}


async def seed_restaurant(session, rest_data, categories):
    """Seed a single restaurant with its menu"""
    name = rest_data["name"]
    
    # Check if restaurant exists
    result = await session.execute(
        text("SELECT id FROM restaurant WHERE name = :name"),
        {"name": name}
    )
    existing = result.fetchone()
    
    if existing:
        logger.info(f"  ⏭️ Restaurant exists: {name}")
        return
    
    # Create restaurant
    category_id = categories.get(rest_data["category"])
    result = await session.execute(
        text("""
            INSERT INTO restaurant (name, name_ar, category_id, is_active)
            VALUES (:name, :name_ar, :cat_id, TRUE)
            RETURNING id
        """),
        {"name": name, "name_ar": rest_data["name_ar"], "cat_id": category_id}
    )
    restaurant_id = result.fetchone()[0]
    
    # Create branch
    await session.execute(
        text("INSERT INTO branch (restaurant_id, name, is_active) VALUES (:rid, 'Main Branch', TRUE)"),
        {"rid": restaurant_id}
    )
    
    # Create menu
    result = await session.execute(
        text("""
            INSERT INTO menu (restaurant_id, name, name_ar, is_active)
            VALUES (:rid, 'Main Menu', 'القائمة الرئيسية', TRUE)
            RETURNING id
        """),
        {"rid": restaurant_id}
    )
    menu_id = result.fetchone()[0]
    
    # Create categories and items
    cat_order = 0
    for cat_name, items in rest_data["menu"].items():
        # Split category name
        if " / " in cat_name:
            name_en, name_ar = cat_name.split(" / ")
        else:
            name_en = name_ar = cat_name
        
        result = await session.execute(
            text("""
                INSERT INTO category (menu_id, name, name_ar, "order")
                VALUES (:mid, :name, :name_ar, :ord)
                RETURNING id
            """),
            {"mid": menu_id, "name": name_en, "name_ar": name_ar, "ord": cat_order}
        )
        category_id = result.fetchone()[0]
        cat_order += 1
        
        # Add items
        item_order = 0
        for item in items:
            has_variants = "v" in item
            
            if has_variants:
                variants = item["v"]
                prices = [v[1] for v in variants]
                price_min, price_max = min(prices), max(prices)
                
                result = await session.execute(
                    text("""
                        INSERT INTO menuitem (category_id, name, name_ar, has_variants, price_min, price_max, "order", is_available)
                        VALUES (:cid, :name, :name_ar, TRUE, :pmin, :pmax, :ord, TRUE)
                        RETURNING id
                    """),
                    {"cid": category_id, "name": item["n"], "name_ar": item["ar"], 
                     "pmin": price_min, "pmax": price_max, "ord": item_order}
                )
                menu_item_id = result.fetchone()[0]
                
                # Add variants
                for v_order, (size_name, price) in enumerate(variants):
                    size_ar = SIZES.get(size_name, size_name)
                    await session.execute(
                        text("""
                            INSERT INTO menuitemvariant (menu_item_id, name, name_ar, price, "order")
                            VALUES (:mid, :name, :name_ar, :price, :ord)
                        """),
                        {"mid": menu_item_id, "name": size_name, "name_ar": size_ar, "price": price, "ord": v_order}
                    )
            else:
                await session.execute(
                    text("""
                        INSERT INTO menuitem (category_id, name, name_ar, price, has_variants, "order", is_available)
                        VALUES (:cid, :name, :name_ar, :price, FALSE, :ord, TRUE)
                    """),
                    {"cid": category_id, "name": item["n"], "name_ar": item["ar"], 
                     "price": item["p"], "ord": item_order}
                )
            
            item_order += 1
    
    logger.info(f"  ✅ Added: {name} ({rest_data['name_ar']})")


async def main():
    logger.info("🚀 Starting seed to Cloud Database...")
    
    async with AsyncSessionLocal() as session:
        # Ensure tables
        await ensure_tables(session)
        
        # Get categories
        categories = await get_categories(session)
        logger.info(f"📁 Found {len(categories)} categories")
        
        # Seed restaurants
        logger.info(f"\n📍 Seeding {len(RESTAURANTS)} restaurants...\n")
        
        for rest_data in RESTAURANTS:
            try:
                await seed_restaurant(session, rest_data, categories)
                await session.commit()
            except Exception as e:
                logger.error(f"  ❌ Error with {rest_data['name']}: {e}")
                await session.rollback()
        
        # Summary
        result = await session.execute(text("SELECT COUNT(*) FROM restaurant"))
        total_restaurants = result.scalar()
        
        result = await session.execute(text("SELECT COUNT(*) FROM menuitem"))
        total_items = result.scalar()
        
        logger.info(f"\n📊 Summary:")
        logger.info(f"   Restaurants: {total_restaurants}")
        logger.info(f"   Menu Items: {total_items}")
        logger.info("\n✅ Seeding complete!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
