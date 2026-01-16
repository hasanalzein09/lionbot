#!/usr/bin/env python3
"""
Third batch import script for additional restaurants from res.md
Contains: Al Ghali, Heartache, Sandwich Abou Afif, Al M3alem Subhi,
         Macmo, Mr. Croissant, Shawarma Abul El Oud, Shawarma Ghassan
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.restaurant import Restaurant, RestaurantCategory
from app.models.menu import Menu, Category, MenuItem, MenuItemVariant

# Exchange rate
LBP_TO_USD = 90000

CATEGORY_MAP = {
    "Sandwiches": "Sandwiches",
    "Burgers": "Sandwiches",
    "Shawarma": "Shawarma",
    "Grills": "Grills",
    "Lebanese": "Home Food",
    "Snacks": "Sandwiches",
    "Bakery": "Manakish",
    "Breakfast": "Breakfast",
    "Pizza": "Pizza",
}

RESTAURANTS_DATA = [
    {
        "name_en": "Al Ghali Mashawi & Snack",
        "name_ar": "الغالي مشاوي وسناك",
        "category": "Grills",
        "categories": [
            {
                "name_en": "Sandwiches",
                "name_ar": "ساندويشات",
                "items": [
                    {"name_en": "Fajita", "name_ar": "فاهيتا", "price": 4.22},
                    {"name_en": "Chicken Sub", "name_ar": "تشيكن ساب", "price": 3.89},
                    {"name_en": "Chinese (Sini)", "name_ar": "صيني", "price": 3.33},
                    {"name_en": "Steak Sub", "name_ar": "ستيك ساب", "price": 4.22},
                    {"name_en": "Crispy", "name_ar": "كريسبي", "price": 3.33},
                    {"name_en": "Chicken Pesto", "name_ar": "تشيكن بيستو", "price": 4.22},
                ]
            },
            {
                "name_en": "Burgers",
                "name_ar": "برغر",
                "items": [
                    {"name_en": "Crunchy Burger", "name_ar": "كرنشي برغر", "price": 3.89},
                    {"name_en": "Al Ghali Burger", "name_ar": "برغر الغالي", "price": 4.44},
                    {"name_en": "Classico Burger", "name_ar": "كلاسيكو برغر", "price": 4.44},
                    {"name_en": "Lebanese Burger", "name_ar": "برغر لبناني", "price": 3.33},
                    {"name_en": "Burger B", "name_ar": "برغر بي", "price": 5.00},
                    {"name_en": "Mushroom Burger", "name_ar": "ماشروم برغر", "price": 5.00},
                    {"name_en": "Mac Burger", "name_ar": "ماك برغر", "price": 3.89},
                    {"name_en": "Honey Butter", "name_ar": "هاني باتر", "price": 5.00},
                ]
            },
            {
                "name_en": "Appetizers",
                "name_ar": "مقبلات",
                "items": [
                    {"name_en": "Fried Potato (Large)", "name_ar": "بطاطا كبير", "price": 3.33},
                    {"name_en": "Fried Potato (Small)", "name_ar": "بطاطا صغير", "price": 2.22},
                    {"name_en": "Wedges", "name_ar": "ودجز", "price": 2.78},
                    {"name_en": "Mozzarella Sticks", "name_ar": "موزاريلا ستيكس", "price": 3.89},
                    {"name_en": "Grilled Chicken Platter", "name_ar": "صحن دجاج مشوي", "price": 7.78},
                    {"name_en": "Scaloppine Platter", "name_ar": "صحن سكالوبيني", "price": 7.78},
                ]
            },
            {
                "name_en": "Stuffed Potato",
                "name_ar": "بطاطا محشية",
                "items": [
                    {"name_en": "Golden Chicken Potato", "name_ar": "بطاطا دجاج ذهبي", "price": 3.89},
                    {"name_en": "Cheese Potato", "name_ar": "بطاطا جبنة", "price": 3.33},
                    {"name_en": "Chicken & BBQ Potato", "name_ar": "بطاطا دجاج باربكيو", "price": 3.89},
                    {"name_en": "Chicken & Spicy Sauce Potato", "name_ar": "بطاطا دجاج حار", "price": 3.89},
                ]
            },
            {
                "name_en": "Grill Platters",
                "name_ar": "صحون المشاوي",
                "items": [
                    {"name_en": "Boneless Chicken Meal", "name_ar": "وجبة دجاج مسحب", "price": 7.78},
                    {"name_en": "Boneless Chicken Whole", "name_ar": "فروج مسحب كامل", "price": 13.33},
                    {"name_en": "Mixed Grill 1 Kilo", "name_ar": "مشاوي مشكل كيلو", "price": 13.89},
                    {"name_en": "Mixed Grill Half Kilo", "name_ar": "مشاوي مشكل نص كيلو", "price": 7.78},
                    {"name_en": "Half Chicken with Fries", "name_ar": "نص فروج مع بطاطا", "price": 7.78},
                ]
            },
            {
                "name_en": "BBQ Skewers",
                "name_ar": "اسياخ مشوية",
                "items": [
                    {"name_en": "Makanek", "name_ar": "مقانق", "price": 1.11},
                    {"name_en": "Sujuk", "name_ar": "سجق", "price": 1.11},
                    {"name_en": "Khashkhash", "name_ar": "خشخاش", "price": 1.11},
                    {"name_en": "Kafta", "name_ar": "كفتة", "price": 1.11},
                    {"name_en": "Shqaf (Meat Chunks)", "name_ar": "شقف", "price": 1.11},
                    {"name_en": "Tawouk White", "name_ar": "طاووق أبيض", "price": 1.11},
                    {"name_en": "Tawouk Red", "name_ar": "طاووق أحمر", "price": 1.11},
                    {"name_en": "Sawda (Liver)", "name_ar": "سودة", "price": 1.11},
                ]
            },
        ]
    },
    {
        "name_en": "Heartache",
        "name_ar": "هارتايك",
        "category": "Sandwiches",
        "categories": [
            {
                "name_en": "Appetizers",
                "name_ar": "مقبلات",
                "items": [
                    {"name_en": "Fries", "name_ar": "بطاطا", "price": 2.00},
                    {"name_en": "Cheese & Fries", "name_ar": "بطاطا وجبنة", "price": 3.00},
                    {"name_en": "Crispy Loaded Fries", "name_ar": "بطاطا محملة كريسبي", "price": 4.50},
                    {"name_en": "Beef Loaded Fries", "name_ar": "بطاطا محملة لحمة", "price": 4.60},
                ]
            },
            {
                "name_en": "Sandwiches",
                "name_ar": "ساندويشات",
                "items": [
                    {"name_en": "Escalope", "name_ar": "اسكالوب", "price": 3.00},
                    {"name_en": "Tawook", "name_ar": "طاووق", "price": 2.80},
                    {"name_en": "Francisco", "name_ar": "فرانسيسكو", "price": 3.70},
                    {"name_en": "Crab", "name_ar": "كراب", "price": 3.80},
                    {"name_en": "Shrimps", "name_ar": "قريدس", "price": 4.00},
                    {"name_en": "Crab & Shrimps", "name_ar": "كراب وقريدس", "price": 4.20},
                    {"name_en": "Sojok", "name_ar": "سجق", "price": 3.80},
                    {"name_en": "Makanek", "name_ar": "مقانق", "price": 3.80},
                    {"name_en": "Fajita", "name_ar": "فاهيتا", "price": 4.20},
                    {"name_en": "Chicken Sub", "name_ar": "تشكن ساب", "price": 4.00},
                    {"name_en": "Twister", "name_ar": "تويستر", "price": 4.00},
                    {"name_en": "Rosto", "name_ar": "روستو", "price": 3.30},
                    {"name_en": "Rosto & Cheese", "name_ar": "روستو وجبنة", "price": 3.50},
                ]
            },
            {
                "name_en": "Burgers",
                "name_ar": "برغر",
                "items": [
                    {"name_en": "Mushroom", "name_ar": "ماشروم", "price": 4.50},
                    {"name_en": "Lebanese", "name_ar": "لبنانية", "price": 3.70},
                    {"name_en": "Zinger", "name_ar": "زنجر", "price": 4.15},
                    {"name_en": "Honey Bunny", "name_ar": "هاني باني", "price": 3.90},
                    {"name_en": "Crunchy", "name_ar": "كرنشي", "price": 4.00},
                    {"name_en": "Smashed", "name_ar": "سماشـد", "price": 4.25},
                ]
            },
            {
                "name_en": "Meals",
                "name_ar": "وجبات",
                "items": [
                    {"name_en": "Crispy Meal (6 pcs)", "name_ar": "وجبة كريسبي 6 قطع", "price": 6.00},
                    {"name_en": "Crispy Meal (4 pcs)", "name_ar": "وجبة كريسبي 4 قطع", "price": 5.00},
                ]
            },
            {
                "name_en": "Drinks",
                "name_ar": "مشروبات",
                "items": [
                    {"name_en": "Pepsi", "name_ar": "بيبسي", "price": 0.70},
                    {"name_en": "7up", "name_ar": "سفن اب", "price": 0.70},
                    {"name_en": "Miranda", "name_ar": "ميراندا", "price": 0.70},
                    {"name_en": "Water", "name_ar": "ماء", "price": 0.20},
                ]
            },
        ]
    },
    {
        "name_en": "Sandwich Abou Afif",
        "name_ar": "ساندويش ابو عفيف",
        "category": "Sandwiches",
        "categories": [
            {
                "name_en": "Sandwiches",
                "name_ar": "ساندويشات",
                "items": [
                    {"name_en": "Abou Afif Beef", "name_ar": "ابو عفيف لحمة", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Abou Afif Chicken", "name_ar": "ابو عفيف دجاج", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Francisco", "name_ar": "فرانسيسكو", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Spicy Chicken", "name_ar": "دجاج حار", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Luna", "name_ar": "لونا", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Chicken Sub", "name_ar": "دجاج صب", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Garlic Chicken", "name_ar": "دجاج و ثوم", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Escalope", "name_ar": "إسكالوب", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Tawouk", "name_ar": "طاووق", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Rosto", "name_ar": "روستو", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Sujuk", "name_ar": "سجق", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Makanek", "name_ar": "مقانق", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                ]
            },
            {
                "name_en": "Burgers",
                "name_ar": "برغر",
                "items": [
                    {"name_en": "Cheese Burger", "name_ar": "تشيز برغر", "price": 4.50},
                    {"name_en": "Escalope Bun", "name_ar": "إسكالوب بان", "price": 4.50},
                ]
            },
            {
                "name_en": "Fries",
                "name_ar": "بطاطا",
                "items": [
                    {"name_en": "Fries Sandwich", "name_ar": "ساندويش بطاطا", "price": 2.50, "variants": [
                        {"name": "20cm", "price": 2.50},
                        {"name": "25cm", "price": 3.50},
                    ]},
                    {"name_en": "Fries Box", "name_ar": "علبة بطاطا", "price": 2.50},
                ]
            },
            {
                "name_en": "Sweet Sandwiches",
                "name_ar": "ساندويشات حلوة",
                "items": [
                    {"name_en": "Nutella", "name_ar": "نوتيلا", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Nutella Halawa", "name_ar": "نوتيلا و حلاوة", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                    {"name_en": "Halawa & Butter", "name_ar": "حلاوة و زبدة", "price": 4.00, "variants": [
                        {"name": "20cm", "price": 4.00},
                        {"name": "25cm", "price": 5.00},
                    ]},
                ]
            },
            {
                "name_en": "Beverages",
                "name_ar": "مشروبات",
                "items": [
                    {"name_en": "Soft Drinks", "name_ar": "مشروبات غازية", "price": 1.00},
                    {"name_en": "Ayran", "name_ar": "عيران", "price": 1.00},
                    {"name_en": "Water", "name_ar": "مياه", "price": 0.50},
                ]
            },
        ]
    },
    {
        "name_en": "Al M3alem Subhi",
        "name_ar": "المعلم صبحي",
        "category": "Grills",
        "categories": [
            {
                "name_en": "Chicken Offers",
                "name_ar": "عروضات الفروج",
                "items": [
                    {"name_en": "2 Gas Roasted Chickens", "name_ar": "فروجين عالغاز كبار", "price": 18.44},
                    {"name_en": "Rice with Gas Chicken", "name_ar": "منسف رز مع فروج عالغاز", "price": 12.29},
                    {"name_en": "Rice with Charcoal Chicken", "name_ar": "منسف رز مع فروج فحم", "price": 13.97},
                    {"name_en": "Rice with Chicken Shawarma", "name_ar": "منسف رز مع شاورما دجاج", "price": 12.29},
                    {"name_en": "Rice with 20 Chicken Kebab", "name_ar": "منسف رز مع 20 سيخ كباب دجاج", "price": 13.97},
                    {"name_en": "Crispy Offer", "name_ar": "عرض القرمشة", "price": 24.58},
                    {"name_en": "Charcoal Chicken + 0.5kg Shawarma", "name_ar": "فروج فحم + نصف كيلو شاورما", "price": 23.46},
                    {"name_en": "Crispy 10 pcs Meal", "name_ar": "وجبة كرسبي 10 قطع", "price": 13.97},
                    {"name_en": "1kg Shawarma + Fries", "name_ar": "كيلو شاورما + محمرة", "price": 23.46},
                ]
            },
            {
                "name_en": "Subhi Boxes",
                "name_ar": "بوكسات المعلم صبحي",
                "items": [
                    {"name_en": "Rizo Mix Box", "name_ar": "بوكس ريزو ميكس", "price": 10.61},
                    {"name_en": "Turkish Box", "name_ar": "بوكس التركي", "price": 11.06},
                    {"name_en": "Snack Box", "name_ar": "بوكس السناك", "price": 13.97},
                    {"name_en": "Crispy Box", "name_ar": "بوكس القرمشة", "price": 12.29},
                    {"name_en": "Grilled Box", "name_ar": "بوكس المشوي", "price": 20.11},
                    {"name_en": "Markouk Box", "name_ar": "بوكس المرقوق", "price": 13.41},
                    {"name_en": "Box 2/3", "name_ar": "بوكس 2/3", "price": 12.85},
                    {"name_en": "Karam Box 1", "name_ar": "بوكس الكرم 1", "price": 12.85},
                    {"name_en": "Karam Box 2", "name_ar": "بوكس الكرم 2", "price": 12.85},
                    {"name_en": "Kaizer Mix Box", "name_ar": "بوكس الكايزر ميكس", "price": 12.85},
                    {"name_en": "Kaizer Meat Box", "name_ar": "بوكس الكايزر لحمة", "price": 13.41},
                    {"name_en": "Kaizer Chicken Box", "name_ar": "بوكس الكايزر دجاج", "price": 12.29},
                ]
            },
            {
                "name_en": "Shawarma",
                "name_ar": "قسم الشاورما",
                "items": [
                    {"name_en": "Chicken Shawarma Large", "name_ar": "سندويش شاورما دجاج لارج", "price": 2.79},
                    {"name_en": "Chicken Shawarma XL", "name_ar": "سندويش شاورما دجاج اكس لارج", "price": 5.03},
                    {"name_en": "Chicken Shawarma Turkish", "name_ar": "سندويش شاورما تركي دجاج", "price": 5.03},
                    {"name_en": "Chicken Kaizer Burger", "name_ar": "برغر شاورما دجاج كايزر", "price": 2.23},
                    {"name_en": "Cut Chicken Shawarma Meal", "name_ar": "وجبة شاورما دجاج مقطعة", "price": 5.31},
                    {"name_en": "Double Chicken Shawarma Meal", "name_ar": "وجبة شاورما دوبل", "price": 8.38},
                    {"name_en": "Turkish Chicken Shawarma Meal", "name_ar": "وجبة شاورما تركي", "price": 6.15},
                    {"name_en": "Shawarma with Rice", "name_ar": "وجبة شاورما مع رز", "price": 6.15},
                    {"name_en": "Half Kilo Chicken Shawarma", "name_ar": "نصف كيلو شاورما دجاج", "price": 12.29},
                    {"name_en": "1 Kilo Chicken Shawarma", "name_ar": "كيلو شاورما دجاج", "price": 23.46},
                    {"name_en": "Meat Shawarma Large", "name_ar": "سندويش شاورما لحمة لارج", "price": 3.91},
                    {"name_en": "Meat Shawarma XL", "name_ar": "سندويش شاورما لحمة اكس لارج", "price": 5.03},
                    {"name_en": "Meat Kaizer Burger", "name_ar": "برغر شاورما لحمة كايزر", "price": 2.23},
                    {"name_en": "Half Kilo Meat Shawarma", "name_ar": "نصف كيلو شاورما لحمة", "price": 13.41},
                    {"name_en": "1 Kilo Meat Shawarma", "name_ar": "كيلو شاورما لحمة", "price": 25.70},
                ]
            },
            {
                "name_en": "Sandwiches & Meals",
                "name_ar": "السندويشات والوجبات",
                "items": [
                    {"name_en": "Chicken Burger", "name_ar": "تشكن برغر", "price": 3.91, "variants": [
                        {"name": "Sandwich", "price": 3.91},
                        {"name": "Meal", "price": 5.03},
                    ]},
                    {"name_en": "Beef Burger", "name_ar": "برغر لحمة", "price": 5.03, "variants": [
                        {"name": "Sandwich", "price": 5.03},
                        {"name": "Meal", "price": 5.59},
                    ]},
                    {"name_en": "Zinger Burger", "name_ar": "برغر زنجر", "price": 5.03, "variants": [
                        {"name": "Sandwich", "price": 5.03},
                        {"name": "Meal", "price": 5.59},
                    ]},
                    {"name_en": "Crispy Sandwich", "name_ar": "سندويش كرسبي", "price": 5.03, "variants": [
                        {"name": "Sandwich", "price": 5.03},
                        {"name": "Meal", "price": 5.59},
                    ]},
                    {"name_en": "Escalope Sandwich", "name_ar": "سندويش اسكالوب", "price": 5.03, "variants": [
                        {"name": "Sandwich", "price": 5.03},
                        {"name": "Meal", "price": 5.59},
                    ]},
                    {"name_en": "Fajita Sandwich", "name_ar": "سندويش فاهيتا", "price": 5.59, "variants": [
                        {"name": "Sandwich", "price": 5.59},
                        {"name": "Meal", "price": 6.15},
                    ]},
                    {"name_en": "Chicken Sub", "name_ar": "سندويش تشكن ساب", "price": 5.03, "variants": [
                        {"name": "Sandwich", "price": 5.03},
                        {"name": "Meal", "price": 5.59},
                    ]},
                ]
            },
            {
                "name_en": "Charcoal Grills",
                "name_ar": "على الفحم",
                "items": [
                    {"name_en": "Charcoal Chicken Large", "name_ar": "سندويش دجاج على الفحم لارج", "price": 3.35},
                    {"name_en": "Charcoal Chicken XL", "name_ar": "سندويش دجاج على الفحم اكس لارج", "price": 6.15},
                    {"name_en": "Tawouk Large", "name_ar": "سندويش طاووق لارج", "price": 3.91},
                    {"name_en": "Tawouk XL", "name_ar": "سندويش طاووق اكس لارج", "price": 6.15},
                    {"name_en": "Kebab Large", "name_ar": "سندويش كباب لارج", "price": 3.35},
                    {"name_en": "Kebab XL", "name_ar": "سندويش كباب اكس لارج", "price": 5.03},
                    {"name_en": "Charcoal Chicken Meal", "name_ar": "وجبة دجاج على الفحم", "price": 5.59},
                    {"name_en": "Double Charcoal Chicken Meal", "name_ar": "وجبة دجاج على الفحم دوبل", "price": 8.94},
                    {"name_en": "Kebab Meal (6 skewers)", "name_ar": "وجبة كباب 6 اسياخ", "price": 7.26},
                    {"name_en": "Tawouk Meal (3 skewers)", "name_ar": "وجبة طاووق 3 اسياخ", "price": 7.26},
                    {"name_en": "Half Kilo Kebab", "name_ar": "نصف كيلو كباب", "price": 8.38},
                    {"name_en": "1 Kilo Kebab", "name_ar": "كيلو كباب", "price": 14.53},
                    {"name_en": "Half Kilo Tawouk", "name_ar": "نصف كيلو طاووق", "price": 9.50},
                    {"name_en": "1 Kilo Tawouk", "name_ar": "كيلو طاووق", "price": 17.88},
                ]
            },
            {
                "name_en": "Chicken Section",
                "name_ar": "قسم الفروج",
                "items": [
                    {"name_en": "Gas Roasted Chicken", "name_ar": "فروج مشوي غاز", "price": 10.61},
                    {"name_en": "Gas Chicken with Fries", "name_ar": "فروج مشوي غاز مع بطاطا", "price": 11.17},
                    {"name_en": "Gas Chicken with Rice", "name_ar": "فروج مشوي غاز مع صحن ارز", "price": 11.17},
                    {"name_en": "Half Gas Chicken with Fries", "name_ar": "نصف فروج غاز مع بطاطا", "price": 6.70},
                    {"name_en": "Broasted Chicken with Fries", "name_ar": "فروج بروستد مع بطاطا", "price": 14.53},
                    {"name_en": "Half Broasted with Fries", "name_ar": "نصف فروج بروستد مع بطاطا", "price": 7.82},
                    {"name_en": "Charcoal Chicken with Fries", "name_ar": "فروج فحم مع بطاطا", "price": 13.41},
                    {"name_en": "Charcoal Chicken with Rice", "name_ar": "فروج فحم مع صحن ارز", "price": 13.97},
                    {"name_en": "Half Charcoal Chicken", "name_ar": "نصف فروج فحم مع بطاطا او ارز", "price": 7.26},
                ]
            },
            {
                "name_en": "Appetizers & Drinks",
                "name_ar": "مقبلات ومشروبات",
                "items": [
                    {"name_en": "Fattoush", "name_ar": "فتوش", "price": 4.47},
                    {"name_en": "Tabbouleh", "name_ar": "تبولة", "price": 4.47},
                    {"name_en": "Caesar Salad", "name_ar": "سلطة سيزر", "price": 5.59},
                    {"name_en": "Rocca Salad", "name_ar": "سلطة روكا", "price": 4.47},
                    {"name_en": "Hummus", "name_ar": "حمص", "price": 4.47},
                    {"name_en": "Fries", "name_ar": "بطاطا", "price": 4.47},
                    {"name_en": "Cheese Rolls", "name_ar": "رقائق جبنة", "price": 4.47},
                    {"name_en": "Kibbeh", "name_ar": "كبة لحم", "price": 4.47},
                    {"name_en": "Rice Plate", "name_ar": "صحن ارز", "price": 4.47},
                    {"name_en": "Water", "name_ar": "مياه", "price": 0.45},
                    {"name_en": "Pepsi Plastic", "name_ar": "بيبسي بلاستيك", "price": 0.84},
                    {"name_en": "Pepsi Can", "name_ar": "بيبسي تنك", "price": 1.12},
                    {"name_en": "Laban Ayran", "name_ar": "لبن عيران", "price": 0.84},
                ]
            },
        ]
    },
    {
        "name_en": "Macmo",
        "name_ar": "ماكمو",
        "category": "Sandwiches",
        "categories": [
            {
                "name_en": "Beef Burgers",
                "name_ar": "برغر لحمة",
                "items": [
                    {"name_en": "Mo Beef", "name_ar": "مو بيف", "price": 3.35, "description": "Mo's Sauce, Iceberg, Onion, Cheddar Cheese, Pickles"},
                    {"name_en": "Big Mo Beef", "name_ar": "بيغ مو بيف", "price": 5.03, "description": "2 Beef Patties, Double Cheddar Cheese"},
                    {"name_en": "Double Mo Cheese Burger", "name_ar": "دبل مو تشيز برغر", "price": 5.03},
                    {"name_en": "King-Mo Beef", "name_ar": "كينغ مو بيف", "price": 5.59},
                    {"name_en": "Smoky Mo Beef", "name_ar": "سموكي مو بيف", "price": 6.70},
                ]
            },
            {
                "name_en": "Chicken Burgers",
                "name_ar": "برغر دجاج",
                "items": [
                    {"name_en": "Mo Chicken", "name_ar": "مو تشيكن", "price": 3.35},
                    {"name_en": "Big Mo Chicken", "name_ar": "بيغ مو تشيكن", "price": 5.03},
                    {"name_en": "Spicy Mo Chicken", "name_ar": "سبايسي مو تشيكن", "price": 3.91},
                    {"name_en": "Mighty Mo Chicken", "name_ar": "مايتي مو تشيكن", "price": 5.59},
                ]
            },
            {
                "name_en": "Kids Meal",
                "name_ar": "وجبات الأطفال",
                "items": [
                    {"name_en": "Mini-Mo Beef", "name_ar": "ميني مو بيف", "price": 2.23},
                    {"name_en": "Mini-Mo Chicken", "name_ar": "ميني مو تشيكن", "price": 2.23},
                    {"name_en": "Mini-Mo Cheese Burger", "name_ar": "ميني مو تشيز برغر", "price": 2.79},
                ]
            },
        ]
    },
    {
        "name_en": "Mr. Croissant",
        "name_ar": "مستر كرواسون",
        "category": "Bakery",
        "categories": [
            {
                "name_en": "Salty Croissant",
                "name_ar": "كرواسون مالح",
                "items": [
                    {"name_en": "Zaatar", "name_ar": "زعتر", "price": 0.56},
                    {"name_en": "Zaatar Baladi", "name_ar": "زعتر بلدي", "price": 1.12},
                    {"name_en": "Akkawi Cheese", "name_ar": "جبنة عكاوي", "price": 1.12},
                    {"name_en": "Kashkawan", "name_ar": "قشقوان", "price": 1.79},
                    {"name_en": "Mozzarella", "name_ar": "موزريلا", "price": 1.79},
                    {"name_en": "Halloumi", "name_ar": "حلوم", "price": 1.79},
                    {"name_en": "Bacon", "name_ar": "بيكون", "price": 1.79},
                    {"name_en": "Puck Cheese", "name_ar": "بوك", "price": 1.79},
                    {"name_en": "Kiri Cheese", "name_ar": "كيري", "price": 1.79},
                    {"name_en": "Two Cheeses", "name_ar": "جبنتين", "price": 2.23},
                    {"name_en": "3 Cheeses", "name_ar": "3 أجبان", "price": 2.50},
                ]
            },
        ]
    },
    {
        "name_en": "Shawarma Abul El Oud",
        "name_ar": "شاورما أبو العود",
        "category": "Shawarma",
        "categories": [
            {
                "name_en": "Chicken Shawarma",
                "name_ar": "شاورما دجاج",
                "items": [
                    {"name_en": "Chicken Shawarma Regular", "name_ar": "شاورما دجاج صغير", "price": 3.25},
                    {"name_en": "Chicken Shawarma Large", "name_ar": "شاورما دجاج كبير", "price": 4.45},
                    {"name_en": "Chicken Shawarma Markouk", "name_ar": "شاورما دجاج مرقوق", "price": 4.45},
                    {"name_en": "Cut Chicken Markook Meal", "name_ar": "وجبة دجاج مرقوق مقطعة", "price": 7.00},
                    {"name_en": "Chicken Shawarma Platter", "name_ar": "صحن شاورما دجاج", "price": 8.00},
                    {"name_en": "Cut Chicken Markook Double", "name_ar": "وجبة شاورما دجاج مقطعة دوبل", "price": 12.00},
                    {"name_en": "Half Kilo Chicken Shawarma", "name_ar": "نص كيلو شاورما دجاج", "price": 14.00},
                    {"name_en": "1 Kilo Chicken Shawarma", "name_ar": "كيلو شاورما دجاج", "price": 28.00},
                    {"name_en": "Mix Meal", "name_ar": "وجبة Mix", "price": 14.00},
                ]
            },
            {
                "name_en": "Beef Shawarma",
                "name_ar": "شاورما لحمة",
                "items": [
                    {"name_en": "Beef Shawarma Regular", "name_ar": "شاورما لحمة صغير", "price": 4.50},
                    {"name_en": "Beef Shawarma Large", "name_ar": "شاورما لحمة كبير", "price": 7.00},
                    {"name_en": "Beef Shawarma Markouk", "name_ar": "شاورما لحمة مرقوق", "price": 7.00},
                    {"name_en": "Cut Markook Beef Meal", "name_ar": "وجبة لحمة مرقوق مقطعة", "price": 10.50},
                    {"name_en": "Beef Shawarma Platter", "name_ar": "صحن شاورما لحمة", "price": 12.00},
                    {"name_en": "Cut Markook Beef Double", "name_ar": "وجبة لحمة مرقوق مقطعة دوبل", "price": 15.50},
                    {"name_en": "Half Kilo Beef Shawarma", "name_ar": "نص كيلو شاورما لحمة", "price": 20.00},
                    {"name_en": "1 Kilo Beef Shawarma", "name_ar": "كيلو شاورما", "price": 40.00},
                ]
            },
            {
                "name_en": "Turkish Items",
                "name_ar": "أصناف تركية",
                "items": [
                    {"name_en": "Shawarma Wrap Chicken", "name_ar": "شاورما راب دجاج", "price": 4.45},
                    {"name_en": "Chicken Döner Turkey", "name_ar": "شاورما دجاج دونر تركي", "price": 6.00},
                    {"name_en": "Chicken Döner Combo", "name_ar": "كومبو دونر دجاج", "price": 7.00},
                    {"name_en": "Döner Sojouk", "name_ar": "دونر سجق", "price": 7.00},
                    {"name_en": "Beef Döner Turkey", "name_ar": "شاورما لحمة دونر تركي", "price": 8.00},
                    {"name_en": "Shawarma Wrap Beef", "name_ar": "شاورما راب لحمة", "price": 7.00},
                ]
            },
            {
                "name_en": "Fries",
                "name_ar": "بطاطا",
                "items": [
                    {"name_en": "Turkish Fries Sandwich", "name_ar": "ساندويش بطاطا تركي", "price": 2.00},
                    {"name_en": "Fries Sandwich", "name_ar": "ساندويش بطاطا", "price": 2.00},
                    {"name_en": "Fries Regular", "name_ar": "بطاطا صغير", "price": 2.00},
                ]
            },
            {
                "name_en": "Salads",
                "name_ar": "سلطات",
                "items": [
                    {"name_en": "Shawarma Caesar Salad", "name_ar": "شاورما سيزر سالاد", "price": 7.00},
                    {"name_en": "Caesar Salad", "name_ar": "سيزر سالاد", "price": 4.00},
                    {"name_en": "Fattoush", "name_ar": "فتوش", "price": 4.00},
                ]
            },
            {
                "name_en": "Offers",
                "name_ar": "عروضات",
                "items": [
                    {"name_en": "The Combo Deal", "name_ar": "The Combo Deal", "price": 7.00},
                    {"name_en": "The Döner Deal", "name_ar": "The Döner Deal", "price": 7.00},
                    {"name_en": "Beef Döner Combo", "name_ar": "كومبو دونر لحمة", "price": 10.00},
                    {"name_en": "Kaizer Chicken", "name_ar": "كايزر دجاج", "price": 18.00},
                    {"name_en": "Kaizer Bites Mix", "name_ar": "كايزر بايتس ميكس", "price": 20.00},
                    {"name_en": "Kaizer Mix", "name_ar": "كايزر ميكس", "price": 24.00},
                    {"name_en": "Abul El Oud Bites", "name_ar": "ابو العود بايتس", "price": 28.00},
                    {"name_en": "Kaizer Meat", "name_ar": "كايزر لحمة", "price": 30.00},
                    {"name_en": "Abul El Oud Bites Mix", "name_ar": "ابو العود بايتس دجاج ولحمة", "price": 35.00},
                ]
            },
            {
                "name_en": "Drinks",
                "name_ar": "مشروبات",
                "items": [
                    {"name_en": "Water", "name_ar": "مياه", "price": 0.30},
                    {"name_en": "Pepsi", "name_ar": "بيبسي", "price": 1.10},
                    {"name_en": "Seven Up", "name_ar": "سفن أب", "price": 1.10},
                    {"name_en": "Miranda", "name_ar": "ميراندا", "price": 1.10},
                    {"name_en": "Ice Tea", "name_ar": "Ice Tea", "price": 1.10},
                    {"name_en": "Yogurt", "name_ar": "لبن", "price": 1.10},
                ]
            },
        ]
    },
    {
        "name_en": "Shawarma Ghassan",
        "name_ar": "شاورما غسان",
        "category": "Shawarma",
        "categories": [
            {
                "name_en": "Chicken Shawarma",
                "name_ar": "شاورما دجاج",
                "items": [
                    {"name_en": "Chicken Shawarma Medium", "name_ar": "سندويش شاورما دجاج وسط", "price": 4.00},
                    {"name_en": "Chicken Shawarma Large", "name_ar": "سندويش شاورما دجاج كبير", "price": 5.00},
                    {"name_en": "Chicken Shawarma Markouk", "name_ar": "سندويش شاورما دجاج مرقوق", "price": 5.00},
                    {"name_en": "Dozen Chicken Shawarma", "name_ar": "دزينة شاورما دجاج", "price": 15.00},
                    {"name_en": "1kg Chicken Shawarma", "name_ar": "شاورما دجاج 1000 غ", "price": 35.00},
                ]
            },
            {
                "name_en": "Beef Shawarma",
                "name_ar": "شاورما لحمة",
                "items": [
                    {"name_en": "Beef Shawarma Medium", "name_ar": "سندويش شاورما لحمة وسط", "price": 5.00},
                    {"name_en": "Beef Shawarma Large", "name_ar": "سندويش شاورما لحمة كبير", "price": 6.00},
                    {"name_en": "Beef Shawarma Markouk", "name_ar": "سندويش شاورما لحمة مرقوق", "price": 6.00},
                    {"name_en": "Dozen Beef Shawarma", "name_ar": "دزينة شاورما لحمة", "price": 15.00},
                    {"name_en": "1kg Beef Shawarma", "name_ar": "شاورما لحمة 1000 غ", "price": 40.00},
                ]
            },
            {
                "name_en": "Burgers",
                "name_ar": "برغر",
                "items": [
                    {"name_en": "Chicken Burger", "name_ar": "سندويش برغر دجاج", "price": 4.00},
                ]
            },
        ]
    },
]

async def get_or_create_restaurant_category(session, category_name: str):
    """Get or create a restaurant category"""
    result = await session.execute(
        select(RestaurantCategory).where(RestaurantCategory.name == category_name)
    )
    category = result.scalar_one_or_none()

    if not category:
        # Map to existing categories
        existing_map = {
            "Sandwiches": "Sandwiches",
            "Burgers": "Sandwiches",
            "Shawarma": "Shawarma",
            "Grills": "Grills",
            "Lebanese": "Home Food",
            "Snacks": "Sandwiches",
            "Bakery": "Manakish",
            "Breakfast": "Breakfast",
            "Pizza": "Pizza",
        }
        mapped_name = existing_map.get(category_name, "Sandwiches")
        result = await session.execute(
            select(RestaurantCategory).where(RestaurantCategory.name == mapped_name)
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
        phone_number="+961 XX XXX XXX",
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
            has_variants = "variants" in item_data

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
            if has_variants:
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
    print(f"  ✓ Created {restaurant_data['name_en']}")

async def main():
    async with AsyncSessionLocal() as session:
        for restaurant_data in RESTAURANTS_DATA:
            print(f"Importing: {restaurant_data['name_en']}...")
            try:
                await import_restaurant(session, restaurant_data)
            except Exception as e:
                print(f"  ✗ Error: {e}")
                await session.rollback()

        print("\n✅ All restaurants imported successfully!")

if __name__ == "__main__":
    asyncio.run(main())
