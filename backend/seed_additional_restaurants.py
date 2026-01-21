"""
Seed Additional Restaurants to Cloud Database
22 new restaurants with menus
Run: python3 seed_additional_restaurants.py
"""
import asyncio
import logging
import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://lionbot:LionBot2024@163.245.208.160:5432/lionbot"
engine = create_async_engine(DATABASE_URL, echo=False, pool_timeout=60)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

LBP_RATE = 90000

SIZES = {
    "Small": "صغير", "Medium": "وسط", "Large": "كبير", "XL": "اكس لارج",
    "S": "صغير", "M": "وسط", "L": "كبير",
    "عادي": "عادي", "مشروحة": "مشروحة", "اكسترا": "اكسترا",
    "صغير": "صغير", "وسط": "وسط", "كبير": "كبير", "عائلي": "عائلي",
    "Sandwich": "سندويش", "Meal": "وجبة",
    "دجاج": "دجاج", "لحمة": "لحمة",
}

def parse_price(price_str):
    """Convert price string to USD float"""
    if not price_str or price_str == "-":
        return None
    
    price_str = str(price_str).strip()
    
    # Extract number
    num_match = re.search(r'[\d,\.]+', price_str.replace(',', ''))
    if not num_match:
        return None
    
    price = float(num_match.group().replace(',', ''))
    
    # Check currency
    if 'LBP' in price_str.upper() or 'L.L' in price_str.upper():
        return round(price / LBP_RATE, 2)
    elif '$' in price_str or 'USD' in price_str.upper():
        return round(price, 2)
    elif price > 1000:  # Likely LBP if > 1000
        return round(price / LBP_RATE, 2)
    else:
        return round(price, 2)

