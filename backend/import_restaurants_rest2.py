#!/usr/bin/env python3
"""
Import script for ALL restaurants from rest2.md (32 unique restaurants)
Exchange rate: 1 USD = 90,000 LBP
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.restaurant import Restaurant, RestaurantCategory
from app.models.menu import Menu, Category, MenuItem, MenuItemVariant

# Exchange rate for LBP to USD
LBP_TO_USD = 90000

# Map to EXISTING categories only (from add_categories.py)
# Existing: Offers, Snacks, Shawarma, Sandwiches, Pizza, Burgers, Grills, Home Food, Sweets, Beverages
CATEGORY_MAP = {
    "Sandwiches": "Sandwiches",
    "Burgers": "Burgers",
    "Shawarma": "Shawarma",
    "Grills": "Grills",
    "Home Food": "Home Food",
    "Pizza": "Pizza",
    "Snacks": "Snacks",
    "Sweets": "Sweets",
    "Beverages": "Beverages",
    "Offers": "Offers",
    "Seafood": "Home Food",
    "Pasta": "Snacks",
    "Breakfast": "Home Food",
}

RESTAURANTS_DATA = [
    # 1. Ramadan Juice
    {
        "name_en": "Ramadan Juice",
        "name_ar": "عصير رمضان",
        "category": "Beverages",
        "categories": [
            {"name_en": "Natural Juices", "name_ar": "عصائر طبيعية", "items": [
                {"name_en": "Mango", "name_ar": "منغا", "price": 2.00, "has_variants": True, "variants": [{"name": "Small", "price": 2.00}, {"name": "Large", "price": 6.50}]},
                {"name_en": "Strawberry", "name_ar": "فريز", "price": 2.00, "has_variants": True, "variants": [{"name": "Small", "price": 2.00}, {"name": "Large", "price": 6.00}]},
                {"name_en": "Orange", "name_ar": "برتقال", "price": 1.50, "has_variants": True, "variants": [{"name": "Small", "price": 1.50}, {"name": "Large", "price": 5.50}]},
                {"name_en": "Lemonade", "name_ar": "ليموناضة", "price": 1.60, "has_variants": True, "variants": [{"name": "Small", "price": 1.60}, {"name": "Large", "price": 5.50}]},
                {"name_en": "Watermelon", "name_ar": "بطيخ", "price": 3.30},
                {"name_en": "Apple", "name_ar": "تفاح", "price": 1.60},
                {"name_en": "Carrot", "name_ar": "جزر", "price": 1.60},
                {"name_en": "Pomegranate", "name_ar": "رمان", "price": 2.50},
            ]},
            {"name_en": "Cocktails", "name_ar": "كوكتيلات", "items": [
                {"name_en": "Cocktail", "name_ar": "كوكتيل", "price": 1.60},
                {"name_en": "Avocado", "name_ar": "افوكا", "price": 5.50},
                {"name_en": "Avocado + Cocktail", "name_ar": "افوكا + كوكتيل", "price": 3.80},
            ]},
            {"name_en": "Milkshakes", "name_ar": "ميلك شيك", "items": [
                {"name_en": "Oreo Milkshake", "name_ar": "ميلك شيك اوريو", "price": 4.50},
                {"name_en": "Nutella Milkshake", "name_ar": "ميلك شيك نوتيلا", "price": 4.50},
                {"name_en": "Lotus Milkshake", "name_ar": "ميلك شيك لوتس", "price": 4.50},
            ]},
        ]
    },

    # 2. Al Abdalla
    {
        "name_en": "Al Abdalla",
        "name_ar": "العبدالله",
        "category": "Grills",
        "categories": [
            {"name_en": "BBQ Chicken", "name_ar": "دجاج مشوي", "items": [
                {"name_en": "Chicken - Whole", "name_ar": "فروج كامل", "price": 18.00},
                {"name_en": "Chicken - Half", "name_ar": "نصف فروج", "price": 9.50},
                {"name_en": "Chicken Legs - Whole", "name_ar": "فخاذ كاملة", "price": 18.00},
                {"name_en": "Chicken Breasts - Whole", "name_ar": "صدور كاملة", "price": 19.00},
            ]},
            {"name_en": "Sandwiches", "name_ar": "ساندويشات", "items": [
                {"name_en": "Chicken Sandwich Large", "name_ar": "ساندويش دجاج كبير", "price": 7.50},
                {"name_en": "Chicken Sandwich Medium", "name_ar": "ساندويش دجاج وسط", "price": 4.50},
                {"name_en": "Fries Sandwich", "name_ar": "ساندويش بطاطا", "price": 2.50},
            ]},
            {"name_en": "Sides", "name_ar": "جوانب", "items": [
                {"name_en": "Fries Plate", "name_ar": "صحن بطاطا", "price": 5.00},
                {"name_en": "Hummus", "name_ar": "حمص", "price": 4.00},
                {"name_en": "Garlic", "name_ar": "ثوم", "price": 0.80},
            ]},
        ]
    },

    # 3. Mishta7
    {
        "name_en": "Mishta7",
        "name_ar": "مشتاق",
        "category": "Sandwiches",
        "categories": [
            {"name_en": "Sandwiches", "name_ar": "ساندويشات", "items": [
                {"name_en": "Chicken Escalope", "name_ar": "اسكالوب دجاج", "price": 3.33},
                {"name_en": "Tawook", "name_ar": "طاووق", "price": 3.33},
                {"name_en": "Makanik", "name_ar": "مقانق", "price": 3.33},
                {"name_en": "Djej fahem", "name_ar": "دجاج فحم", "price": 3.33},
                {"name_en": "Chicken Crispy", "name_ar": "كرسبي دجاج", "price": 4.44},
                {"name_en": "Chicken Curry", "name_ar": "دجاج كاري", "price": 3.89},
                {"name_en": "Chicken Fajita", "name_ar": "فاهيتا دجاج", "price": 4.44},
                {"name_en": "Batata Sandwich", "name_ar": "ساندويش بطاطا", "price": 1.67},
            ]},
            {"name_en": "Beef Burgers", "name_ar": "برغر لحم", "items": [
                {"name_en": "American Burger", "name_ar": "برغر امريكي", "price": 4.44},
                {"name_en": "Classic Burger", "name_ar": "برغر كلاسيك", "price": 4.44},
            ]},
        ]
    },

    # 4. Mister Saj
    {
        "name_en": "Mister Saj",
        "name_ar": "مستر صاج",
        "category": "Home Food",
        "categories": [
            {"name_en": "Breakfast", "name_ar": "فطور", "items": [
                {"name_en": "Zaatar", "name_ar": "زعتر", "price": 0.89},
                {"name_en": "Labneh", "name_ar": "لبنة", "price": 2.22},
                {"name_en": "Keshek", "name_ar": "كشك", "price": 2.22},
                {"name_en": "Akkawi cheese", "name_ar": "جبنة عكاوي", "price": 2.22},
                {"name_en": "Halloum Meshwi", "name_ar": "حلوم مشوي", "price": 2.56},
                {"name_en": "Four Cheese", "name_ar": "اربع اجبان", "price": 3.89},
                {"name_en": "Turkey & Cheese", "name_ar": "حبش وجبنة", "price": 4.44},
            ]},
            {"name_en": "Chicken", "name_ar": "دجاج", "items": [
                {"name_en": "Boneless", "name_ar": "مسحب", "price": 5.00},
                {"name_en": "Fajita & cheese", "name_ar": "فاهيتا وجبنة", "price": 5.00},
                {"name_en": "Shawarma", "name_ar": "شاورما", "price": 5.00},
                {"name_en": "Tawook", "name_ar": "طاووق", "price": 5.00},
            ]},
            {"name_en": "Meat", "name_ar": "لحمة", "items": [
                {"name_en": "Hamburger W cheese", "name_ar": "همبرغر وجبنة", "price": 5.00},
                {"name_en": "Steak & cheese", "name_ar": "ستيك وجبنة", "price": 5.56},
                {"name_en": "Soujok & Cheese", "name_ar": "سجق وجبنة", "price": 5.00},
            ]},
        ]
    },

    # 5. Check In
    {
        "name_en": "Check In",
        "name_ar": "تشك ان",
        "category": "Sandwiches",
        "phone": "76 006 004",
        "categories": [
            {"name_en": "Appetizers", "name_ar": "مقبلات", "items": [
                {"name_en": "Hummus", "name_ar": "حمص", "price": 2.78},
                {"name_en": "Fries Small", "name_ar": "بطاطا صغير", "price": 2.78},
                {"name_en": "Fries Large", "name_ar": "بطاطا كبير", "price": 3.89},
                {"name_en": "Cheese Fries", "name_ar": "تشيز فرايز", "price": 4.44},
            ]},
            {"name_en": "Sandwiches", "name_ar": "سندويشات", "items": [
                {"name_en": "Chicken Sandwich", "name_ar": "سندويش دجاج", "price": 4.00},
                {"name_en": "Tawook", "name_ar": "طاووق", "price": 4.00},
                {"name_en": "Twister", "name_ar": "تويستر", "price": 5.00},
                {"name_en": "Check In Burger", "name_ar": "تشك ان برغر", "price": 4.44},
            ]},
            {"name_en": "Crispy Meals", "name_ar": "وجبات كرسبي", "items": [
                {"name_en": "Crispy 7 pcs", "name_ar": "كرسبي 7 قطع", "price": 7.78},
                {"name_en": "Crispy 12 pcs", "name_ar": "كرسبي 12 قطعة", "price": 12.22},
            ]},
        ]
    },

    # 6. Aura (Cafe)
    {
        "name_en": "Aura",
        "name_ar": "أورا",
        "category": "Beverages",
        "phone": "01 820 874",
        "categories": [
            {"name_en": "Hot Drinks", "name_ar": "مشروبات ساخنة", "items": [
                {"name_en": "Espresso", "name_ar": "اسبريسو", "price": 1.67},
                {"name_en": "Americano", "name_ar": "امريكانو", "price": 3.33},
                {"name_en": "Cappuccino", "name_ar": "كابتشينو", "price": 3.33},
                {"name_en": "Turkish Coffee", "name_ar": "قهوة تركية", "price": 3.33},
            ]},
            {"name_en": "Latte", "name_ar": "لاتيه", "items": [
                {"name_en": "Spanish Latte", "name_ar": "سبانيش لاتيه", "price": 4.00},
                {"name_en": "Mocha Latte", "name_ar": "موكا لاتيه", "price": 4.00},
                {"name_en": "Caramel Latte", "name_ar": "كراميل لاتيه", "price": 4.00},
            ]},
            {"name_en": "Matcha", "name_ar": "ماتشا", "items": [
                {"name_en": "Regular Matcha", "name_ar": "ماتشا عادي", "price": 4.44},
                {"name_en": "Vanilla Matcha", "name_ar": "ماتشا فانيلا", "price": 4.44},
            ]},
        ]
    },

    # 7. Shaar (Sweets)
    {
        "name_en": "Shaar",
        "name_ar": "شعار",
        "category": "Sweets",
        "categories": [
            {"name_en": "Ice Cream", "name_ar": "بوظة", "items": [
                {"name_en": "Ice Cream 1 Kilo", "name_ar": "بوظة كيلو", "price": 7.78},
                {"name_en": "Ice Cream Half Kilo", "name_ar": "بوظة نص كيلو", "price": 3.89},
                {"name_en": "Ice Cream Ball", "name_ar": "بول بوظة", "price": 0.56},
            ]},
            {"name_en": "Crepe", "name_ar": "كريب", "items": [
                {"name_en": "Nutella Crepe", "name_ar": "كريب نيوتيلا", "price": 3.33},
                {"name_en": "Classic Crepe", "name_ar": "كريب كلاسيك", "price": 2.78},
                {"name_en": "Lotus Crepe", "name_ar": "كريب لوتوس", "price": 3.33},
                {"name_en": "Oreo Crepe", "name_ar": "كريب أوريو", "price": 3.33},
                {"name_en": "Kinder Crepe", "name_ar": "كريب كندر", "price": 3.33},
                {"name_en": "Fruit Crepe", "name_ar": "كريب فواكه", "price": 3.89},
            ]},
            {"name_en": "Waffle", "name_ar": "وافل", "items": [
                {"name_en": "Nutella Waffle", "name_ar": "وافل نوتيلا", "price": 4.44},
                {"name_en": "Lotus Waffle", "name_ar": "وافل لوتوس", "price": 4.44},
            ]},
        ]
    },

    # 8. Foul Al Zaeem
    {
        "name_en": "Foul Al Zaeem",
        "name_ar": "فول الزعيم",
        "category": "Home Food",
        "categories": [
            {"name_en": "Foul Boxes", "name_ar": "علب", "items": [
                {"name_en": "Foul", "name_ar": "فول", "price": 1.67, "has_variants": True, "variants": [{"name": "Small", "price": 1.67}, {"name": "Large", "price": 3.33}]},
                {"name_en": "Foul with Tahini", "name_ar": "فول بطحينة", "price": 2.00},
                {"name_en": "Msabbaha", "name_ar": "مسبحة", "price": 1.67},
                {"name_en": "Balila", "name_ar": "بليلة", "price": 1.67},
                {"name_en": "Fatteh", "name_ar": "فتة", "price": 4.44},
            ]},
            {"name_en": "Plates", "name_ar": "صحون", "items": [
                {"name_en": "Hummus", "name_ar": "حمص", "price": 1.67},
                {"name_en": "Eggs", "name_ar": "بيض", "price": 3.50},
            ]},
        ]
    },

    # 9. Falafel Al Zaeem
    {
        "name_en": "Falafel Al Zaeem",
        "name_ar": "فلافل الزعيم",
        "category": "Home Food",
        "phone": "81626170",
        "categories": [
            {"name_en": "Sandwiches", "name_ar": "سندويشات", "items": [
                {"name_en": "Falafel Sandwich", "name_ar": "سندويش فلافل", "price": 1.00},
                {"name_en": "Falafel with Hummus", "name_ar": "فلافل مع حمص", "price": 1.50},
                {"name_en": "Special Falafel", "name_ar": "فلافل سبيسيال", "price": 2.00},
            ]},
            {"name_en": "Plates", "name_ar": "صحون", "items": [
                {"name_en": "Falafel Plate", "name_ar": "صحن فلافل", "price": 3.00},
                {"name_en": "Mixed Plate", "name_ar": "صحن مشكل", "price": 4.00},
            ]},
        ]
    },

    # 10. Favourite
    {
        "name_en": "Favourite",
        "name_ar": "فيفوريت",
        "category": "Sandwiches",
        "categories": [
            {"name_en": "Sandwiches", "name_ar": "سندويشات", "items": [
                {"name_en": "Tawook", "name_ar": "طاووق", "price": 3.00},
                {"name_en": "Grilled Chicken", "name_ar": "دجاج محمر", "price": 3.00},
                {"name_en": "BBQ Chicken", "name_ar": "دجاج باربكيو", "price": 3.00},
                {"name_en": "Chinese Chicken", "name_ar": "دجاج صيني", "price": 3.00},
                {"name_en": "Chicken Liver", "name_ar": "سوده دجاج", "price": 3.00},
                {"name_en": "Roast Beef", "name_ar": "روستو لحمه", "price": 3.00},
                {"name_en": "Escalope", "name_ar": "اسكالوب", "price": 3.00},
                {"name_en": "Crispy", "name_ar": "كرسبي", "price": 3.00},
                {"name_en": "Chicken Sub", "name_ar": "تشكن ساب", "price": 4.00},
                {"name_en": "Crab", "name_ar": "كراب", "price": 3.00},
            ]},
        ]
    },

    # 11. Brunch
    {
        "name_en": "Brunch",
        "name_ar": "برانش",
        "category": "Sandwiches",
        "categories": [
            {"name_en": "Appetizers", "name_ar": "مقبلات", "items": [
                {"name_en": "French Fries", "name_ar": "بطاطا مقلية", "price": 3.00},
                {"name_en": "Wedges fries", "name_ar": "بطاطا ودجز", "price": 4.00},
                {"name_en": "Mozzarella sticks", "name_ar": "موزاريلا ستيكس", "price": 4.00},
            ]},
            {"name_en": "Bagels", "name_ar": "بيغل", "items": [
                {"name_en": "Labneh Bagel", "name_ar": "بيغل لبنة", "price": 3.00},
                {"name_en": "Avocado eggs bagel", "name_ar": "بيغل افوكادو وبيض", "price": 5.00},
                {"name_en": "Halloumi pesto bagel", "name_ar": "بيغل حلوم بيستو", "price": 4.00},
                {"name_en": "Fried chicken bagel", "name_ar": "بيغل دجاج مقلي", "price": 6.00},
                {"name_en": "Beef burger bagel", "name_ar": "بيغل برغر لحم", "price": 6.00},
                {"name_en": "Philly cheesesteak bagel", "name_ar": "بيغل فيلي تشيز ستيك", "price": 8.00},
            ]},
            {"name_en": "Salad", "name_ar": "سلطات", "items": [
                {"name_en": "Caesar Salad", "name_ar": "سلطة سيزر", "price": 6.00},
                {"name_en": "Crab salad", "name_ar": "سلطة كراب", "price": 8.00},
            ]},
        ]
    },

    # 12. Akleh
    {
        "name_en": "Akleh",
        "name_ar": "أكلة",
        "category": "Sandwiches",
        "categories": [
            {"name_en": "Burgers", "name_ar": "برغر", "items": [
                {"name_en": "Lebanese burger", "name_ar": "برغر لبناني", "price": 4.44},
                {"name_en": "Classic burgers", "name_ar": "برغر كلاسيك", "price": 4.44},
                {"name_en": "Cheese burger", "name_ar": "تشيز برغر", "price": 5.00},
                {"name_en": "Double cheese burger", "name_ar": "دوبل تشيز برغر", "price": 6.67},
            ]},
            {"name_en": "Sandwiches", "name_ar": "ساندويشات", "items": [
                {"name_en": "Fahita", "name_ar": "فاهيتا", "price": 5.56},
                {"name_en": "Chinese", "name_ar": "صيني", "price": 3.89},
                {"name_en": "Tawook", "name_ar": "طاووق", "price": 3.89},
                {"name_en": "Escalope", "name_ar": "اسكالوب", "price": 3.89},
                {"name_en": "Crispy", "name_ar": "كرسبي", "price": 4.44},
            ]},
            {"name_en": "Offers", "name_ar": "عروض", "items": [
                {"name_en": "Akleh box", "name_ar": "علبة أكلة", "price": 22.22},
                {"name_en": "Large crispy offer", "name_ar": "عرض كرسبي كبير", "price": 20.00},
            ]},
        ]
    },

    # 13. Pan Corner
    {
        "name_en": "Pan Corner",
        "name_ar": "بان كورنر",
        "category": "Pizza",
        "categories": [
            {"name_en": "Pizza", "name_ar": "بيتزا", "items": [
                {"name_en": "Supreme Pizza", "name_ar": "بيتزا سوبريم", "price": 11.00, "has_variants": True, "variants": [{"name": "M", "price": 11.00}, {"name": "L", "price": 13.00}, {"name": "XL", "price": 17.00}]},
                {"name_en": "Alfredo Chicken Pizza", "name_ar": "بيتزا الفريدو دجاج", "price": 11.00},
                {"name_en": "BBQ Chicken Pizza", "name_ar": "بيتزا باربكيو دجاج", "price": 11.00},
                {"name_en": "Pepperoni Pizza", "name_ar": "بيتزا بيبروني", "price": 9.00},
                {"name_en": "Margherita", "name_ar": "مارغريتا", "price": 9.00},
            ]},
            {"name_en": "Sweet Pizza", "name_ar": "بيتزا حلوة", "items": [
                {"name_en": "Pistachio Pizza", "name_ar": "بيتزا فستق", "price": 6.00},
                {"name_en": "Chocolate Pizza", "name_ar": "بيتزا شوكولا", "price": 6.00},
            ]},
            {"name_en": "Starters", "name_ar": "مقبلات", "items": [
                {"name_en": "Cheese Garlic Bread", "name_ar": "خبز ثوم بالجبنة", "price": 4.00},
                {"name_en": "Mozzarella Sticks", "name_ar": "موزاريلا ستيكس", "price": 4.00},
                {"name_en": "French Fries", "name_ar": "بطاطا مقلية", "price": 4.00},
            ]},
        ]
    },

    # 14. Burgero
    {
        "name_en": "Burgero",
        "name_ar": "برغرو",
        "category": "Burgers",
        "categories": [
            {"name_en": "Beef Burgers", "name_ar": "برغر لحم", "items": [
                {"name_en": "Classic Burger", "name_ar": "برغر كلاسيك", "price": 6.50},
                {"name_en": "The Lebanese", "name_ar": "اللبناني", "price": 6.50},
                {"name_en": "The Burgero", "name_ar": "البرغرو", "price": 8.50},
                {"name_en": "The Smash Burger", "name_ar": "سماش برغر", "price": 9.00},
                {"name_en": "Giant Burger", "name_ar": "برغر عملاق", "price": 10.00},
                {"name_en": "Truffle Burger", "name_ar": "ترافل برغر", "price": 10.00},
            ]},
            {"name_en": "Chicken Burgers", "name_ar": "برغر دجاج", "items": [
                {"name_en": "Classic Grilled Chicken", "name_ar": "دجاج مشوي كلاسيك", "price": 6.50},
                {"name_en": "Chicken Truffle", "name_ar": "ترافل دجاج", "price": 9.00},
                {"name_en": "Classic Fried Chicken", "name_ar": "دجاج مقلي كلاسيك", "price": 6.50},
            ]},
            {"name_en": "Fries Selection", "name_ar": "بطاطا", "items": [
                {"name_en": "French Fries", "name_ar": "بطاطا مقلية", "price": 4.50},
                {"name_en": "Curly Fries", "name_ar": "بطاطا كيرلي", "price": 5.00},
            ]},
        ]
    },

    # 15. Dr Meat
    {
        "name_en": "Dr Meat",
        "name_ar": "دكتور ميت",
        "category": "Grills",
        "categories": [
            {"name_en": "Burgers", "name_ar": "برغر", "items": [
                {"name_en": "Lebanese Burger", "name_ar": "برغر لبناني", "price": 6.00},
                {"name_en": "Classic Burger", "name_ar": "برغر كلاسيك", "price": 6.00},
                {"name_en": "Smash Burger", "name_ar": "سماش برغر", "price": 6.00},
                {"name_en": "Swiss Mushroom Burger", "name_ar": "سويس مشروم برغر", "price": 7.00},
                {"name_en": "Truffle Burger", "name_ar": "ترافل برغر", "price": 7.00},
                {"name_en": "WAGYU", "name_ar": "واغيو", "price": 18.00},
            ]},
            {"name_en": "Sandwiches", "name_ar": "ساندويشات", "items": [
                {"name_en": "Steak Sandwich", "name_ar": "ساندويش ستيك", "price": 7.00},
                {"name_en": "Philadelphia Steak", "name_ar": "فيلادلفيا ستيك", "price": 7.00},
                {"name_en": "Roast Sandwich", "name_ar": "ساندويش روست", "price": 7.00},
            ]},
            {"name_en": "Meat Plates", "name_ar": "صحون لحم", "items": [
                {"name_en": "Beef Sizzling", "name_ar": "لحم سيزلنغ", "price": 23.00},
                {"name_en": "Dr. Ribs", "name_ar": "ريبز", "price": 25.00},
                {"name_en": "Dr. Steak Fillet", "name_ar": "ستيك فيليه", "price": 19.00},
            ]},
        ]
    },

    # 16. Fayez Pizza
    {
        "name_en": "Fayez Pizza",
        "name_ar": "فايز بيتزا",
        "category": "Pizza",
        "categories": [
            {"name_en": "Specialty Pizza", "name_ar": "بيتزا خاصة", "items": [
                {"name_en": "Margherita", "name_ar": "مارغريتا", "price": 9.00, "has_variants": True, "variants": [{"name": "S", "price": 6.00}, {"name": "M", "price": 9.00}, {"name": "L", "price": 12.00}]},
                {"name_en": "Pepperoni", "name_ar": "بيبروني", "price": 13.00},
                {"name_en": "Lebanese", "name_ar": "لبنانية", "price": 11.00},
                {"name_en": "Meat Lover", "name_ar": "لحم لوفر", "price": 15.00},
            ]},
            {"name_en": "Chicken Pizza", "name_ar": "بيتزا دجاج", "items": [
                {"name_en": "Chicken Truffle", "name_ar": "دجاج ترافل", "price": 15.00},
                {"name_en": "Chicken BBQ", "name_ar": "دجاج باربكيو", "price": 13.00},
                {"name_en": "Chicken Fajita", "name_ar": "دجاج فاهيتا", "price": 13.00},
            ]},
            {"name_en": "Pasta", "name_ar": "باستا", "items": [
                {"name_en": "Alfredo", "name_ar": "الفريدو", "price": 7.00},
                {"name_en": "Creamy Pesto", "name_ar": "كريمي بيستو", "price": 7.00},
            ]},
        ]
    },

    # 17. Chahine Seafood
    {
        "name_en": "Chahine Seafood",
        "name_ar": "شاهين سي فود",
        "category": "Home Food",
        "categories": [
            {"name_en": "Sandwiches", "name_ar": "ساندويشات", "items": [
                {"name_en": "Calamari", "name_ar": "كلاماري", "price": 5.00},
                {"name_en": "Chahine's Shrimp", "name_ar": "قريدس شاهين", "price": 5.56},
                {"name_en": "Crab", "name_ar": "كراب", "price": 4.44},
                {"name_en": "Crispy Fillet", "name_ar": "فيليه كرسبي", "price": 4.44},
                {"name_en": "Crispy Shrimp", "name_ar": "قريدس كرسبي", "price": 5.00},
            ]},
            {"name_en": "Platters", "name_ar": "صحون", "items": [
                {"name_en": "Shrimps Platter", "name_ar": "صحن قريدس", "price": 9.44},
                {"name_en": "Calamari Platter", "name_ar": "صحن كلاماري", "price": 9.44},
                {"name_en": "Grilled Shrimps", "name_ar": "قريدس مشوي", "price": 11.11},
            ]},
            {"name_en": "Family Meals", "name_ar": "وجبات عائلية", "items": [
                {"name_en": "Crispy Fillet Family", "name_ar": "فيليه كرسبي عائلي", "price": 24.44},
                {"name_en": "Shrimps Family", "name_ar": "قريدس عائلي", "price": 24.44},
            ]},
        ]
    },

    # 18. Twist
    {
        "name_en": "Twist",
        "name_ar": "تويست",
        "category": "Beverages",
        "categories": [
            {"name_en": "Hot Coffee", "name_ar": "قهوة ساخنة", "items": [
                {"name_en": "Espresso Single", "name_ar": "اسبريسو سنغل", "price": 1.67},
                {"name_en": "Espresso Double", "name_ar": "اسبريسو دوبل", "price": 2.22},
                {"name_en": "Cappuccino", "name_ar": "كابتشينو", "price": 3.33},
                {"name_en": "Americano", "name_ar": "امريكانو", "price": 3.00},
                {"name_en": "Mocha Latte", "name_ar": "موكا لاتيه", "price": 4.44},
                {"name_en": "Matcha Latte", "name_ar": "ماتشا لاتيه", "price": 4.44},
            ]},
            {"name_en": "Cold Drinks", "name_ar": "مشروبات باردة", "items": [
                {"name_en": "Iced Americano", "name_ar": "ايس امريكانو", "price": 3.44},
                {"name_en": "Iced Latte", "name_ar": "ايس لاتيه", "price": 4.00},
            ]},
        ]
    },

    # 19. Space Food
    {
        "name_en": "Space Food",
        "name_ar": "سبيس فود",
        "category": "Snacks",
        "categories": [
            {"name_en": "Salad", "name_ar": "سلطات", "items": [
                {"name_en": "Caesar Salad", "name_ar": "سلطة سيزر", "price": 6.67},
                {"name_en": "Tuna Salad", "name_ar": "سلطة تونا", "price": 7.78},
                {"name_en": "Crab Salad", "name_ar": "سلطة كراب", "price": 7.78},
            ]},
            {"name_en": "Appetizers", "name_ar": "مقبلات", "items": [
                {"name_en": "French Fries Medium", "name_ar": "بطاطا وسط", "price": 3.50},
                {"name_en": "French Fries Large", "name_ar": "بطاطا كبير", "price": 5.00},
                {"name_en": "Mozzarella Sticks", "name_ar": "موزاريلا ستيكس", "price": 5.00},
            ]},
            {"name_en": "Pasta", "name_ar": "باستا", "items": [
                {"name_en": "Curry Chicken", "name_ar": "كاري دجاج", "price": 8.00},
                {"name_en": "Fajita Chicken", "name_ar": "فاهيتا دجاج", "price": 9.50},
                {"name_en": "Pesto Chicken", "name_ar": "بيستو دجاج", "price": 9.00},
                {"name_en": "Fettuccine Chicken", "name_ar": "فيتوتشيني دجاج", "price": 9.00},
            ]},
        ]
    },

    # 20. Qarmash
    {
        "name_en": "Qarmash",
        "name_ar": "قرمش",
        "category": "Snacks",
        "categories": [
            {"name_en": "Chicken Broasted", "name_ar": "دجاج بروستد", "items": [
                {"name_en": "Broast 3 Pcs", "name_ar": "بروستد 3 قطع", "price": 8.00},
                {"name_en": "Broast 4 Pcs", "name_ar": "بروستد 4 قطع", "price": 9.00},
                {"name_en": "Broast 8 Pcs", "name_ar": "بروستد 8 قطع", "price": 16.00},
                {"name_en": "Broast 12 Pcs Family", "name_ar": "بروستد 12 قطعة عائلي", "price": 24.00},
            ]},
            {"name_en": "Sandwiches", "name_ar": "سندويشات", "items": [
                {"name_en": "Crispy Sandwich", "name_ar": "ساندويش كرسبي", "price": 4.50},
                {"name_en": "Tawook Sandwich", "name_ar": "ساندويش طاووق", "price": 4.50},
                {"name_en": "Zinger Burger", "name_ar": "زينجر برغر", "price": 4.50},
            ]},
        ]
    },

    # 21. Baba Ghanouj
    {
        "name_en": "Baba Ghanouj",
        "name_ar": "بابا غنوج",
        "category": "Home Food",
        "phone": "03 40 9998",
        "categories": [
            {"name_en": "Breakfast", "name_ar": "فطور", "items": [
                {"name_en": "Foul", "name_ar": "فول", "price": 4.50},
                {"name_en": "Hummus", "name_ar": "حمص", "price": 4.50},
                {"name_en": "Msabbaha", "name_ar": "مسبحة", "price": 4.50},
                {"name_en": "Hummus Fatteh", "name_ar": "فتة حمص", "price": 5.50},
                {"name_en": "Meat Fatteh", "name_ar": "فتة لحمة", "price": 7.00},
            ]},
            {"name_en": "Shawarma", "name_ar": "شاورما", "items": [
                {"name_en": "Chicken Shawarma Sandwich", "name_ar": "سندويش شاورما دجاج", "price": 3.50},
                {"name_en": "Meat Shawarma Sandwich", "name_ar": "سندويش شاورما لحم", "price": 4.50},
                {"name_en": "Chicken Shawarma Plate", "name_ar": "صحن شاورما دجاج", "price": 7.50},
            ]},
            {"name_en": "Burgers", "name_ar": "برغر", "items": [
                {"name_en": "Lebanese Burger", "name_ar": "برغر لبناني", "price": 6.00},
                {"name_en": "Classic Burger", "name_ar": "برغر كلاسيك", "price": 6.00},
            ]},
        ]
    },

    # 22. Mn2osha & more
    {
        "name_en": "Mn2osha & more",
        "name_ar": "منقوشة و اكتر",
        "category": "Home Food",
        "categories": [
            {"name_en": "Breakfast", "name_ar": "فطور", "items": [
                {"name_en": "Zaatar", "name_ar": "زعتر", "price": 0.67},
                {"name_en": "Labneh", "name_ar": "لبنة", "price": 1.78},
                {"name_en": "Keshek", "name_ar": "كشك", "price": 1.78},
                {"name_en": "Akkawi Cheese", "name_ar": "جبنة عكاوي", "price": 2.00},
                {"name_en": "Halloumi & Kashkaval", "name_ar": "حلوم وقشقوان", "price": 2.50},
                {"name_en": "Turkey & Cheese", "name_ar": "حبش وجبنة", "price": 3.61},
            ]},
            {"name_en": "Chicken", "name_ar": "دجاج", "items": [
                {"name_en": "Boneless", "name_ar": "بونلس", "price": 3.89},
                {"name_en": "Taouk", "name_ar": "طاووق", "price": 3.89},
                {"name_en": "Fajita & Cheese", "name_ar": "فاهيتا وجبنة", "price": 3.89},
            ]},
            {"name_en": "Pizza", "name_ar": "بيتزا", "items": [
                {"name_en": "Vegetarian", "name_ar": "نباتية", "price": 5.00, "has_variants": True, "variants": [{"name": "S", "price": 5.00}, {"name": "M", "price": 7.00}, {"name": "L", "price": 9.00}]},
                {"name_en": "Pepperoni", "name_ar": "بيبروني", "price": 5.00},
                {"name_en": "BBQ", "name_ar": "باربكيو", "price": 6.00},
            ]},
        ]
    },

    # 23. 7amoudi menu
    {
        "name_en": "7amoudi menu",
        "name_ar": "منيو حمودي",
        "category": "Home Food",
        "categories": [
            {"name_en": "Arabic Sandwich", "name_ar": "ساندويش عربي", "items": [
                {"name_en": "Potato Sandwich", "name_ar": "ساندويش بطاطا", "price": 1.67},
                {"name_en": "Taouk", "name_ar": "طاووق", "price": 1.89},
                {"name_en": "Escalope", "name_ar": "اسكلوب", "price": 1.89},
                {"name_en": "Crispy", "name_ar": "كرسبي", "price": 1.89},
                {"name_en": "Sujuk", "name_ar": "سجق", "price": 2.78},
                {"name_en": "Makanek", "name_ar": "مقانق", "price": 2.78},
            ]},
            {"name_en": "Burger", "name_ar": "برغر", "items": [
                {"name_en": "Burger", "name_ar": "برغر", "price": 2.22},
                {"name_en": "Cheese Burger", "name_ar": "تشيز برغر", "price": 2.78},
                {"name_en": "Zinger", "name_ar": "زنجر", "price": 3.33},
                {"name_en": "American Burger", "name_ar": "اميركن برغر", "price": 3.33},
            ]},
            {"name_en": "French Sandwich", "name_ar": "ساندويش فرنجي", "items": [
                {"name_en": "Fajita", "name_ar": "فاهيتا", "price": 3.33},
                {"name_en": "Francisco", "name_ar": "فرانسيسكو", "price": 3.33},
                {"name_en": "Twister", "name_ar": "توستر", "price": 3.33},
            ]},
        ]
    },

    # 24. Drop
    {
        "name_en": "Drop",
        "name_ar": "دروب",
        "category": "Beverages",
        "categories": [
            {"name_en": "Coffee", "name_ar": "قهوة", "items": [
                {"name_en": "Espresso", "name_ar": "اسبريسو", "price": 2.22},
                {"name_en": "Americano", "name_ar": "امريكانو", "price": 3.33},
                {"name_en": "Cappuccino", "name_ar": "كابتشينو", "price": 3.89},
                {"name_en": "Flat White", "name_ar": "فلات وايت", "price": 4.44},
            ]},
            {"name_en": "Latte", "name_ar": "لاتيه", "items": [
                {"name_en": "TRIO (Signature)", "name_ar": "تريو", "price": 4.44},
                {"name_en": "Mocha", "name_ar": "موكا", "price": 4.44},
                {"name_en": "Hot Chocolate", "name_ar": "هوت شوكولا", "price": 4.44},
                {"name_en": "Matcha", "name_ar": "ماتشا", "price": 4.44},
            ]},
            {"name_en": "Frappés", "name_ar": "فرابيه", "items": [
                {"name_en": "Coffee", "name_ar": "قهوة", "price": 4.44},
                {"name_en": "Lotus", "name_ar": "لوتس", "price": 4.44},
                {"name_en": "Oreo", "name_ar": "اوريو", "price": 4.44},
            ]},
            {"name_en": "Dessert", "name_ar": "حلويات", "items": [
                {"name_en": "Lotus Cake", "name_ar": "كيك لوتس", "price": 4.44},
                {"name_en": "NewYork Cheese Cake", "name_ar": "تشيز كيك", "price": 4.44},
                {"name_en": "Brownies", "name_ar": "براونيز", "price": 3.33},
            ]},
        ]
    },

    # 25. Adi's
    {
        "name_en": "Adi's",
        "name_ar": "أديز",
        "category": "Burgers",
        "categories": [
            {"name_en": "Chicken Burger", "name_ar": "برغر دجاج", "items": [
                {"name_en": "Zinger", "name_ar": "زينجر", "price": 6.66},
                {"name_en": "Spicy Zinger", "name_ar": "زينجر حار", "price": 6.66},
                {"name_en": "Grilled Chicken", "name_ar": "دجاج مشوي", "price": 5.00},
            ]},
            {"name_en": "Beef Burger", "name_ar": "برغر لحم", "items": [
                {"name_en": "American", "name_ar": "أمريكان", "price": 5.56},
                {"name_en": "Lebanese", "name_ar": "لبناني", "price": 5.56},
                {"name_en": "Swiss Mushroom", "name_ar": "سويس مشروم", "price": 7.78},
            ]},
            {"name_en": "Sandwiches", "name_ar": "ساندويشات", "items": [
                {"name_en": "Fajita", "name_ar": "فاهيتا", "price": 5.56},
                {"name_en": "Tawook", "name_ar": "طاووق", "price": 4.45},
                {"name_en": "Crispy", "name_ar": "كرسبي", "price": 5.56},
            ]},
            {"name_en": "Pizza", "name_ar": "بيتزا", "items": [
                {"name_en": "Margherita", "name_ar": "مارغريتا", "price": 6.67},
                {"name_en": "Pepperoni", "name_ar": "بيبروني", "price": 8.89},
            ]},
            {"name_en": "Sides", "name_ar": "جوانب", "items": [
                {"name_en": "Fries", "name_ar": "بطاطا", "price": 3.34},
                {"name_en": "Cheesy Fries", "name_ar": "بطاطا بالجبنة", "price": 4.44},
                {"name_en": "Mozzarella Sticks", "name_ar": "موزاريلا ستيكس", "price": 4.44},
            ]},
        ]
    },

    # 26. Abu Arab - Malik al Kaak al Masri
    {
        "name_en": "Abu Arab - Malik al Kaak al Masri",
        "name_ar": "أبو عرب - ملك الكعك المصري",
        "category": "Sandwiches",
        "categories": [
            {"name_en": "Regular Kaak", "name_ar": "كعك عادي", "items": [
                {"name_en": "Plain", "name_ar": "سادة", "price": 0.89},
                {"name_en": "Zaatar with Oil", "name_ar": "زعتر مع زيت", "price": 2.22},
                {"name_en": "Bacon", "name_ar": "بيكون", "price": 2.56},
                {"name_en": "Bulgarian Cheese with Chili", "name_ar": "بلغاري مع حر", "price": 2.78},
                {"name_en": "Grilled Potato", "name_ar": "بطاطا مشوية", "price": 2.22},
                {"name_en": "Labneh with Olives", "name_ar": "لبنة زيتون", "price": 2.44},
                {"name_en": "Feta Cheese with Chili", "name_ar": "فيتا مع حر", "price": 2.44},
                {"name_en": "Chocolate", "name_ar": "شوكولا", "price": 2.56},
                {"name_en": "Akkawi", "name_ar": "عكاوي", "price": 2.78},
                {"name_en": "Halloumi", "name_ar": "حلوم", "price": 2.78},
                {"name_en": "Kashkaval", "name_ar": "قشقوان", "price": 3.33},
                {"name_en": "Halawa Kaak", "name_ar": "كعكة حلاوة", "price": 2.56},
            ]},
            {"name_en": "Mixed Kaak", "name_ar": "كعك مشكل", "items": [
                {"name_en": "Smoked Turkey + Kashkaval", "name_ar": "حبش مدخن + قشقوان", "price": 5.67},
                {"name_en": "Smoked Turkey + Akkawi", "name_ar": "حبش مدخن + عكاوي", "price": 5.11},
                {"name_en": "Smoked Turkey + Mozzarella", "name_ar": "حبش مدخن + موزريلا", "price": 5.00},
                {"name_en": "Pepperoni + Kashkaval", "name_ar": "بيبروني + قشقوان", "price": 5.67},
                {"name_en": "Pepperoni + Mozzarella", "name_ar": "بيبروني + موزريلا", "price": 5.00},
                {"name_en": "Kashkaval + Bacon", "name_ar": "قشقوان + بيكون", "price": 4.44},
                {"name_en": "Halloumi + Bacon", "name_ar": "حلوم + بيكون", "price": 3.67},
                {"name_en": "4 Cheese", "name_ar": "4 Cheese", "price": 6.89},
                {"name_en": "Sojouk + Kashkaval", "name_ar": "سجق + قشقوان", "price": 5.56},
            ]},
            {"name_en": "Cold / Drinks", "name_ar": "بارد", "items": [
                {"name_en": "Small Water", "name_ar": "مياه صغيرة", "price": 0.33},
                {"name_en": "Large Water", "name_ar": "مياه كبيرة", "price": 0.56},
                {"name_en": "Ayran Yogurt", "name_ar": "لبن عيران", "price": 0.83},
                {"name_en": "Juice", "name_ar": "عصير", "price": 0.83},
                {"name_en": "Pepsi", "name_ar": "بيبسي", "price": 1.11},
            ]},
        ]
    },

    # 27. Gharmti & Kiblawi Sweets
    {
        "name_en": "Gharmti & Kiblawi Sweets",
        "name_ar": "غرمتي وقبلاوي",
        "category": "Sweets",
        "categories": [
            {"name_en": "Chokunafa", "name_ar": "شوكونافة", "items": [
                {"name_en": "Lotus Chokunafa", "name_ar": "شوكونافة لوتس", "price": 5.00},
                {"name_en": "Pistachio Chokunafa", "name_ar": "شوكونافة فستق", "price": 5.00},
                {"name_en": "Hazelnut Chokunafa", "name_ar": "شوكونافة بندق", "price": 5.00},
                {"name_en": "White Pistachio Chokunafa", "name_ar": "شوكونافة فستق أبيض", "price": 5.00},
            ]},
            {"name_en": "Knafeh Plate", "name_ar": "صحن كنافة", "items": [
                {"name_en": "Knafeh Plate Regular", "name_ar": "صحن كنافة عادي", "price": 3.33},
                {"name_en": "Knafeh Plate Extra", "name_ar": "صحن كنافة اكسترا", "price": 4.44},
                {"name_en": "Knafeh Chocolate Plate", "name_ar": "صحن كنافة شوكولا", "price": 4.44},
                {"name_en": "Knafeh Lotus Plate", "name_ar": "صحن كنافة لوتس", "price": 4.44},
                {"name_en": "Nabulsie Plate", "name_ar": "صحن نابلسية", "price": 3.56},
            ]},
            {"name_en": "Kaake Knafeh & Nabulsie", "name_ar": "كعكة كنافة ونابلسية", "items": [
                {"name_en": "Kaake Knafeh Regular", "name_ar": "كعكة كنافة عادي", "price": 2.22},
                {"name_en": "Kaake Knafeh Extra", "name_ar": "كعكة كنافة اكسترا", "price": 3.33},
                {"name_en": "Kaake Knafeh Chocolate", "name_ar": "كعكة كنافة شوكولا", "price": 3.33},
                {"name_en": "Kaake Nabulsie", "name_ar": "كعكة نابلسية", "price": 2.44},
            ]},
            {"name_en": "Croissant", "name_ar": "كرواسون", "items": [
                {"name_en": "Chocolate Croissant", "name_ar": "كرواسون شوكولا", "price": 1.11},
                {"name_en": "Cheese Croissant", "name_ar": "كرواسون جبنة", "price": 1.11},
                {"name_en": "Croissant Zaatar", "name_ar": "كرواسون زعتر", "price": 1.11},
                {"name_en": "Croissant Knafeh", "name_ar": "كرواسون كنافة", "price": 3.33},
            ]},
            {"name_en": "Drinks", "name_ar": "مشروبات", "items": [
                {"name_en": "Avocado", "name_ar": "أفوكادو", "price": 2.22},
                {"name_en": "Avocado + Cocktail", "name_ar": "أفوكادو + كوكتيل", "price": 1.67},
                {"name_en": "Cocktail", "name_ar": "كوكتيل", "price": 1.44},
                {"name_en": "Mango", "name_ar": "مانجو", "price": 1.67},
                {"name_en": "Strawberry", "name_ar": "فريز", "price": 1.67},
            ]},
        ]
    },

    # 28. Al Akkad
    {
        "name_en": "Al Akkad",
        "name_ar": "العقاد",
        "category": "Beverages",
        "categories": [
            {"name_en": "Akkad Specials", "name_ar": "خاص العقاد", "items": [
                {"name_en": "Shaqaf Cocktail", "name_ar": "كوكتيل شقف", "price": 3.75, "has_variants": True, "variants": [{"name": "Small", "price": 3.75}, {"name": "Medium", "price": 6.00}, {"name": "Large", "price": 7.50}]},
                {"name_en": "Tropicana Cup", "name_ar": "كوب تروبيكانا", "price": 4.25, "has_variants": True, "variants": [{"name": "Small", "price": 4.25}, {"name": "Medium", "price": 6.80}, {"name": "Large", "price": 8.50}]},
                {"name_en": "Akkad Cup", "name_ar": "كوب العقاد", "price": 2.75, "has_variants": True, "variants": [{"name": "Small", "price": 2.75}, {"name": "Medium", "price": 4.40}, {"name": "Large", "price": 5.50}]},
                {"name_en": "HULK Cup", "name_ar": "كوب HULK", "price": 4.25, "has_variants": True, "variants": [{"name": "Small", "price": 4.25}, {"name": "Medium", "price": 6.80}, {"name": "Large", "price": 8.50}]},
                {"name_en": "Avocado Cup", "name_ar": "كوب أفوكا", "price": 4.25, "has_variants": True, "variants": [{"name": "Small", "price": 4.25}, {"name": "Medium", "price": 6.80}, {"name": "Large", "price": 8.50}]},
            ]},
            {"name_en": "Fresh Juices", "name_ar": "عصائر طازجة", "items": [
                {"name_en": "Strawberry Juice", "name_ar": "عصير فريز", "price": 1.00, "has_variants": True, "variants": [{"name": "Small", "price": 1.00}, {"name": "Medium", "price": 1.60}, {"name": "Large", "price": 2.00}]},
                {"name_en": "Mango Juice", "name_ar": "عصير مانجا", "price": 1.25, "has_variants": True, "variants": [{"name": "Small", "price": 1.25}, {"name": "Medium", "price": 2.00}, {"name": "Large", "price": 2.50}]},
                {"name_en": "Lemonade", "name_ar": "ليموناضة", "price": 1.00, "has_variants": True, "variants": [{"name": "Small", "price": 1.00}, {"name": "Medium", "price": 1.60}, {"name": "Large", "price": 2.00}]},
                {"name_en": "Pomegranate Juice", "name_ar": "عصير رمان", "price": 1.75, "has_variants": True, "variants": [{"name": "Small", "price": 1.75}, {"name": "Medium", "price": 2.80}, {"name": "Large", "price": 3.50}]},
                {"name_en": "Cocktail Juice", "name_ar": "عصير كوكتيل", "price": 1.00, "has_variants": True, "variants": [{"name": "Small", "price": 1.00}, {"name": "Medium", "price": 1.60}, {"name": "Large", "price": 2.00}]},
            ]},
            {"name_en": "Cakes", "name_ar": "كيك", "items": [
                {"name_en": "Blueberry Cheesecake", "name_ar": "تشيز كيك بلوبيري", "price": 4.00},
                {"name_en": "Lotus Cheesecake", "name_ar": "تشيز كيك لوتس", "price": 4.00},
                {"name_en": "Oreo Cheesecake", "name_ar": "تشيز كيك اوريو", "price": 4.00},
                {"name_en": "Red Velvet", "name_ar": "رد فلفت", "price": 4.00},
                {"name_en": "Chocolate Cake", "name_ar": "شوكاتو كيك", "price": 5.50},
            ]},
        ]
    },

    # 29. Atyab Basterma
    {
        "name_en": "Atyab Basterma",
        "name_ar": "اطيب باسترما",
        "category": "Sandwiches",
        "categories": [
            {"name_en": "Cold Cuts", "name_ar": "لحوم باردة", "items": [
                {"name_en": "Basterma", "name_ar": "باسترما", "price": 30.00},
                {"name_en": "Roast Beef", "name_ar": "روست بيف", "price": 27.00},
                {"name_en": "Sojok", "name_ar": "سجق", "price": 15.00},
                {"name_en": "Makanek", "name_ar": "مقانق", "price": 15.00},
            ]},
            {"name_en": "Appetizers", "name_ar": "مقبلات", "items": [
                {"name_en": "Fries Box", "name_ar": "علبة بطاطا", "price": 4.00},
                {"name_en": "Basterma Sticks", "name_ar": "ستيك باسترما", "price": 5.00},
                {"name_en": "Mozzarella Sticks", "name_ar": "موزاريلا ستيكس", "price": 5.00},
                {"name_en": "Curly Fries", "name_ar": "بطاطا كيرلي", "price": 5.00},
            ]},
            {"name_en": "Sandwiches", "name_ar": "ساندويشات", "items": [
                {"name_en": "Basterma Sandwich", "name_ar": "ساندويش باسترما", "price": 5.50},
                {"name_en": "Rosto Sandwich", "name_ar": "ساندويش روستو", "price": 5.50},
                {"name_en": "Makanek Sandwich", "name_ar": "ساندويش مقانق", "price": 4.00},
                {"name_en": "Sojok Sandwich", "name_ar": "ساندويش سجق", "price": 4.00},
                {"name_en": "Turkey & Cheese", "name_ar": "حبش وجبنة", "price": 5.00},
            ]},
            {"name_en": "Subs", "name_ar": "صب", "items": [
                {"name_en": "Fajita Sub", "name_ar": "صب فاهيتا", "price": 6.00},
                {"name_en": "Philadelphia Sub", "name_ar": "صب فيلادلفيا", "price": 7.00},
                {"name_en": "Chicken Sub", "name_ar": "صب دجاج", "price": 5.50},
                {"name_en": "Steak Sandwich", "name_ar": "ساندويش ستيك", "price": 7.00},
                {"name_en": "Tawook Sub", "name_ar": "صب طاووق", "price": 4.50},
            ]},
            {"name_en": "Burgers", "name_ar": "برغر", "items": [
                {"name_en": "Lebanese Burger", "name_ar": "برغر لبناني", "price": 5.00},
                {"name_en": "Classic Burger", "name_ar": "برغر كلاسيك", "price": 6.00},
                {"name_en": "Zinger Burger", "name_ar": "زينجر برغر", "price": 6.50},
                {"name_en": "Smashed Burger", "name_ar": "سماش برغر", "price": 7.00},
                {"name_en": "Mushroom Burger", "name_ar": "مشروم برغر", "price": 7.00},
            ]},
        ]
    },

    # 30. Al Sayed
    {
        "name_en": "Al Sayed",
        "name_ar": "السيد",
        "category": "Shawarma",
        "categories": [
            {"name_en": "Shawarma", "name_ar": "شاورما", "items": [
                {"name_en": "Chicken Shawarma Large", "name_ar": "شاورما دجاج كبير", "price": 6.00},
                {"name_en": "Chicken Shawarma Medium", "name_ar": "شاورما دجاج وسط", "price": 5.00},
                {"name_en": "Chicken Shawarma Markouk", "name_ar": "شاورما دجاج مرقوق", "price": 6.00},
                {"name_en": "Meat Shawarma Large", "name_ar": "شاورما لحمة كبير", "price": 6.00},
                {"name_en": "Meat Shawarma Medium", "name_ar": "شاورما لحمة وسط", "price": 5.00},
                {"name_en": "Meat Shawarma Markouk", "name_ar": "شاورما لحمة مرقوق", "price": 6.00},
                {"name_en": "Extra Shawarma", "name_ar": "شاورما اكسترا", "price": 7.00},
                {"name_en": "Sayed Shawarma", "name_ar": "سيد الشاورما", "price": 10.00},
            ]},
            {"name_en": "Shawarma Meals", "name_ar": "وجبات شاورما", "items": [
                {"name_en": "Chicken Markouk Meal", "name_ar": "وجبة مرقوق دجاج", "price": 14.00},
                {"name_en": "Meat Markouk Meal", "name_ar": "وجبة مرقوق لحمة", "price": 14.00},
                {"name_en": "Mixed Markouk Meal", "name_ar": "وجبة مرقوق مشكل", "price": 14.00},
                {"name_en": "Sayed Shawarma Meal", "name_ar": "وجبة سيد الشاورما", "price": 22.00},
                {"name_en": "Chicken Shawarma 1KG", "name_ar": "كيلو شاورما دجاج", "price": 35.00},
                {"name_en": "Meat Shawarma 1KG", "name_ar": "كيلو شاورما لحمة", "price": 35.00},
            ]},
            {"name_en": "Burgers", "name_ar": "برغر", "items": [
                {"name_en": "Chicken Burger", "name_ar": "برغر دجاج", "price": 5.00},
                {"name_en": "Meat Burger", "name_ar": "برغر لحمه", "price": 5.00},
                {"name_en": "Chicken Burger with Cheese", "name_ar": "برغر دجاج مع جبنة", "price": 6.00},
                {"name_en": "Meat Burger with Cheese", "name_ar": "برغر لحمه مع جبنة", "price": 6.00},
            ]},
            {"name_en": "Tawook", "name_ar": "طاووق", "items": [
                {"name_en": "Tawook Large", "name_ar": "طاووق كبير", "price": 6.00},
                {"name_en": "Tawook Medium", "name_ar": "طاووق وسط", "price": 5.00},
                {"name_en": "Tawook Markouk", "name_ar": "شيش طاووق مرقوق", "price": 6.00},
                {"name_en": "Tawook Meal", "name_ar": "وجبة طاووق", "price": 14.00},
            ]},
            {"name_en": "Fries", "name_ar": "بطاطا", "items": [
                {"name_en": "Fries Plate Medium", "name_ar": "صحن بطاطا وسط", "price": 4.00},
                {"name_en": "Fries Plate Large", "name_ar": "صحن بطاطا كبير", "price": 5.00},
                {"name_en": "Fries Sandwich", "name_ar": "سندويش بطاطا", "price": 2.50},
            ]},
        ]
    },

    # 31. Stories
    {
        "name_en": "Stories",
        "name_ar": "ستوريز",
        "category": "Beverages",
        "categories": [
            {"name_en": "Hot Coffee", "name_ar": "قهوة ساخنة", "items": [
                {"name_en": "Espresso", "name_ar": "اسبريسو", "price": 3.00},
                {"name_en": "Americano", "name_ar": "امريكانو", "price": 3.33},
                {"name_en": "Latte", "name_ar": "لاتيه", "price": 3.67},
                {"name_en": "Cappuccino", "name_ar": "كابتشينو", "price": 3.67},
                {"name_en": "Flat White", "name_ar": "فلات وايت", "price": 3.67},
                {"name_en": "Mocha", "name_ar": "موكا", "price": 4.22},
                {"name_en": "Caramel Macchiato", "name_ar": "كراميل ماكياتو", "price": 4.22},
            ]},
            {"name_en": "Non-Coffee", "name_ar": "بدون قهوة", "items": [
                {"name_en": "Steamed Milk", "name_ar": "حليب ساخن", "price": 2.44},
                {"name_en": "Matcha Latte", "name_ar": "ماتشا لاتيه", "price": 3.67},
                {"name_en": "Hot Chocolate", "name_ar": "هوت شوكولا", "price": 3.89},
            ]},
            {"name_en": "Iced Coffee", "name_ar": "قهوة باردة", "items": [
                {"name_en": "Iced Latte", "name_ar": "ايس لاتيه", "price": 3.67},
                {"name_en": "Iced Americano", "name_ar": "ايس امريكانو", "price": 3.78},
                {"name_en": "Iced Mocha", "name_ar": "ايس موكا", "price": 4.22},
                {"name_en": "Iced Matcha", "name_ar": "ايس ماتشا", "price": 3.67},
            ]},
            {"name_en": "Frappuccino", "name_ar": "فرابتشينو", "items": [
                {"name_en": "Espresso Frap", "name_ar": "اسبريسو فراب", "price": 3.33},
                {"name_en": "Coffee Frap", "name_ar": "كوفي فراب", "price": 3.33},
                {"name_en": "Caramel Frap", "name_ar": "كراميل فراب", "price": 4.22},
                {"name_en": "Mocha Frap", "name_ar": "موكا فراب", "price": 4.22},
                {"name_en": "Matcha Cream Frap", "name_ar": "ماتشا كريم فراب", "price": 4.22},
            ]},
            {"name_en": "Sandwiches & Salads", "name_ar": "ساندويشات وسلطات", "items": [
                {"name_en": "Labneh Sandwich", "name_ar": "ساندويش لبنة", "price": 4.44},
                {"name_en": "Halloumi Pesto", "name_ar": "حلوم بيستو", "price": 6.00},
                {"name_en": "Turkey & Cheese", "name_ar": "حبش وجبنة", "price": 6.56},
                {"name_en": "Greek Salad", "name_ar": "سلطة يونانية", "price": 7.78},
            ]},
            {"name_en": "Bakery", "name_ar": "مخبوزات", "items": [
                {"name_en": "Thyme Croissant", "name_ar": "كرواسون زعتر", "price": 3.33},
                {"name_en": "Cheese Croissant", "name_ar": "كرواسون جبنة", "price": 3.89},
                {"name_en": "Chocolate Croissant", "name_ar": "كرواسون شوكولا", "price": 3.89},
                {"name_en": "Cinnamon Rolls", "name_ar": "سينامون رول", "price": 5.56},
            ]},
        ]
    },

    # 32. Twister
    {
        "name_en": "Twister",
        "name_ar": "تويستر",
        "category": "Snacks",
        "categories": [
            {"name_en": "Starters", "name_ar": "مقبلات", "items": [
                {"name_en": "Twister Fries", "name_ar": "تويستر فرايز", "price": 5.00},
                {"name_en": "French Fries", "name_ar": "بطاطا مقلية", "price": 4.00},
                {"name_en": "Family Fries", "name_ar": "بطاطا عائلي", "price": 7.00},
                {"name_en": "Wedges Potato", "name_ar": "بطاطا ويدجز", "price": 5.00},
                {"name_en": "Mozzarella Sticks", "name_ar": "موزاريلا ستيك", "price": 6.00},
                {"name_en": "Cheese Bombs", "name_ar": "كرات الجبن", "price": 6.00},
                {"name_en": "Cheese Fries", "name_ar": "تشيزي فرايز", "price": 6.00},
                {"name_en": "Loaded Fries", "name_ar": "لودد فرايز", "price": 7.00},
                {"name_en": "Chicken Loaded Fries", "name_ar": "لودد فرايز بالدجاج", "price": 9.00},
            ]},
            {"name_en": "Salads", "name_ar": "سلطة", "items": [
                {"name_en": "Twister Signature Salad", "name_ar": "سلطة السيزر بالدجاج والأناناس", "price": 10.00},
                {"name_en": "Caesar Salad", "name_ar": "سلطة السيزر", "price": 6.00},
                {"name_en": "Twister Caesar Salad", "name_ar": "سلطة السيزر بالدجاج", "price": 9.00},
            ]},
            {"name_en": "Mac & Cheese", "name_ar": "ماك آند تشيز", "items": [
                {"name_en": "Mac & Cheese", "name_ar": "ماك آند تشيز", "price": 7.00},
                {"name_en": "Mac & Cheese With Chicken", "name_ar": "ماك آند تشيز مع دجاج", "price": 9.00},
                {"name_en": "Mac & Cheese with Spicy Chicken", "name_ar": "ماك آند تشيز مع دجاج حار", "price": 9.00},
            ]},
            {"name_en": "Twister Wraps", "name_ar": "تويستر", "items": [
                {"name_en": "Original Twister Wrap", "name_ar": "تويستر اوريجينال", "price": 5.50},
                {"name_en": "Spicy Twister Wrap", "name_ar": "تويستر حار", "price": 5.50},
                {"name_en": "Classic Twister Wrap", "name_ar": "تويستر كلاسيك", "price": 6.50},
                {"name_en": "BBQ Twister Wrap", "name_ar": "تويستر باربيكيو", "price": 6.50},
                {"name_en": "Buffalo Twister Wrap", "name_ar": "تويستر بوفالو حار", "price": 6.50},
                {"name_en": "Cheesy Twister Wrap", "name_ar": "تويستر بالجبنة", "price": 7.00},
                {"name_en": "Signature Twister Wrap", "name_ar": "تويستر بالأناناس", "price": 7.50},
            ]},
            {"name_en": "Zinger", "name_ar": "زنجر", "items": [
                {"name_en": "Zinger Burger", "name_ar": "زنجر برغر", "price": 5.00},
                {"name_en": "Classic Zinger", "name_ar": "زنجر كلاسيك", "price": 6.00},
                {"name_en": "BBQ Zinger", "name_ar": "زنجر باربيكيو", "price": 6.00},
                {"name_en": "Buffalo Zinger", "name_ar": "زنجر بوفالو", "price": 6.00},
                {"name_en": "Cheezy Zinger", "name_ar": "زنجر بالجبنة", "price": 7.00},
                {"name_en": "Signature Zinger", "name_ar": "زنجر بالأناناس", "price": 7.00},
            ]},
            {"name_en": "Burgers", "name_ar": "برغر", "items": [
                {"name_en": "Original Burger", "name_ar": "أوريجينال برغر", "price": 5.00},
                {"name_en": "Classic Burger", "name_ar": "كلاسيك برغر", "price": 5.00},
                {"name_en": "BBQ Burger", "name_ar": "باربيكيو برغر", "price": 5.00},
                {"name_en": "Buffalo Burger", "name_ar": "بوفالو برغر", "price": 5.00},
                {"name_en": "Cheesy Burger", "name_ar": "تشيزي برغر", "price": 6.00},
                {"name_en": "Signature Burger", "name_ar": "برغر بالأناناس", "price": 6.00},
            ]},
            {"name_en": "Crispy", "name_ar": "كرسبي", "items": [
                {"name_en": "Crispy Strips 3 pcs", "name_ar": "كرسبي 3 قطع", "price": 4.50},
                {"name_en": "BBQ Strips 3 pcs", "name_ar": "كرسبي بالباربيكيو 3 قطع", "price": 6.00},
                {"name_en": "Buffalo Strips 3 pcs", "name_ar": "كرسبي بالبوفالو 3 قطع", "price": 6.00},
                {"name_en": "Crispy Combo 3 pcs", "name_ar": "كرسبي كومبو 3 قطع", "price": 8.00},
                {"name_en": "Crispy Meal 5 pcs", "name_ar": "وجبة كرسبي 5 قطع", "price": 11.00},
                {"name_en": "Duo Meal 10 pcs", "name_ar": "وجبة كرسبي 10 قطع", "price": 20.00},
                {"name_en": "Family Crispy Meal 20 pcs", "name_ar": "وجبة عائلية كرسبي 20 قطعة", "price": 35.00},
            ]},
        ]
    },
]


async def get_or_create_restaurant_category(session, category_name: str):
    """Get restaurant category by name (using existing categories only)"""
    mapped_name = CATEGORY_MAP.get(category_name, "Sandwiches")

    result = await session.execute(
        select(RestaurantCategory).where(RestaurantCategory.name == mapped_name)
    )
    category = result.scalar_one_or_none()

    # Fallback to Sandwiches if not found
    if not category:
        result = await session.execute(
            select(RestaurantCategory).where(RestaurantCategory.name == "Sandwiches")
        )
        category = result.scalar_one_or_none()

    return category


async def import_restaurant(session, restaurant_data: dict):
    """Import a single restaurant with its menu"""

    # Check if restaurant already exists
    result = await session.execute(
        select(Restaurant).where(Restaurant.name == restaurant_data["name_en"])
    )
    existing = result.scalar_one_or_none()

    if existing:
        print(f"  ⏭ {restaurant_data['name_en']} already exists, skipping...")
        return

    # Get category
    category = await get_or_create_restaurant_category(session, restaurant_data["category"])

    # Create restaurant
    restaurant = Restaurant(
        name=restaurant_data["name_en"],
        name_ar=restaurant_data["name_ar"],
        description=f"Delicious {restaurant_data['category']} food",
        description_ar=f"أطباق {restaurant_data['category']} لذيذة",
        category_id=category.id if category else None,
        phone_number=restaurant_data.get("phone", "+961 XX XXX XXX"),
        is_active=True,
        subscription_tier="basic",
        commission_rate=0.15,
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
    for idx, cat_data in enumerate(restaurant_data.get("categories", [])):
        cat = Category(
            menu_id=menu.id,
            name=cat_data["name_en"],
            name_ar=cat_data["name_ar"],
            order=idx
        )
        session.add(cat)
        await session.flush()

        for item_idx, item_data in enumerate(cat_data.get("items", [])):
            price = item_data.get("price", 0)
            has_variants = item_data.get("has_variants", False) or "variants" in item_data

            item = MenuItem(
                category_id=cat.id,
                name=item_data.get("name_en", item_data.get("name_ar", "")),
                name_ar=item_data.get("name_ar", ""),
                description=item_data.get("description", ""),
                description_ar=item_data.get("description_ar", ""),
                price=price if not has_variants else None,
                is_available=True,
                order=item_idx,
                has_variants=has_variants
            )
            session.add(item)
            await session.flush()

            # Add variants if present
            if has_variants and "variants" in item_data:
                for v_idx, variant in enumerate(item_data["variants"]):
                    v = MenuItemVariant(
                        menu_item_id=item.id,
                        name=variant["name"],
                        name_ar=variant.get("name_ar", variant["name"]),
                        price=variant["price"],
                        order=v_idx
                    )
                    session.add(v)

    await session.commit()
    print(f"  ✓ Created {restaurant_data['name_en']} with {len(restaurant_data.get('categories', []))} categories")


async def main():
    print("🚀 Starting import of ALL 32 restaurants from rest2.md...")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        for i, restaurant_data in enumerate(RESTAURANTS_DATA, 1):
            print(f"\n[{i}/32] 📍 Importing: {restaurant_data['name_en']} ({restaurant_data['name_ar']})...")
            try:
                await import_restaurant(session, restaurant_data)
            except Exception as e:
                print(f"  ✗ Error: {e}")
                await session.rollback()

    print("\n" + "=" * 60)
    print("✅ Import complete!")
    print(f"📊 Total restaurants processed: {len(RESTAURANTS_DATA)}")


if __name__ == "__main__":
    asyncio.run(main())
