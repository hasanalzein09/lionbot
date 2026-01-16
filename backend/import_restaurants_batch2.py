"""Script to import additional restaurants - Batch 2"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.restaurant import Restaurant, RestaurantCategory
from app.models.menu import Menu, Category, MenuItem, MenuItemVariant

# LBP to USD conversion (for items priced in LBP)
LBP_RATE = 90000

def lbp_to_usd(price_lbp):
    return round(price_lbp / LBP_RATE, 2)

# Additional restaurants data
RESTAURANTS_DATA = [
    {
        "name": "Doner House",
        "name_ar": "دونر هاوس",
        "category": "Shawarma",
        "menu": [
            {"category_en": "Burger", "category_ar": "برغر", "items": [
                {"name": "Zinger Burger", "name_ar": "زنجر برغر", "price": 4.17},
                {"name": "Crunchy Burger", "name_ar": "كرانشي برغر", "price": 4.17},
                {"name": "House Burger", "name_ar": "هاوس برغر", "price": 5.01},
                {"name": "Mushroom Burger", "name_ar": "مشروم برغر", "price": 5.01},
                {"name": "BBQ Burger", "name_ar": "باربكيو برغر", "price": 4.44},
                {"name": "Mexican Burger", "name_ar": "مكسيكان برغر", "price": 4.44},
                {"name": "Cheese Burger", "name_ar": "تشيز برغر", "price": 4.44},
                {"name": "Chicken Breast Burger", "name_ar": "تشكن برست برغر", "price": 4.44},
                {"name": "Lebanese Burger", "name_ar": "ليبانير برغر", "price": 3.89},
            ]},
            {"category_en": "Sandwiches & Snacks", "category_ar": "ساندويشات وسناك", "items": [
                {"name": "Francisco", "name_ar": "فرانسيسكو", "price": 4.16},
                {"name": "Chicken BBQ", "name_ar": "تشكن باربكيو", "price": 5.00},
                {"name": "Crispy", "name_ar": "كرسبي", "price": 3.89},
                {"name": "Escalope", "name_ar": "اسكالوب", "price": 3.89},
                {"name": "Tawook", "name_ar": "طاووق", "price": 4.16},
                {"name": "Fajita", "name_ar": "فاهيتا", "price": 4.44},
                {"name": "Chicken Sub", "name_ar": "تشكن ساب", "price": 4.17},
                {"name": "Philadelphia", "name_ar": "فيلادلفيا", "price": 5.56},
                {"name": "Twister", "name_ar": "تويستر", "price": 4.67},
            ]},
            {"category_en": "Shawarma", "category_ar": "شاورما", "items": [
                {"name": "Shawarma Arabi", "name_ar": "شاورما عربي", "price": 3.78},
                {"name": "Shawarma Tortilla", "name_ar": "شاورما تورتيا", "price": 4.22},
                {"name": "Doner Meat Turkish", "name_ar": "دونر لحمة تركي", "price": 5.33},
                {"name": "Shawarma Meat Arabi", "name_ar": "شاورما لحمة عربي", "price": 4.78},
                {"name": "Doner Chicken Turkish", "name_ar": "دونر دجاج تركي", "price": 4.22},
                {"name": "Doner Mix", "name_ar": "دونر ميكس", "price": 5.33},
            ]},
            {"category_en": "Meals", "category_ar": "وجبات", "items": [
                {"name": "Crispy Meal", "name_ar": "وجبة كرسبي", "price": 8.33},
                {"name": "Zinger Meal", "name_ar": "وجبة زنجر", "price": 8.33},
                {"name": "Crunchy Meal", "name_ar": "وجبة كرانشي", "price": 8.33},
            ]},
            {"category_en": "French Fries", "category_ar": "بطاطا", "items": [
                {"name": "Cheese Fries Large", "name_ar": "تشيز فرايز كبير", "price": 6.11},
                {"name": "Fries Large", "name_ar": "بطاطا كبير", "price": 4.44},
                {"name": "Fries Small", "name_ar": "بطاطا صغير", "price": 2.79},
                {"name": "Fries Sandwich", "name_ar": "بطاطا ساندويش", "price": 2.22},
            ]},
            {"category_en": "Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Soft Drink", "name_ar": "مشروب غازي", "price": 1.00},
                {"name": "Water", "name_ar": "مياه", "price": 0.50},
            ]},
        ]
    },
    {
        "name": "Hayat Doner",
        "name_ar": "حياة دونر",
        "category": "Shawarma",
        "menu": [
            {"category_en": "The Doner", "category_ar": "الدونر", "items": [
                {"name": "Beef Doner", "name_ar": "دونر لحمة", "price": 8.06},
                {"name": "Chicken Doner", "name_ar": "دونر دجاج", "price": 7.22},
                {"name": "Doner Mix", "name_ar": "دونر ميكس", "price": 7.50},
            ]},
            {"category_en": "Lebanese Shawarma", "category_ar": "شاورما لبناني", "items": [
                {"name": "Chicken Shawarma Small", "name_ar": "شاورما دجاج صغير", "price": 3.06},
                {"name": "Chicken Shawarma Large", "name_ar": "شاورما دجاج كبير", "price": 4.44},
                {"name": "Beef Shawarma Small", "name_ar": "شاورما لحمة صغير", "price": 4.17},
                {"name": "Beef Shawarma Large", "name_ar": "شاورما لحمة كبير", "price": 5.56},
            ]},
            {"category_en": "Tortilla", "category_ar": "تورتيا", "items": [
                {"name": "Beef Tortilla", "name_ar": "تورتيا لحمة", "price": 6.11},
                {"name": "Chicken Tortilla", "name_ar": "تورتيا دجاج", "price": 5.83},
                {"name": "Tortilla Mix", "name_ar": "تورتيا ميكس", "price": 5.83},
            ]},
            {"category_en": "Plates", "category_ar": "صحون", "items": [
                {"name": "Chicken Leb Plate", "name_ar": "صحن دجاج لبناني", "price": 11.11},
                {"name": "Beef Leb Plate", "name_ar": "صحن لحمة لبناني", "price": 12.22},
                {"name": "Mix Leb Combo", "name_ar": "صحن لبناني ميكس", "price": 11.67},
                {"name": "Chicken Turkish Plate", "name_ar": "صحن دجاج تركي", "price": 11.67},
                {"name": "Beef Turkish Plate", "name_ar": "صحن لحمة تركي", "price": 12.78},
            ]},
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "Beef Turkish Burger", "name_ar": "برغر لحمة تركي", "price": 6.39},
                {"name": "Lebanese Beef Burger", "name_ar": "برغر لحمة لبناني", "price": 5.28},
            ]},
            {"category_en": "Potatoes", "category_ar": "بطاطا", "items": [
                {"name": "Baked Potato", "name_ar": "بطاطا مشوية", "price": 6.39},
                {"name": "French Fries Large", "name_ar": "بطاطا مقلية كبير", "price": 3.06},
                {"name": "French Fries Small", "name_ar": "بطاطا مقلية صغير", "price": 1.89},
            ]},
            {"category_en": "Appetizers", "category_ar": "مقبلات", "items": [
                {"name": "Hummus Plate", "name_ar": "صحن حمص", "price": 3.06},
                {"name": "Grape Leaves", "name_ar": "ورق عنب", "price": 5.00},
                {"name": "Fried Kibbeh", "name_ar": "كبة مقلية", "price": 5.56},
            ]},
            {"category_en": "Salads", "category_ar": "سلطات", "items": [
                {"name": "Fattoush", "name_ar": "فتوش", "price": 2.78},
                {"name": "Turkish Salad", "name_ar": "سلطة تركية", "price": 3.33},
            ]},
            {"category_en": "Desserts", "category_ar": "حلويات", "items": [
                {"name": "Knafeh", "name_ar": "كنافة", "price": 5.56},
                {"name": "Mouhalabiya", "name_ar": "مهلبية", "price": 1.67},
                {"name": "Rice Pudding", "name_ar": "رز بحليب", "price": 1.67},
            ]},
            {"category_en": "Beverages", "category_ar": "مشروبات", "items": [
                {"name": "Soft Drink", "name_ar": "مشروب غازي", "price": 1.11},
                {"name": "Laban Ayran", "name_ar": "لبن عيران", "price": 1.11},
                {"name": "Water", "name_ar": "ماء", "price": 0.39},
                {"name": "Fresh Orange Juice", "name_ar": "عصير برتقال", "price": 1.89},
            ]},
        ]
    },
    {
        "name": "Popeyes",
        "name_ar": "بوبايز",
        "category": "Fried Chicken",
        "menu": [
            {"category_en": "Sandwiches", "category_ar": "ساندويشات", "items": [
                {"name": "Cajun Chicken Sandwich", "name_ar": "ساندويش دجاج كاجن", "price": 9.67},
                {"name": "Creole Chicken Sandwich", "name_ar": "ساندويش كريول", "price": 9.67},
                {"name": "Chicken Sandwich", "name_ar": "ساندويش دجاج", "price": 9.67},
                {"name": "Chicken Wrap", "name_ar": "تشيكن راب", "price": 9.67},
                {"name": "Cajun Fish Sandwich", "name_ar": "ساندويش سمك كاجن", "price": 9.67},
            ]},
            {"category_en": "Seafood", "category_ar": "مأكولات بحرية", "items": [
                {"name": "Butterfly Shrimp", "name_ar": "روبيان الفراشة", "price": 10.17},
                {"name": "Fish & Shrimp", "name_ar": "سمك وروبيان", "price": 9.17},
                {"name": "Cajun Fish", "name_ar": "سمك كاجن", "price": 8.83},
            ]},
            {"category_en": "Tenders", "category_ar": "تندرز", "items": [
                {"name": "Tenders 3Pcs", "name_ar": "تندرز ٣ قطع", "price": 6.17},
                {"name": "Tenders 5Pcs", "name_ar": "تندرز ٥ قطع", "price": 9.50},
                {"name": "Tenders 12Pcs", "name_ar": "تندرز ١٢ قطعة", "price": 26.67},
            ]},
            {"category_en": "Chicken Combos", "category_ar": "كومبو الدجاج", "items": [
                {"name": "2Pcs Combo", "name_ar": "وجبة ٢ قطع", "price": 7.17},
                {"name": "3Pcs Combo", "name_ar": "وجبة ٣ قطع", "price": 9.28},
                {"name": "4Pcs Combo", "name_ar": "وجبة ٤ قطع", "price": 10.33},
            ]},
            {"category_en": "Family Meals", "category_ar": "وجبات عائلية", "items": [
                {"name": "12Pcs Family Meal", "name_ar": "وجبة ١٢ قطعة", "price": 35.56},
                {"name": "16Pcs Family Meal", "name_ar": "وجبة ١٦ قطعة", "price": 40.56},
                {"name": "20Pcs Family Meal", "name_ar": "وجبة ٢٠ قطعة", "price": 58.89},
            ]},
            {"category_en": "Sides", "category_ar": "جوانب", "items": [
                {"name": "Fries Small", "name_ar": "بطاطا صغير", "price": 2.11},
                {"name": "Fries Large", "name_ar": "بطاطا كبير", "price": 3.67},
                {"name": "Coleslaw Small", "name_ar": "كولسلو صغير", "price": 2.11},
                {"name": "Biscuit", "name_ar": "بسكويت", "price": 0.33},
            ]},
            {"category_en": "Kids Meals", "category_ar": "وجبات أطفال", "items": [
                {"name": "Kids Meal", "name_ar": "وجبة طفل", "price": 5.11},
            ]},
        ]
    },
    {
        "name": "SEEK",
        "name_ar": "سيك",
        "category": "Sandwiches",
        "menu": [
            {"category_en": "Sandwiches", "category_ar": "ساندويشات", "items": [
                {"name": "Roast Beef", "name_ar": "روست بيف", "price": 6.67},
                {"name": "Beef Tongue", "name_ar": "لسان بقر", "price": 6.67},
                {"name": "Sujuk", "name_ar": "سجق", "price": 5.00},
                {"name": "Makanek", "name_ar": "مقانق", "price": 5.00},
                {"name": "Chicken Liver", "name_ar": "سودة دجاج", "price": 3.89},
                {"name": "Philadelphia", "name_ar": "فيلادلفيا", "price": 5.56},
                {"name": "Beef Shawarma", "name_ar": "شاورما لحمة", "price": 5.00},
                {"name": "Francisco", "name_ar": "فرانسيسكو", "price": 5.00},
                {"name": "Tawook", "name_ar": "طاووق", "price": 5.00},
                {"name": "Fajita", "name_ar": "فاهيتا", "price": 5.00},
                {"name": "Chicken Shawarma", "name_ar": "شاورما دجاج", "price": 3.89},
                {"name": "Crispy", "name_ar": "كرسبي", "price": 3.33},
                {"name": "Escalope", "name_ar": "اسكالوب", "price": 3.33},
                {"name": "Chicken Sub", "name_ar": "تشيكن ساب", "price": 5.00},
                {"name": "Shrimp", "name_ar": "قريدس", "price": 5.56},
                {"name": "Tuna", "name_ar": "تونا", "price": 3.89},
                {"name": "Special Seek", "name_ar": "سبيشل سيك", "price": 8.89},
            ]},
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "Lebanese Beef", "name_ar": "برغر لبناني", "price": 4.44},
                {"name": "Beef Cheese", "name_ar": "برغر جبنة", "price": 5.00},
                {"name": "Chicken Burger", "name_ar": "برغر دجاج", "price": 4.44},
                {"name": "Mushroom Burger", "name_ar": "برغر مشروم", "price": 6.67},
            ]},
            {"category_en": "Pasta", "category_ar": "باستا", "items": [
                {"name": "Chicken Pasta", "name_ar": "باستا دجاج", "price": 5.56},
                {"name": "Shrimp Pasta", "name_ar": "باستا قريدس", "price": 6.67},
            ]},
            {"category_en": "Appetizers", "category_ar": "مقبلات", "items": [
                {"name": "Fries", "name_ar": "بطاطا", "price": 2.22},
                {"name": "Fries Plate", "name_ar": "صحن بطاطا", "price": 3.89},
                {"name": "Mozzarella Sticks", "name_ar": "موزاريلا ستيكس", "price": 3.89},
            ]},
            {"category_en": "Salads", "category_ar": "سلطات", "items": [
                {"name": "Tuna Salad", "name_ar": "سلطة تونا", "price": 5.56},
                {"name": "Crab Salad", "name_ar": "سلطة كراب", "price": 5.56},
                {"name": "Caesar Salad", "name_ar": "سلطة سيزر", "price": 5.56},
            ]},
            {"category_en": "Meals", "category_ar": "وجبات", "items": [
                {"name": "Lebanese Beef Burger Meal", "name_ar": "وجبة برغر لبناني", "price": 7.78},
                {"name": "Chicken Burger Meal", "name_ar": "وجبة برغر دجاج", "price": 6.67},
                {"name": "Beef Shawarma Meal", "name_ar": "وجبة شاورما لحمة", "price": 8.89},
                {"name": "Chicken Shawarma Meal", "name_ar": "وجبة شاورما دجاج", "price": 7.78},
                {"name": "Crispy Meal", "name_ar": "وجبة كرسبي", "price": 7.78},
            ]},
            {"category_en": "Beverages", "category_ar": "مشروبات", "items": [
                {"name": "Soft Drink", "name_ar": "مشروب غازي", "price": 1.11},
                {"name": "Water", "name_ar": "مياه", "price": 0.56},
            ]},
        ]
    },
    {
        "name": "SUBMARINE",
        "name_ar": "صبمارين",
        "category": "Sandwiches",
        "menu": [
            {"category_en": "Sandwiches", "category_ar": "ساندويشات", "items": [
                {"name": "Spicy Steak", "name_ar": "ستيك حار", "price": 6.89},
                {"name": "Chinese", "name_ar": "صيني", "price": 5.56},
                {"name": "Mexican", "name_ar": "مكسيكان", "price": 6.00},
                {"name": "Tawook", "name_ar": "طاووق", "price": 5.44},
                {"name": "Francisco", "name_ar": "فرانسيسكو", "price": 6.11},
                {"name": "Crab", "name_ar": "كراب", "price": 5.89},
                {"name": "Shrimp", "name_ar": "قريدس", "price": 7.44},
                {"name": "Supreme", "name_ar": "سوبريم", "price": 6.33},
                {"name": "Makanek", "name_ar": "مقانق", "price": 5.78},
                {"name": "Spicy Fajita", "name_ar": "فاهيتا حارة", "price": 7.22},
                {"name": "Philadelphia", "name_ar": "فيلادلفيا", "price": 7.33},
                {"name": "Escalope", "name_ar": "اسكالوب", "price": 5.56},
                {"name": "Twister", "name_ar": "تويستر", "price": 6.11},
                {"name": "Honey Mustard", "name_ar": "هني ماسترد", "price": 6.67},
                {"name": "Chicken Sub", "name_ar": "تشيكن ساب", "price": 6.11},
                {"name": "Sojok", "name_ar": "سجق", "price": 5.78},
                {"name": "Dynamite Chicken", "name_ar": "دايناميت دجاج", "price": 7.22},
                {"name": "Truffle Steak", "name_ar": "ترافل ستيك", "price": 8.67},
                {"name": "Dynamite Shrimp", "name_ar": "دايناميت قريدس", "price": 8.67},
            ]},
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "Lebanese Burger", "name_ar": "برغر لبناني", "price": 6.89},
                {"name": "Submarine Burger", "name_ar": "برغر صبمارين", "price": 8.44},
                {"name": "Classic Smash", "name_ar": "سماش كلاسيك", "price": 7.11},
                {"name": "Mozzarella Burger", "name_ar": "برغر موزاريلا", "price": 8.44},
            ]},
        ]
    },
    {
        "name": "Krispy Tender",
        "name_ar": "كريسبي تندر",
        "category": "Fried Chicken",
        "menu": [
            {"category_en": "Meals & Combos", "category_ar": "وجبات وكومبو", "items": [
                {"name": "Krispy Meal 3 Pcs", "name_ar": "وجبة كريسبي ٣ قطع", "description": "3 Pcs Krispy, Coleslaw, Fries and Soft Drink", "price": 10.00},
                {"name": "Krispy Meal 5 Pcs", "name_ar": "وجبة كريسبي ٥ قطع", "price": 6.11},
                {"name": "Krispy Meal 8 Pcs", "name_ar": "وجبة كريسبي ٨ قطع", "price": 20.00},
                {"name": "Twins Combo", "name_ar": "توينز كومبو", "price": 8.33},
                {"name": "Friends Meal", "name_ar": "وجبة أصدقاء", "price": 21.11},
                {"name": "Family Meal", "name_ar": "وجبة عائلية", "price": 37.22},
                {"name": "Combo Meal", "name_ar": "كومبو ميل", "price": 6.67},
                {"name": "Double Combo Meal", "name_ar": "دبل كومبو", "price": 13.33},
                {"name": "Kids Meal Burger", "name_ar": "وجبة أطفال برغر", "price": 6.11},
                {"name": "Kids Meal Nuggets", "name_ar": "وجبة أطفال ناغتس", "price": 6.11},
            ]},
            {"category_en": "Sandwiches & Burgers", "category_ar": "ساندويشات وبرغر", "items": [
                {"name": "Cheese Royale Deluxe", "name_ar": "تشيز رويال ديلوكس", "price": 6.67},
                {"name": "Royale Double Up", "name_ar": "رويال دبل أب", "price": 9.44},
                {"name": "Delight Wrap", "name_ar": "ديلايت راب", "price": 5.56},
                {"name": "BBQ Wrap", "name_ar": "باربكيو راب", "price": 5.56},
                {"name": "KT Burger", "name_ar": "كي تي برغر", "price": 6.11},
            ]},
            {"category_en": "Sides & Appetizers", "category_ar": "جوانب ومقبلات", "items": [
                {"name": "Tender Loaded Fries", "name_ar": "تندر لودد فرايز", "price": 6.67},
                {"name": "Krispy 1 Pc", "name_ar": "كريسبي قطعة", "price": 2.22},
                {"name": "Coleslaw", "name_ar": "كولسلو", "price": 2.22},
                {"name": "Cheese Fries", "name_ar": "بطاطا بالجبنة", "price": 4.89},
                {"name": "Fries", "name_ar": "بطاطا", "price": 3.67},
                {"name": "Mozzarella Sticks", "name_ar": "موزاريلا ستيكس", "price": 3.67},
            ]},
            {"category_en": "Beverages", "category_ar": "مشروبات", "items": [
                {"name": "Soft Drink", "name_ar": "مشروب غازي", "price": 1.22},
                {"name": "Water", "name_ar": "مياه", "price": 0.56},
            ]},
        ]
    },
    {
        "name": "Smoking Hub",
        "name_ar": "سموكينغ هاب",
        "category": "Grills",
        "menu": [
            {"category_en": "Starters", "category_ar": "مقبلات", "items": [
                {"name": "French Fries 300g", "name_ar": "بطاطا ٣٠٠ غ", "price": 4.00},
                {"name": "Wedges 300g", "name_ar": "ودجز ٣٠٠ غ", "price": 5.00},
                {"name": "Mozzarella Sticks", "name_ar": "موزاريلا ستيكس", "price": 5.00},
                {"name": "Curly Fries 300g", "name_ar": "كيرلي فرايز ٣٠٠ غ", "price": 5.00},
                {"name": "Brisket Triangles", "name_ar": "مثلثات بريسكت", "price": 5.00},
                {"name": "Smoked Brisket Boat", "name_ar": "بريسكت بوت", "price": 5.00},
            ]},
            {"category_en": "Salads", "category_ar": "سلطات", "items": [
                {"name": "Noodles Salad", "name_ar": "سلطة نودلز", "price": 11.00},
                {"name": "Quinoa Salad", "name_ar": "سلطة كينوا", "price": 12.00},
                {"name": "Broccoli Salad", "name_ar": "سلطة بروكلي", "price": 12.00},
            ]},
            {"category_en": "Sandwiches", "category_ar": "ساندويشات", "items": [
                {"name": "Hotdog", "name_ar": "هوت دوغ", "price": 4.00},
                {"name": "Special Hotdog", "name_ar": "هوت دوغ سبيشل", "price": 5.50},
            ]},
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "Caramelized Burger (Patty)", "name_ar": "برغر كراميل (باتي)", "price": 12.50},
                {"name": "Caramelized Burger (Shredded)", "name_ar": "برغر كراميل (مفروم)", "price": 13.00},
                {"name": "Brisket Burger", "name_ar": "برغر بريسكت", "price": 13.50},
                {"name": "Texas Burger", "name_ar": "برغر تكساس", "price": 10.00},
                {"name": "Classic Beef (Patty)", "name_ar": "كلاسيك بيف (باتي)", "price": 8.50},
                {"name": "Classic Beef (Shredded)", "name_ar": "كلاسيك بيف (مفروم)", "price": 9.50},
                {"name": "Mushroom Burger (Patty)", "name_ar": "مشروم برغر (باتي)", "price": 14.00},
                {"name": "Mushroom Burger (Shredded)", "name_ar": "مشروم برغر (مفروم)", "price": 14.50},
            ]},
            {"category_en": "Plates", "category_ar": "صحون", "items": [
                {"name": "Brisket Plate 250g", "name_ar": "صحن بريسكت ٢٥٠ غ", "price": 18.00},
                {"name": "Cheeks Plate", "name_ar": "صحن خدود", "price": 18.00},
            ]},
            {"category_en": "Add-ons", "category_ar": "إضافات", "items": [
                {"name": "Combo Deal", "name_ar": "كومبو", "description": "Fries, coleslaw & soft drink", "price": 4.50},
                {"name": "Honey Cup", "name_ar": "عسل", "price": 3.00},
            ]},
        ]
    },
]

# Category mappings
CATEGORY_MAP = {
    "Shawarma": "Shawarma",
    "Fried Chicken": "Sandwiches",
    "Sandwiches": "Sandwiches",
    "Grills": "Grills",
}


async def get_category(session, cat_key: str):
    """Get restaurant category from database"""
    cat_name = CATEGORY_MAP.get(cat_key, "Sandwiches")
    result = await session.execute(
        select(RestaurantCategory).where(RestaurantCategory.name == cat_name)
    )
    return result.scalars().first()


async def import_restaurants():
    """Import all restaurants"""
    async with AsyncSessionLocal() as session:
        for rest_data in RESTAURANTS_DATA:
            print(f"Importing: {rest_data['name']}...")

            # Get category
            category = await get_category(session, rest_data.get("category", "Sandwiches"))

            # Check if restaurant exists
            result = await session.execute(
                select(Restaurant).where(Restaurant.name == rest_data["name"])
            )
            restaurant = result.scalars().first()

            if restaurant:
                print(f"  Restaurant '{rest_data['name']}' already exists, skipping...")
                continue

            # Create restaurant
            restaurant = Restaurant(
                name=rest_data["name"],
                name_ar=rest_data.get("name_ar"),
                is_active=True,
                category_id=category.id if category else None,
                subscription_tier="basic"
            )
            session.add(restaurant)
            await session.flush()

            # Create menu
            menu = Menu(
                restaurant_id=restaurant.id,
                name="Main Menu",
                name_ar="القائمة الرئيسية",
                is_active=True
            )
            session.add(menu)
            await session.flush()

            # Create categories and items
            for cat_order, cat_data in enumerate(rest_data.get("menu", [])):
                menu_category = Category(
                    menu_id=menu.id,
                    name=cat_data.get("category_en", "Other"),
                    name_ar=cat_data.get("category_ar"),
                    order=cat_order
                )
                session.add(menu_category)
                await session.flush()

                # Create items
                for item_order, item_data in enumerate(cat_data.get("items", [])):
                    menu_item = MenuItem(
                        category_id=menu_category.id,
                        name=item_data.get("name", ""),
                        name_ar=item_data.get("name_ar"),
                        description=item_data.get("description"),
                        price=item_data.get("price"),
                        is_available=True,
                        order=item_order
                    )
                    session.add(menu_item)

            print(f"  ✓ Created {rest_data['name']}")

        await session.commit()
        print("\n✅ All restaurants imported successfully!")


if __name__ == "__main__":
    asyncio.run(import_restaurants())