# Additional restaurants data
RESTAURANTS = [
    {
        "name": "Midos Sandwiches", "name_ar": "ميدوز ساندويشات", "category": "Sandwiches",
        "menu": {
            "Breakfast / فطور": [
                {"n": "Labneh", "ar": "لبنة", "p": 1.56},
                {"n": "Feta Cheese", "ar": "جبنة فيتا", "p": 3.33},
                {"n": "Halloumi Cheese", "ar": "جبنة حلوم", "p": 3.89},
                {"n": "Egg N' Cheese", "ar": "بيض وجبنة", "p": 6.11},
            ],
            "Starters / مقبلات": [
                {"n": "Wedges Box", "ar": "علبة ويدجز", "p": 5.0},
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 4.44},
                {"n": "Curly Fries", "ar": "بطاطا حلزونية", "p": 6.67},
                {"n": "French Fries Box", "ar": "علبة بطاطا", "p": 4.44},
                {"n": "VIP-Fries", "ar": "بطاطا VIP", "p": 8.89},
            ],
            "Salads / سلطات": [
                {"n": "Greek Salad", "ar": "سلطة يونانية", "p": 6.44},
                {"n": "Caesar Salad", "ar": "سلطة سيزر", "p": 8.67},
                {"n": "Crab Salad", "ar": "سلطة سلطعون", "p": 9.11},
                {"n": "Tuna Salad", "ar": "سلطة تونا", "p": 8.33},
            ],
            "Sandwiches / سندويشات": [
                {"n": "Crispy Chicken", "ar": "دجاج مقرمش", "p": 7.22},
                {"n": "Roast Beef", "ar": "روست بيف", "p": 7.22},
                {"n": "Mido's Chicken", "ar": "دجاج ميدوز", "p": 8.89},
                {"n": "Fajita", "ar": "فاهيتا", "p": 9.33},
                {"n": "Philadelphia", "ar": "فيلادلفيا", "p": 9.56},
                {"n": "Francisco", "ar": "فرانسيسكو", "p": 8.33},
                {"n": "Chicken Sub", "ar": "تشيكن سب", "p": 7.78},
            ],
            "Burgers / برغر": [
                {"n": "Lebanese Burger", "ar": "برغر لبناني", "p": 7.44},
                {"n": "Swiss Mushroom Burger", "ar": "برغر فطر سويسري", "p": 9.56},
                {"n": "Midos Burger", "ar": "برغر ميدوز", "p": 9.44},
                {"n": "Truffle Burger", "ar": "برغر ترافل", "p": 10.0},
                {"n": "Smash Burger", "ar": "سماش برغر", "p": 8.33},
                {"n": "Zinger Burger", "ar": "زينجر برغر", "p": 8.67},
            ],
            "Drinks / مشروبات": [
                {"n": "Soft Drinks", "ar": "مشروبات غازية", "p": 1.67},
                {"n": "Water", "ar": "مياه", "p": 1.11},
            ],
        }
    },
    {
        "name": "Bob Juice", "name_ar": "بوب جوس", "category": "Beverages",
        "menu": {
            "BOB Specials / سبيشال بوب": [
                {"n": "V.I.P", "ar": "في آي بي", "v": [("Small", 4.0), ("Medium", 6.5), ("Large", 8.0)]},
                {"n": "Hulk", "ar": "هالك", "v": [("Small", 3.6), ("Medium", 5.6), ("Large", 7.22)]},
                {"n": "Mudamer", "ar": "مدمر", "p": 2.5},
            ],
            "Cocktails / كوكتيل": [
                {"n": "Shaqaf Cocktail", "ar": "كوكتيل شقف", "v": [("Small", 3.25), ("Medium", 5.2)]},
                {"n": "Avoca Cup", "ar": "كوب أفوكا", "p": 3.6},
                {"n": "Hawaii Cup", "ar": "كوب هاواي", "p": 2.25},
            ],
            "Desserts / حلويات": [
                {"n": "Rice Pudding", "ar": "رز بحليب", "p": 1.0},
                {"n": "Custard", "ar": "كاسترد", "p": 1.0},
                {"n": "Cheesecake", "ar": "تشيز كيك", "p": 3.0},
            ],
            "Crepes & Waffles / كريب ووافل": [
                {"n": "Triple Chocolate Crepe", "ar": "كريب تريبل شوكولا", "p": 6.5},
                {"n": "Banana Wrap Crepe", "ar": "كريب موز", "p": 4.0},
                {"n": "Triple Chocolate Waffle", "ar": "وافل تريبل شوكولا", "p": 9.0},
            ],
        }
    },
    {
        "name": "Shawarma Ghassan", "name_ar": "شاورما غسان", "category": "Shawarma",
        "menu": {
            "Shawarma / شاورما": [
                {"n": "Chicken Shawarma", "ar": "شاورما دجاج", "v": [("Small", 4.0), ("Medium", 4.0), ("Large", 5.0)]},
                {"n": "Beef Shawarma", "ar": "شاورما لحمة", "v": [("Small", 4.0), ("Medium", 4.0), ("Large", 5.0)]},
                {"n": "Chicken Shawarma 1kg", "ar": "شاورما دجاج كيلو", "p": 35.0},
                {"n": "Beef Shawarma 1kg", "ar": "شاورما لحمة كيلو", "p": 35.0},
            ],
            "Meals / وجبات": [
                {"n": "Tawouk Platter", "ar": "صحن طاووق", "p": 15.0},
                {"n": "Chicken Platter", "ar": "صحن دجاج", "p": 15.0},
                {"n": "Mixed Platter", "ar": "صحن مشكل", "p": 15.0},
                {"n": "Burger Platter", "ar": "صحن برغر", "p": 9.0},
            ],
            "Fries / بطاطا": [
                {"n": "Fries Platter", "ar": "صحن بطاطا", "v": [("Medium", 4.0), ("Large", 5.0)]},
                {"n": "Fries Box", "ar": "علبة بطاطا", "p": 3.0},
            ],
            "Grilled / مشاوي": [
                {"n": "Tawouk Sandwich", "ar": "سندويش طاووق", "p": 4.0},
                {"n": "Burger Beef", "ar": "برغر لحمة", "p": 4.0},
                {"n": "Burger Chicken", "ar": "برغر دجاج", "p": 4.0},
            ],
        }
    },
    {
        "name": "Al Akkad Cocktail", "name_ar": "كوكتيل العقاد", "category": "Beverages",
        "menu": {
            "Akkad Specials / سبيشال العقاد": [
                {"n": "Avoca Cup", "ar": "كوب أفوكا", "v": [("Small", 4.25), ("Medium", 6.8), ("Large", 8.5)]},
                {"n": "V.I.P Cup", "ar": "كوب VIP", "p": 4.75},
                {"n": "Hulk Cup", "ar": "كوب هالك", "p": 4.25},
            ],
            "Cocktails / كوكتيل": [
                {"n": "Shaqaf Cocktail", "ar": "كوكتيل شقف", "v": [("Small", 3.75), ("Medium", 6.0), ("Large", 7.5)]},
                {"n": "Light Cocktail", "ar": "كوكتيل لايت", "p": 2.25},
            ],
            "Desserts / حلويات": [
                {"n": "Custard", "ar": "كاسترد", "p": 1.0},
                {"n": "Mhalabieh", "ar": "مهلبية", "p": 1.0},
                {"n": "Blueberry Cheesecake", "ar": "تشيز كيك بلوبيري", "p": 4.0},
            ],
        }
    },
    {
        "name": "Fayez Pizza", "name_ar": "بيتزا فايز", "category": "Pizza",
        "menu": {
            "Appetizers / مقبلات": [
                {"n": "Cheesy Garlic Bread", "ar": "خبز ثوم بالجبنة", "p": 5.0},
                {"n": "Nachos", "ar": "ناتشوز", "p": 10.0},
                {"n": "Crispy Chicken Tenders", "ar": "تندرز دجاج", "p": 10.0},
                {"n": "Potato Wedges", "ar": "ويدجز", "p": 5.0},
            ],
            "Salads / سلطات": [
                {"n": "Greek Salad", "ar": "سلطة يونانية", "p": 7.0},
                {"n": "Caesar Salad", "ar": "سلطة سيزر", "p": 4.0},
                {"n": "Chef Salad", "ar": "سلطة شيف", "p": 7.0},
            ],
            "Pizza / بيتزا": [
                {"n": "Margherita", "ar": "مارغريتا", "p": 6.0},
                {"n": "Four Cheese", "ar": "أربع أجبان", "p": 9.0},
                {"n": "Pepperoni", "ar": "بيبروني", "p": 9.0},
                {"n": "Lebanese", "ar": "لبنانية", "p": 8.0},
                {"n": "Veggie", "ar": "خضار", "p": 7.0},
            ],
            "Wraps / راب": [
                {"n": "Steak Philly", "ar": "ستيك فيلي", "p": 10.0},
                {"n": "Chicken Pesto", "ar": "دجاج بيستو", "p": 8.0},
                {"n": "Chicken Fajita", "ar": "فاهيتا دجاج", "p": 8.0},
            ],
            "Pasta / باستا": [
                {"n": "Fettuccine Alfredo", "ar": "فيتوتشيني ألفريدو", "p": 7.0},
                {"n": "Four Cheese Pasta", "ar": "باستا أربع أجبان", "p": 9.0},
            ],
        }
    },
    {
        "name": "Chahine Seafood", "name_ar": "سي فود شاهين", "category": "Grills",
        "menu": {
            "Seafood / بحري": [
                {"n": "Loaded Seafood Mix", "ar": "سي فود مشكل", "p": 5.0},
                {"n": "Shrimps Platter", "ar": "صحن قريدس", "p": 9.44},
                {"n": "Calamari", "ar": "كالاماري", "p": 4.44},
                {"n": "Chahine's Shrimp", "ar": "قريدس شاهين", "p": 4.44},
                {"n": "Crispy Fillet", "ar": "فيليه مقرمش", "p": 5.56},
                {"n": "Crispy Shrimp", "ar": "قريدس مقرمش", "p": 5.0},
            ],
            "Burgers / برغر": [
                {"n": "Crispy Fillet Burger", "ar": "برغر فيليه", "p": 5.56},
                {"n": "Fish Metla Burger", "ar": "برغر سمك", "p": 5.56},
                {"n": "Shrimp Burger", "ar": "برغر قريدس", "p": 5.56},
            ],
            "Salads / سلطات": [
                {"n": "Crab Salad", "ar": "سلطة سلطعون", "p": 5.56},
                {"n": "Crab and Shrimps", "ar": "سلطعون وقريدس", "p": 7.22},
            ],
            "Fries / بطاطا": [
                {"n": "Fries Box", "ar": "علبة بطاطا", "p": 2.78},
                {"n": "Fries Platter", "ar": "صحن بطاطا", "p": 4.44},
            ],
        }
    },
    {
        "name": "Space Food", "name_ar": "سبيس فود", "category": "Pizza",
        "menu": {
            "Pizza Chicken / بيتزا دجاج": [
                {"n": "Sweet & Sour", "ar": "حامض حلو", "v": [("S", 8.0), ("M", 10.0), ("L", 13.0)]},
                {"n": "Teryaki", "ar": "تيرياكي", "v": [("S", 8.0), ("M", 10.0), ("L", 13.0)]},
                {"n": "BBQ", "ar": "باربكيو", "v": [("S", 8.0), ("M", 10.0), ("L", 13.0)]},
                {"n": "Chicken Philly", "ar": "دجاج فيلي", "v": [("S", 9.0), ("M", 11.0), ("L", 14.0)]},
            ],
            "Pizza Shrimp / بيتزا قريدس": [
                {"n": "Sweet & Sour Shrimp", "ar": "قريدس حامض حلو", "v": [("S", 10.0), ("M", 13.0), ("L", 16.0)]},
                {"n": "Teryaki Shrimp", "ar": "قريدس تيرياكي", "v": [("S", 10.0), ("M", 13.0), ("L", 16.0)]},
            ],
            "Pizza / بيتزا": [
                {"n": "Pepperoni", "ar": "بيبروني", "v": [("S", 7.0), ("M", 9.0), ("L", 12.0)]},
                {"n": "Vegetarian", "ar": "نباتية", "v": [("S", 6.0), ("M", 8.0), ("L", 11.0)]},
            ],
            "Salads / سلطات": [
                {"n": "Caesar Salad", "ar": "سلطة سيزر", "p": 6.67},
                {"n": "Tuna Salad", "ar": "سلطة تونا", "p": 7.78},
                {"n": "Crab Salad", "ar": "سلطة سلطعون", "p": 7.78},
                {"n": "Shrimps Salad", "ar": "سلطة قريدس", "p": 7.78},
            ],
            "Appetizers / مقبلات": [
                {"n": "French Fries", "ar": "بطاطا مقلية", "v": [("M", 3.5), ("L", 5.0)]},
                {"n": "Wedges", "ar": "ويدجز", "v": [("M", 4.0), ("L", 6.5)]},
                {"n": "Mozzarella Sticks", "ar": "أصابع موزاريلا", "p": 5.0},
            ],
            "Pasta / باستا": [
                {"n": "Curry Chicken", "ar": "كاري دجاج", "v": [("M", 8.0), ("L", 10.5)]},
                {"n": "Fajita Pasta", "ar": "باستا فاهيتا", "v": [("M", 9.5), ("L", 12.5)]},
                {"n": "Pesto Chicken", "ar": "بيستو دجاج", "v": [("M", 9.0), ("L", 12.0)]},
                {"n": "Fettuccine Chicken", "ar": "فيتوتشيني دجاج", "v": [("M", 9.0), ("L", 11.5)]},
            ],
        }
    },
    {
        "name": "Farrouj Shaheen", "name_ar": "فروج شاهين", "category": "Grills",
        "menu": {
            "Chicken / فروج": [
                {"n": "Charcoal Chicken", "ar": "فروج على الفحم", "p": 12.78},
                {"n": "Half Charcoal Chicken", "ar": "نصف فروج فحم", "p": 6.67},
                {"n": "Big Sandwich", "ar": "سندويش كبير", "p": 4.44},
                {"n": "Medium Sandwich", "ar": "سندويش وسط", "p": 2.78},
                {"n": "Shaheen Kaakeh", "ar": "كعكة شاهين", "p": 5.0},
            ],
            "Appetizers / مقبلات": [
                {"n": "Small Fries", "ar": "بطاطا صغير", "p": 2.22},
                {"n": "Large Fries", "ar": "بطاطا كبير", "p": 3.89},
                {"n": "Hummus", "ar": "حمص", "p": 2.22},
                {"n": "Fattoush", "ar": "فتوش", "p": 3.33},
            ],
            "Drinks / مشروبات": [
                {"n": "Soft Drinks", "ar": "مشروبات غازية", "p": 1.11},
                {"n": "Ayran", "ar": "عيران", "p": 1.11},
                {"n": "Water", "ar": "مياه", "p": 0.44},
            ],
        }
    },
    {
        "name": "Malek El Mo3ajanat", "name_ar": "ملك المعجنات", "category": "Home Food",
        "menu": {
            "Manakesh / مناقيش": [
                {"n": "Zaatar", "ar": "زعتر", "p": 0.78},
                {"n": "Akkawi Cheese", "ar": "جبنة عكاوي", "p": 2.22},
                {"n": "Zaatar & Cheese", "ar": "زعتر وجبنة", "p": 1.89},
                {"n": "Halloumi", "ar": "حلوم", "p": 2.22},
                {"n": "Halloumi & Kashkaval", "ar": "حلوم وقشقوان", "p": 3.33},
                {"n": "Labneh", "ar": "لبنة", "p": 1.94},
                {"n": "Keshek", "ar": "كشك", "p": 2.22},
                {"n": "Lahm Bi Ajeen", "ar": "لحمة بعجين", "p": 3.89},
            ],
            "Special Manakesh / مناقيش سبيسيال": [
                {"n": "Pepperoni & Kashkaval", "ar": "بيبروني وقشقوان", "p": 4.44},
                {"n": "Tawouk & Kashkaval", "ar": "طاووق وقشقوان", "p": 3.89},
                {"n": "Fajita & Kashkaval", "ar": "فاهيتا وقشقوان", "p": 4.44},
                {"n": "Shawarma & Kashkaval", "ar": "شاورما وقشقوان", "p": 4.44},
                {"n": "Special", "ar": "سبيسيال", "p": 5.56},
            ],
            "Pizza / بيتزا": [
                {"n": "Margherita", "ar": "مارغريتا", "v": [("Small", 5.56), ("Medium", 6.67), ("Large", 8.89)]},
                {"n": "Vegetables", "ar": "خضرا", "v": [("Small", 6.67), ("Medium", 8.89), ("Large", 10.0)]},
                {"n": "Mortadella", "ar": "مرتديلا", "v": [("Small", 6.67), ("Medium", 8.89), ("Large", 11.11)]},
                {"n": "Pepperoni", "ar": "بيبروني", "v": [("Small", 7.78), ("Medium", 10.0), ("Large", 12.22)]},
            ],
            "Fatayer / فطاير": [
                {"n": "Spinach", "ar": "سبانخ", "p": 1.11},
                {"n": "Cheese", "ar": "جبنة", "p": 1.11},
                {"n": "Hot Dog", "ar": "هوت دوغ", "p": 1.39},
            ],
        }
    },
    {
        "name": "Farid Sandwich", "name_ar": "فريد ساندويش", "category": "Grills",
        "menu": {
            "Sandwiches / سندويشات": [
                {"n": "Fatayel", "ar": "فتايل", "p": 2.0},
                {"n": "Kafta", "ar": "كفتة", "p": 2.0},
                {"n": "Makanek", "ar": "مقانق", "p": 2.11},
                {"n": "Sojok", "ar": "سجق", "p": 2.11},
                {"n": "Chicken", "ar": "دجاج", "p": 2.11},
                {"n": "Sawda", "ar": "سودة", "p": 2.0},
                {"n": "Basterma", "ar": "بسترما", "p": 2.22},
                {"n": "Roasto", "ar": "روستو", "p": 2.56},
                {"n": "Add Cheese", "ar": "مع جبنة", "p": 0.72},
            ],
        }
    },
    {
        "name": "Abu Malek", "name_ar": "أبو مالك", "category": "Home Food",
        "menu": {
            "Manakesh / مناقيش": [
                {"n": "Zaatar", "ar": "زعتر", "p": 0.67},
                {"n": "Cheese", "ar": "جبنة", "p": 2.11},
                {"n": "Akkawi & Kashkaval", "ar": "عكاوي وقشقوان", "p": 3.22},
                {"n": "Halloumi & Kashkaval", "ar": "حلوم وقشقوان", "p": 3.22},
                {"n": "Kashkaval", "ar": "قشقوان", "p": 2.89},
                {"n": "Labneh", "ar": "لبنة", "p": 2.11},
                {"n": "Keshek", "ar": "كشك", "p": 1.78},
                {"n": "Special", "ar": "سبيسيال", "p": 5.33},
            ],
            "Pizza / بيتزا": [
                {"n": "Margherita", "ar": "مارغريتا", "v": [("Small", 5.78), ("Medium", 9.67), ("Large", 12.78)]},
                {"n": "Vegetables", "ar": "خضرة", "v": [("Small", 6.11), ("Medium", 10.33), ("Large", 13.89)]},
                {"n": "Pepperoni", "ar": "بيبروني", "v": [("Small", 7.22), ("Medium", 12.0), ("Large", 16.11)]},
            ],
        }
    },
    {
        "name": "Al M3alem Subhi", "name_ar": "المعلم صبحي", "category": "Shawarma",
        "menu": {
            "Shawarma / شاورما": [
                {"n": "Chicken Shawarma Large", "ar": "شاورما دجاج كبير", "p": 2.78},
                {"n": "Chicken Shawarma XL", "ar": "شاورما دجاج اكس لارج", "p": 5.0},
                {"n": "Beef Shawarma Large", "ar": "شاورما لحمة كبير", "p": 3.89},
                {"n": "Beef Shawarma XL", "ar": "شاورما لحمة اكس لارج", "p": 5.0},
                {"n": "Shawarma Meal", "ar": "وجبة شاورما", "p": 5.28},
            ],
            "Grilled / مشاوي": [
                {"n": "Charcoal Chicken Sandwich", "ar": "سندويش دجاج فحم", "p": 3.33},
                {"n": "Tawouk Sandwich", "ar": "سندويش طاووق", "p": 3.89},
                {"n": "Kabab Sandwich", "ar": "سندويش كباب", "p": 3.33},
            ],
            "Sandwiches / سندويشات": [
                {"n": "Chicken Burger", "ar": "تشيكن برغر", "p": 3.89},
                {"n": "Beef Burger", "ar": "برغر لحمة", "p": 5.0},
                {"n": "Zinger Burger", "ar": "زينجر برغر", "p": 5.0},
                {"n": "Crispy Sandwich", "ar": "سندويش كريسبي", "p": 5.0},
                {"n": "Fajita Sandwich", "ar": "سندويش فاهيتا", "p": 5.56},
            ],
            "Chicken / فروج": [
                {"n": "Roasted Chicken", "ar": "فروج مشوي", "p": 10.56},
                {"n": "Broasted Chicken", "ar": "فروج بروستد", "p": 14.44},
                {"n": "Charcoal Chicken", "ar": "فروج فحم", "p": 13.33},
            ],
        }
    },
    {
        "name": "Abu Arab Kaak", "name_ar": "ملك الكعك العصروني", "category": "Home Food",
        "menu": {
            "Regular Kaak / كعك عادي": [
                {"n": "Plain", "ar": "سادة", "p": 0.89},
                {"n": "Zaatar", "ar": "زعتر", "p": 2.22},
                {"n": "Cheese Akkawi", "ar": "جبنة عكاوي", "p": 2.78},
                {"n": "Halloumi", "ar": "حلوم", "p": 2.78},
                {"n": "Kashkaval", "ar": "قشقوان", "p": 3.33},
                {"n": "Halawa", "ar": "حلاوة", "p": 2.56},
                {"n": "Chocolate", "ar": "شوكولا", "p": 2.56},
            ],
            "Mixed Kaak / كعك مشكل": [
                {"n": "Turkey & Kashkaval", "ar": "حبش وقشقوان", "p": 5.67},
                {"n": "Pepperoni & Kashkaval", "ar": "بيبروني وقشقوان", "p": 5.67},
                {"n": "Pizza Kaak", "ar": "كعكة بيتزا", "p": 4.44},
                {"n": "4 Cheese", "ar": "أربع أجبان", "p": 6.89},
                {"n": "Sojok & Kashkaval", "ar": "سجق وقشقوان", "p": 5.56},
            ],
            "Drinks / مشروبات": [
                {"n": "Pepsi", "ar": "بيبسي", "p": 1.11},
                {"n": "Ayran", "ar": "لبن عيران", "p": 0.83},
                {"n": "Water", "ar": "مياه", "p": 0.33},
            ],
        }
    },
    {
        "name": "Al Hamra Restaurant", "name_ar": "مطعم الحمرا", "category": "Shawarma",
        "menu": {
            "Shawarma / شاورما": [
                {"n": "Chicken Shawarma Large", "ar": "شاورما دجاج كبيرة", "p": 3.33},
                {"n": "Chicken Shawarma Medium", "ar": "شاورما دجاج وسط", "p": 1.94},
                {"n": "Doner Chicken", "ar": "دونر دجاج", "p": 4.44},
                {"n": "1kg Chicken Shawarma", "ar": "كيلو شاورما دجاج", "p": 22.22},
            ],
            "Chicken / فروج": [
                {"n": "Roasted Chicken", "ar": "فروج مشوي", "p": 11.0},
                {"n": "Broasted Chicken", "ar": "فروج بروستد", "p": 12.78},
                {"n": "Charcoal Chicken", "ar": "فروج فحم", "p": 12.78},
            ],
            "Crispy / كريسبي": [
                {"n": "Crispy Meal 3pcs", "ar": "وجبة كريسبي ٣ قطع", "p": 5.0},
                {"n": "Crispy Meal 5pcs", "ar": "وجبة كريسبي ٥ قطع", "p": 6.67},
            ],
            "Snacks / سناك": [
                {"n": "Tawouk Sandwich", "ar": "سندويش طاووق", "p": 3.33},
                {"n": "Fajita Sandwich", "ar": "سندويش فاهيتا", "p": 5.0},
                {"n": "Philadelphia", "ar": "فيلادلفيا", "p": 5.0},
                {"n": "Crispy Sandwich", "ar": "سندويش كريسبي", "p": 5.0},
            ],
            "Burgers / برغر": [
                {"n": "Beef Burger", "ar": "برغر لحمة", "p": 5.0},
                {"n": "Zinger Burger", "ar": "زينجر برغر", "p": 4.44},
                {"n": "Mushroom Burger", "ar": "مشروم برغر", "p": 5.0},
            ],
        }
    },
    {
        "name": "Al Akhawain Al Jamal", "name_ar": "الأخوين الجمل", "category": "Grills",
        "menu": {
            "Grilled Sandwiches / مشاوي سندويش": [
                {"n": "Kafta Sandwich", "ar": "سندويش كفتة", "p": 1.11},
                {"n": "Shaqaf Sandwich", "ar": "سندويش شقف", "p": 1.11},
                {"n": "Sawda Sandwich", "ar": "سندويش سودة", "p": 1.11},
                {"n": "Kabab Sandwich", "ar": "سندويش كباب", "p": 1.11},
                {"n": "Tawouk Sandwich", "ar": "سندويش طاووق", "p": 1.11},
            ],
            "Shawarma / شاورما": [
                {"n": "Chicken Shawarma", "ar": "شاورما دجاج", "p": 2.78},
                {"n": "Beef Shawarma", "ar": "شاورما لحمة", "p": 2.78},
                {"n": "1kg Shawarma", "ar": "كيلو شاورما", "p": 25.56},
            ],
            "Burgers / برغر": [
                {"n": "Beef Burger", "ar": "برغر لحمة", "p": 2.22},
                {"n": "Kafta Burger", "ar": "برغر كفتة", "p": 2.22},
            ],
            "Grill Meals / وجبات مشاوي": [
                {"n": "4 Skewers Meal", "ar": "وجبة ٤ أسياخ", "p": 4.44},
                {"n": "6 Skewers Meal", "ar": "وجبة ٦ أسياخ", "p": 6.11},
                {"n": "1kg Mixed Grill", "ar": "كيلو مشاوي مشكل", "p": 13.33},
            ],
            "Kibbeh / كبة": [
                {"n": "Kibbeh Meal 6pcs", "ar": "وجبة كبة ٦ قطع", "p": 6.67},
                {"n": "Raw Kibbeh 12pcs", "ar": "كبة نية ١٢ قطعة", "p": 6.67},
            ],
        }
    },
    {
        "name": "Baba Ghanouj & Dr. Meat", "name_ar": "بابا غنوج ودكتور ميت", "category": "Grills",
        "menu": {
            "Dr. Meat Steaks / ستيكات": [
                {"n": "Brisket Meal Local", "ar": "بريسكت محلي", "p": 14.0},
                {"n": "Rib Eye Brazilian", "ar": "ريب آي برازيلي", "p": 20.0},
                {"n": "Rib Eye Australian", "ar": "ريب آي أسترالي", "p": 35.0},
                {"n": "Wagyu Burger", "ar": "برغر واغيو", "p": 18.0},
            ],
            "Dr. Meat Burgers / برغر": [
                {"n": "Lebanese Burger", "ar": "برغر لبناني", "p": 6.0},
                {"n": "Classic Burger", "ar": "برغر كلاسيك", "p": 6.0},
                {"n": "Truffle Burger", "ar": "برغر ترافل", "p": 7.0},
                {"n": "Smash Burger", "ar": "سماش برغر", "p": 6.0},
            ],
            "Baba Ghanouj Manakesh / مناقيش": [
                {"n": "Akkawi & Kashkawan", "ar": "عكاوي وقشقوان", "p": 4.0},
                {"n": "Halloumi", "ar": "حلوم", "p": 2.5},
                {"n": "Zaatar", "ar": "زعتر", "p": 1.5},
                {"n": "Lahm Bi Ajeen", "ar": "لحمة بعجين", "p": 3.5},
            ],
            "Pizza / بيتزا": [
                {"n": "Margherita", "ar": "مارغريتا", "v": [("S", 8.0), ("M", 10.0), ("L", 12.0)]},
                {"n": "Pepperoni", "ar": "بيبروني", "v": [("S", 8.0), ("M", 10.0), ("L", 12.0)]},
            ],
            "Sandwiches / سندويشات": [
                {"n": "Chicken Sub", "ar": "تشيكن سب", "p": 5.0},
                {"n": "Fajita", "ar": "فاهيتا", "p": 5.0},
                {"n": "Crispy", "ar": "كريسبي", "p": 5.5},
                {"n": "Zinger", "ar": "زينجر", "p": 5.5},
            ],
            "Shawarma / شاورما": [
                {"n": "Chicken Shawarma", "ar": "شاورما دجاج", "p": 3.5},
                {"n": "Meat Shawarma", "ar": "شاورما لحمة", "p": 4.5},
                {"n": "1kg Chicken Shawarma", "ar": "كيلو شاورما دجاج", "p": 24.0},
            ],
            "Grills / مشاوي": [
                {"n": "Kafta Sandwich", "ar": "سندويش كفتة", "p": 3.0},
                {"n": "Tawook Sandwich", "ar": "سندويش طاووق", "p": 3.0},
                {"n": "Mixed Grill 1kg", "ar": "مشاوي مشكل كيلو", "p": 26.0},
            ],
        }
    },
    {
        "name": "Bayt Al Nar", "name_ar": "بيت النار على الحطب", "category": "Home Food",
        "menu": {
            "Manakesh Regular / مناقيش عادية": [
                {"n": "Zaatar", "ar": "زعتر", "p": 0.44},
                {"n": "Cheese", "ar": "جبنة", "p": 1.33},
                {"n": "Keshek", "ar": "كشك", "p": 1.11},
                {"n": "Labneh", "ar": "لبنة", "p": 1.11},
                {"n": "Halloumi & Kashkaval", "ar": "حلوم وقشقوان", "p": 1.89},
                {"n": "Tawouk", "ar": "طاووق", "p": 2.78},
                {"n": "Fajita", "ar": "فاهيتا", "p": 2.78},
            ],
            "Pizza / بيتزا": [
                {"n": "Vegetables", "ar": "خضرة", "p": 2.78},
                {"n": "Sojok", "ar": "سجق", "p": 3.33},
                {"n": "Mortadella", "ar": "مرتديلا", "p": 3.33},
                {"n": "Pepperoni", "ar": "بيبروني", "p": 3.89},
                {"n": "Awarma", "ar": "قاورما", "p": 3.89},
            ],
        }
    },
    {
        "name": "Forn Lobnan", "name_ar": "فرن لبنان", "category": "Home Food",
        "menu": {
            "Manakesh / مناقيش": [
                {"n": "Akkawi Cheese", "ar": "جبنة عكاوي", "p": 2.0},
                {"n": "Akkawi & Kashkaval", "ar": "عكاوي وقشقوان", "p": 2.78},
                {"n": "Four Cheese", "ar": "فور تشيز", "p": 2.78},
                {"n": "Zaatar", "ar": "زعتر", "p": 0.78},
                {"n": "Labneh Mix", "ar": "خلطة اللبنة", "p": 1.67},
            ],
            "Meat Manakesh / مناقيش لحوم": [
                {"n": "Lahm Bi Ajeen", "ar": "لحمة بعجين", "p": 2.78},
                {"n": "Mortadella & Cheese", "ar": "مرتديلا وجبنة", "p": 3.33},
                {"n": "Sojok & Cheese", "ar": "سجق وجبنة", "p": 3.33},
                {"n": "Tawouk & Cheese", "ar": "طاووق وجبنة", "p": 3.89},
                {"n": "Fajita & Cheese", "ar": "فاهيتا وجبنة", "p": 3.89},
            ],
            "Pizza / بيتزا": [
                {"n": "Mortadella", "ar": "مرتديلا", "p": 5.0},
                {"n": "Sojok", "ar": "سجق", "p": 5.0},
                {"n": "Awarma", "ar": "قاورما", "p": 5.56},
                {"n": "Vegetables", "ar": "خضار", "p": 4.44},
            ],
        }
    },
    {
        "name": "Kaake by Meat Chop", "name_ar": "كعكة ميت شوب", "category": "Home Food",
        "menu": {
            "Kaak & Saj / كعك وصاج": [
                {"n": "Zaatar", "ar": "زعتر", "p": 1.0},
                {"n": "Keshek", "ar": "كشك", "p": 1.67},
                {"n": "Cheese Akkawi", "ar": "جبنة عكاوي", "p": 2.0},
                {"n": "3 Cheese", "ar": "ثلاث أجبان", "p": 2.78},
                {"n": "4 Cheese", "ar": "أربع أجبان", "p": 3.33},
                {"n": "Cheese & Chips", "ar": "جبنة وشيبس", "p": 3.0},
                {"n": "Labneh", "ar": "لبنة", "p": 1.67},
                {"n": "Labneh Harra", "ar": "لبنة حرة", "p": 2.0},
            ],
            "Special Kaak / كعك سبيسيال": [
                {"n": "Basterma & Cheese", "ar": "بسترما وجبنة", "p": 4.89},
                {"n": "Sojok & Cheese", "ar": "سجق وجبنة", "p": 4.89},
                {"n": "Kafta & Cheese", "ar": "كفتة وجبنة", "p": 4.89},
                {"n": "Kaaki Burger", "ar": "كعكي برغر", "p": 4.89},
                {"n": "Fajitas", "ar": "فاهيتا", "p": 4.33},
                {"n": "Chicken Sub", "ar": "تشيكن سب", "p": 4.33},
                {"n": "Tawook", "ar": "طاووق", "p": 4.33},
            ],
            "Sweet / حلو": [
                {"n": "Nutella Banana", "ar": "نوتيلا موز", "p": 3.0},
                {"n": "Nutella Halawa Banana", "ar": "نوتيلا حلاوة موز", "p": 3.56},
            ],
            "Drinks / مشروبات": [
                {"n": "Soft Drinks", "ar": "مشروبات غازية", "p": 1.67},
                {"n": "Water", "ar": "مياه", "p": 0.56},
            ],
        }
    },
    {
        "name": "Forn Al Qamar", "name_ar": "فرن القمر للجريش", "category": "Home Food",
        "menu": {
            "Manakesh / مناقيش": [
                {"n": "Zaatar", "ar": "زعتر", "p": 0.56},
                {"n": "Cheese", "ar": "جبنة", "p": 1.67},
                {"n": "Cheese & Kashkaval", "ar": "جبنة وقشقوان", "p": 2.22},
                {"n": "Keshek", "ar": "كشك", "p": 1.67},
                {"n": "Labneh", "ar": "لبنة", "p": 1.67},
                {"n": "Sojok & Cheese", "ar": "سجق وجبنة", "p": 2.78},
                {"n": "Tawouk", "ar": "طاووق", "p": 3.33},
                {"n": "Fajita", "ar": "فاهيتا", "p": 3.33},
            ],
            "Pizza / بيتزا": [
                {"n": "Vegetables", "ar": "خضرا", "v": [("Small", 4.44), ("Medium", 6.67), ("Large", 11.11)]},
                {"n": "Mortadella", "ar": "مرتديلا", "v": [("Small", 5.56), ("Medium", 7.78), ("Large", 13.33)]},
                {"n": "Chicken", "ar": "دجاج", "v": [("Small", 6.11), ("Medium", 8.89), ("Large", 14.44)]},
            ],
        }
    },
    {
        "name": "Forn Wa Saj Bazazo", "name_ar": "فرن وصاج بظاظو", "category": "Home Food",
        "menu": {
            "Manakesh / مناقيش": [
                {"n": "Zaatar", "ar": "زعتر", "p": 0.78},
                {"n": "Cheese", "ar": "جبنة", "p": 2.22},
                {"n": "Cheese & Zaatar", "ar": "جبنة وزعتر", "p": 1.67},
                {"n": "3 Cheese", "ar": "ثلاث أجبان", "p": 3.89},
                {"n": "Halloumi & Kashkaval", "ar": "حلوم وقشقوان", "p": 3.33},
                {"n": "Akkawi & Kashkaval", "ar": "عكاوي وقشقوان", "p": 3.33},
                {"n": "Tawouk & Kashkaval", "ar": "طاووق وقشقوان", "p": 4.44},
                {"n": "Fajita & Kashkaval", "ar": "فاهيتا وقشقوان", "p": 4.44},
            ],
            "Pizza / بيتزا": [
                {"n": "Margherita", "ar": "مارغريتا", "v": [("Small", 5.56), ("Medium", 7.78), ("Large", 15.0)]},
                {"n": "Vegetables", "ar": "خضرة", "v": [("Small", 5.56), ("Medium", 7.78), ("Large", 15.0)]},
                {"n": "Mortadella", "ar": "مرتديلا", "v": [("Small", 6.11), ("Medium", 8.33), ("Large", 17.0)]},
                {"n": "Pepperoni", "ar": "بيبروني", "v": [("Small", 6.67), ("Medium", 10.0), ("Large", 17.0)]},
            ],
        }
    },
]


async def get_categories(session):
    """Get category name to ID mapping"""
    result = await session.execute(text("SELECT id, name FROM restaurant_category"))
    return {row[1]: row[0] for row in result.fetchall()}


async def seed_restaurant(session, rest_data, categories):
    """Seed a single restaurant"""
    name = rest_data["name"]
    
    # Check if exists
    result = await session.execute(
        text("SELECT id FROM restaurant WHERE name = :name"),
        {"name": name}
    )
    if result.fetchone():
        logger.info(f"  ⏭️ Exists: {name}")
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
    logger.info("🚀 Seeding additional restaurants...")
    
    async with AsyncSessionLocal() as session:
        categories = await get_categories(session)
        logger.info(f"📁 Found {len(categories)} categories")
        
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
        logger.info("\n✅ Done!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
