"""Script to import restaurants from res.md file"""
import asyncio
import re
import json
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.restaurant import Restaurant, RestaurantCategory
from app.models.menu import Menu, Category, MenuItem, MenuItemVariant

# Restaurant data parsed from res.md
RESTAURANTS_DATA = [
    {
        "name": "King Croissant",
        "name_ar": "كينج كرواسون",
        "category": "Bakery",
        "menu": [
            {"category_en": "Tripoli Kaak", "category_ar": "كعكة طرابلسية", "items": [
                {"name_ar": "زعتر وعكاوي", "price": 2.22},
                {"name_ar": "عكاوي", "price": 2.56},
                {"name_ar": "عكاوي وقشقوان", "price": 2.78},
                {"name_ar": "حلوم مع خضار", "price": 3.33},
                {"name_ar": "لبنة حرة", "price": 3.33},
                {"name_ar": "لبنة مع خضار", "price": 3.33},
                {"name_ar": "زعتر مع جبنة", "price": 3.89},
                {"name_ar": "مرتديلا وقشقوان", "price": 3.33},
                {"name_ar": "حبش صدر مدخن", "price": 3.33},
                {"name_ar": "3 أجبان", "price": 2.78},
                {"name_ar": "4 أجبان", "price": 2.56},
                {"name_ar": "5 أجبان", "price": 2.78},
                {"name_ar": "بيكون", "price": 2.22},
                {"name_ar": "بيكون مع عكاوي", "price": 2.56},
                {"name_ar": "جبنة وشيتوس", "price": 2.78},
                {"name_ar": "سجق", "price": 2.89},
                {"name_ar": "بيبروني", "price": 2.78},
                {"name_ar": "هوت دوج", "price": 2.00},
                {"name_ar": "شاورما", "price": 2.22},
                {"name_ar": "فاهيتا", "price": 2.22},
                {"name_ar": "طاووق مع موزاريلا", "price": 2.78},
                {"name_ar": "بستاشيو", "price": 3.33},
                {"name_ar": "لوتس", "price": 2.89},
                {"name_ar": "كوكتيل شوكولا", "price": 3.11},
                {"name_ar": "نوتيلا", "price": 3.33},
            ]},
            {"category_en": "Croissant Pizza", "category_ar": "كرواسون بيتزا", "items": [
                {"name_ar": "بيتزا خضار", "price": 3.33},
                {"name_ar": "بيتزا مرتديلا كوكتيل حبش", "price": 3.33},
                {"name_ar": "بيتزا حبش مدخن", "price": 3.67},
                {"name_ar": "بيتزا سجق", "price": 3.67},
                {"name_ar": "بيتزا بيبروني", "price": 3.67},
                {"name_ar": "بيتزا هوت دوج", "price": 3.89},
                {"name_ar": "3 أجبان مفتوح", "price": 3.33},
                {"name_ar": "4 أجبان مفتوح", "price": 3.67},
                {"name_ar": "5 أجبان مفتوح", "price": 3.89},
                {"name_ar": "طاووق موزاريلا مفتوح", "price": 3.89},
                {"name_ar": "فاهيتا موزاريلا مفتوح", "price": 3.89},
                {"name_ar": "قاورما مفتوح", "price": 4.44},
                {"name_ar": "كشك مفتوح", "price": 3.00},
                {"name_ar": "زعتر مفتوح", "price": 1.67},
                {"name_ar": "جبنة مفتوح", "price": 2.78},
            ]},
            {"category_en": "Stuffed Croissant", "category_ar": "كرواسون محشي", "items": [
                {"name_ar": "كرواسون سادة", "price": 0.78},
                {"name_ar": "زعتر", "price": 0.78},
                {"name_ar": "عكاوي", "price": 1.00},
                {"name_ar": "شوكولا", "price": 1.00},
                {"name_ar": "لوز", "price": 1.67},
                {"name_ar": "قشقوان", "price": 2.67},
                {"name_ar": "عكاوي وقشقوان", "price": 2.67},
                {"name_ar": "لبنة سادة", "price": 1.67},
                {"name_ar": "لبنة مع خضار", "price": 1.89},
                {"name_ar": "حلوم", "price": 2.56},
                {"name_ar": "حلوم وعكاوي", "price": 2.78},
            ]},
            {"category_en": "Sweet Croissant", "category_ar": "كرواسون حلو", "items": [
                {"name_ar": "نوتيلا", "price": 2.56},
                {"name_ar": "كندر", "price": 2.67},
                {"name_ar": "غلاكسي", "price": 2.44},
                {"name_ar": "لوتس", "price": 2.78},
                {"name_ar": "أوريو", "price": 2.44},
                {"name_ar": "بستاشيو", "price": 2.78},
                {"name_ar": "كرانش", "price": 2.22},
                {"name_ar": "باونتي", "price": 2.22},
                {"name_ar": "كيت كات", "price": 2.22},
            ]},
            {"category_en": "Knefeh", "category_ar": "كنافة", "items": [
                {"name_ar": "كعكة الكنافة", "price": 2.22},
                {"name_ar": "صحن الكنافة", "price": 3.33},
                {"name_ar": "كنافة بالكرواسون", "price": 2.78},
                {"name_ar": "كنافة بالكرواسون مع البستاشيو", "price": 3.89},
                {"name_ar": "كيلو كنافة بالجبن", "price": 11.11},
            ]},
            {"category_en": "Saj", "category_ar": "صاج", "items": [
                {"name_ar": "زعتر", "price": 1.33},
                {"name_ar": "زعتر مع خضار", "price": 1.67},
                {"name_ar": "لبنة سادة", "price": 1.67},
                {"name_ar": "لبنة مع خضار", "price": 2.56},
                {"name_ar": "عكاوي", "price": 2.56},
                {"name_ar": "عكاوي وقشقوان", "price": 2.89},
                {"name_ar": "طاووق وموزاريلا", "price": 3.89},
                {"name_ar": "فاهيتا", "price": 4.44},
                {"name_ar": "شاورما دجاج", "price": 4.44},
            ]},
        ]
    },
    {
        "name": "Furn Libnan",
        "name_ar": "فرن لبنان",
        "category": "Bakery",
        "menu": [
            {"category_en": "Regular Manakish", "category_ar": "مناقيش عادية", "items": [
                {"name": "Jebneh Akkawi - Regular", "name_ar": "جبنة عكاوي - عادي", "price": 2.00},
                {"name": "Jebneh Akkawi - Extra", "name_ar": "جبنة عكاوي - اكسترا", "price": 2.80},
                {"name": "Akkawi & Kashkaval - Regular", "name_ar": "عكاوي وقشقوان - عادي", "price": 2.80},
                {"name": "Four Cheese - Regular", "name_ar": "فور تشيز - عادي", "price": 2.80},
                {"name": "Half Cheese Half Zaatar - Regular", "name_ar": "نص جبنة نص زعتر - عادي", "price": 1.45},
                {"name": "Zaatar Baladi - Regular", "name_ar": "زعتر بلدي - عادي", "price": 0.80},
                {"name": "Labneh Mix - Regular", "name_ar": "خلطة اللبنة - عادي", "price": 1.65},
                {"name": "Keshek Mix - Regular", "name_ar": "خلطة الكشك - عادي", "price": 1.65},
            ]},
            {"category_en": "Meat Manakish", "category_ar": "مناقيش لحمة", "items": [
                {"name": "Meat Pie (Lahm Baajin)", "name_ar": "لحمة بعجين", "price": 2.80},
                {"name": "Kafta w Cheese", "name_ar": "كفتة مع جبنة", "price": 3.35},
                {"name": "Mortadella w Cheese", "name_ar": "مرتديلا وجبنة", "price": 3.35},
                {"name": "Sojok w Cheese", "name_ar": "سجق وجبنة", "price": 3.35},
                {"name": "Awarma w Cheese", "name_ar": "قاورما وجبنة", "price": 3.90},
                {"name": "Tawook w Cheese", "name_ar": "طاووق وجبنة", "price": 3.90},
                {"name": "Fajita w Cheese", "name_ar": "فاهيتا وجبنة", "price": 3.90},
            ]},
            {"category_en": "Pizza", "category_ar": "بيتزا", "items": [
                {"name": "Pizza Mortadella", "name_ar": "بيتزا مرتديلا", "price": 5.00},
                {"name": "Pizza Sojok", "name_ar": "بيتزا سجق", "price": 5.00},
                {"name": "Pizza Awarma", "name_ar": "بيتزا قاورما", "price": 5.55},
                {"name": "Pizza Pepperoni", "name_ar": "بيتزا ببروني", "price": 5.00},
                {"name": "Pizza Veggie", "name_ar": "بيتزا خضار", "price": 4.45},
            ]},
            {"category_en": "Refreshments", "category_ar": "مشروبات", "items": [
                {"name": "Soft Drinks", "name_ar": "مشروبات غازية", "price": 0.90},
                {"name": "Laban", "name_ar": "لبن", "price": 0.90},
                {"name": "Water", "name_ar": "مياه", "price": 0.35},
            ]},
        ]
    },
    {
        "name": "BOUDI SANDWICH",
        "name_ar": "بودي ساندويش",
        "category": "Sandwiches",
        "menu": [
            {"category_en": "Chicken Sandwiches", "category_ar": "ساندويشات دجاج", "items": [
                {"name": "Chicken Liver (Sawda)", "name_ar": "سودة", "description": "Garlic, Pickles, Salt", "price": 2.00},
                {"name": "Chicken", "name_ar": "دجاج", "description": "Garlic, Pickles", "price": 2.00},
                {"name": "Tawook", "name_ar": "طاووق", "description": "Garlic, Pickles", "price": 2.20},
                {"name": "Curry", "name_ar": "كاري", "description": "Garlic, Pickles", "price": 2.20},
                {"name": "Chinese (Sini)", "name_ar": "صيني", "description": "Mayo, Garlic, Pickles", "price": 2.20},
                {"name": "Mexican", "name_ar": "مكسيكان", "description": "Avocado, Corn, Lettuce", "price": 2.20},
            ]},
            {"category_en": "Meat Sandwiches", "category_ar": "ساندويشات لحمة", "items": [
                {"name": "Steak", "name_ar": "ستيك", "description": "Mayo, BBQ, Spicy, Mozzarella, Cheddar", "price": 3.45},
                {"name": "Philadelphia", "name_ar": "فيلادلفيا", "description": "Mayo, Cheese, Mozzarella", "price": 3.45},
                {"name": "Rosto", "name_ar": "روستو", "description": "Mayo, Mustard, Pickles, Lettuce", "price": 2.80},
                {"name": "Makanek", "name_ar": "مقانق", "description": "Garlic, Pickles, Lemon", "price": 2.00},
                {"name": "Sojok", "name_ar": "سجق", "description": "Garlic, Pickles, Lemon", "price": 2.00},
            ]},
            {"category_en": "Subs", "category_ar": "سابز", "items": [
                {"name": "Fajita", "name_ar": "فاهيتا", "description": "Avocado, Pepper, Onion, Mozzarella", "price": 4.00},
                {"name": "Boudi Special", "name_ar": "بودي", "description": "Fries, Mayo, BBQ, Corn, Lettuce, Cheese", "price": 4.00},
                {"name": "Chicken Sub", "name_ar": "تشيكن ساب", "description": "Sub Sauce, Pickles, Lettuce, Cheese", "price": 4.00},
                {"name": "Francisco", "name_ar": "فرنسيسكو", "description": "Mayo, Pickles, Corn, Lettuce, Cheese", "price": 4.00},
            ]},
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "Burger", "name_ar": "برغر", "description": "Fries, Salad, Cocktail Sauce", "price": 2.80},
                {"name": "Chicken Burger", "name_ar": "تشيكن برغر", "description": "Fries, Mayo, Pickles, Lettuce", "price": 2.80},
                {"name": "Chicken Breast Burger", "name_ar": "تشيكن بريست", "description": "Mayo, Mozzarella, Cheddar, Lettuce", "price": 4.00},
            ]},
            {"category_en": "Fish", "category_ar": "سمك", "items": [
                {"name": "Shrimp (Kreides)", "name_ar": "قريدس", "description": "Tartar, Lemon, Lettuce", "price": 2.65},
                {"name": "Fish Fillet", "name_ar": "فيليه سمك", "description": "Mayo, Lemon, Lettuce", "price": 2.00},
            ]},
            {"category_en": "Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Pepsi", "name_ar": "بيبسي", "price": 1.10},
                {"name": "Laban", "name_ar": "لبن", "price": 1.10},
                {"name": "Water", "name_ar": "مياه", "price": 0.30},
            ]},
        ]
    },
    {
        "name": "KAAKÉ by meat chop",
        "name_ar": "كعكة باي ميت شوب",
        "category": "Bakery",
        "menu": [
            {"category_en": "Food", "category_ar": "طعام", "items": [
                {"name": "Zaatar", "name_ar": "زعتر", "price": 1.00},
                {"name": "Keshek", "name_ar": "كشك", "price": 1.65},
                {"name": "Keshek w jebneh", "name_ar": "كشك وجبنة", "price": 2.45},
                {"name": "Jebneh 3ekawi", "name_ar": "جبنة عكاوي", "price": 2.00},
                {"name": "3ekawi w mozzarella", "name_ar": "عكاوي وموزاريلا", "price": 2.45},
                {"name": "4 cheese", "name_ar": "4 أجبان", "price": 3.35},
                {"name": "Cheese & Chips", "name_ar": "جبنة وشيبس", "price": 3.00},
                {"name": "Haloum pesto", "name_ar": "حلوم بيستو", "price": 3.35},
                {"name": "Labni", "name_ar": "لبنة", "price": 1.65},
                {"name": "Sojok w jebneh", "name_ar": "سجق وجبنة", "price": 4.90},
                {"name": "Awarma w jebneh", "name_ar": "قاورما وجبنة", "price": 4.90},
                {"name": "Fajitas", "name_ar": "فاهيتا", "price": 4.35},
                {"name": "Tawook", "name_ar": "طاووق", "price": 4.35},
                {"name": "Nutella banana", "name_ar": "نوتيلا موز", "price": 3.00},
            ]},
            {"category_en": "Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Soft drinks", "name_ar": "مشروبات غازية", "price": 1.65},
                {"name": "Water", "name_ar": "مياه", "price": 0.55},
                {"name": "Ice tea", "name_ar": "شاي مثلج", "price": 1.65},
            ]},
        ]
    },
    {
        "name": "Bayt Al Nar",
        "name_ar": "بيت النار",
        "category": "Bakery",
        "menu": [
            {"category_en": "Manakish", "category_ar": "مناقيش", "items": [
                {"name": "Jebneh (Cheese)", "name_ar": "جبنة", "price": 1.65},
                {"name": "Zaatar", "name_ar": "زعتر", "price": 0.55},
                {"name": "Keshek", "name_ar": "كشك", "price": 1.45},
                {"name": "Mortadella", "name_ar": "مرتديلا", "price": 2.00},
                {"name": "Sojok", "name_ar": "سجق", "price": 2.20},
                {"name": "Tawook", "name_ar": "طاووق", "price": 3.35},
                {"name": "Fajita", "name_ar": "فاهيتا", "price": 3.35},
                {"name": "Awarma", "name_ar": "قاورما", "price": 3.35},
                {"name": "Labneh w Khodra", "name_ar": "لبنة مع خضرة", "price": 1.65},
                {"name": "Halloumi", "name_ar": "حلومي", "price": 1.75},
                {"name": "Bacon", "name_ar": "بيكون", "price": 2.00},
            ]},
            {"category_en": "Pizza", "category_ar": "بيتزا", "items": [
                {"name": "Pizza Khodra (Veggie)", "name_ar": "بيتزا خضار", "price": 3.35},
                {"name": "Pizza Mortadella", "name_ar": "بيتزا مرتديلا", "price": 4.45},
                {"name": "Pizza Sojok", "name_ar": "بيتزا سجق", "price": 4.45},
                {"name": "Pizza Awarma", "name_ar": "بيتزا قاورما", "price": 5.00},
                {"name": "Pizza Pepperoni", "name_ar": "بيتزا بيبروني", "price": 5.00},
                {"name": "Pizza Margherita", "name_ar": "بيتزا مارغريتا", "price": 3.90},
            ]},
        ]
    },
    {
        "name": "Foul w Trawiqa",
        "name_ar": "فول وطراويقا",
        "category": "Breakfast",
        "menu": [
            {"category_en": "Main Items", "category_ar": "أطباق رئيسية", "items": [
                {"name": "Large Foul Plate", "name_ar": "صحن فول كبير", "price": 3.35},
                {"name": "Clay Pot Foul", "name_ar": "صحن فول فخار", "price": 2.20},
                {"name": "Large Msawha", "name_ar": "صحن مشوشة كبير", "price": 3.35},
                {"name": "Large Hommos", "name_ar": "صحن حمص كبير", "price": 3.35},
                {"name": "Large Fatteh Bowl", "name_ar": "جاط فتة كبير", "price": 7.20},
                {"name": "Small Fatteh Bowl", "name_ar": "جاط فتة صغير", "price": 5.00},
                {"name": "Dozen Falafel", "name_ar": "دزينة فلافل", "price": 5.55},
            ]},
            {"category_en": "Breakfast Plates", "category_ar": "أطباق فطور", "items": [
                {"name": "Labneh Plate with sides", "name_ar": "صحن لبنة مع سرفيس", "price": 2.80},
                {"name": "Cheese Plate with sides", "name_ar": "صحن جبنة مع سرفيس", "price": 2.80},
                {"name": "Eggs Plate with sides", "name_ar": "صحن بيض مع سرفيس", "price": 2.80},
                {"name": "Sojok Plate with sides", "name_ar": "صحن سجق مع سرفيس", "price": 5.00},
                {"name": "Awarma Plate with sides", "name_ar": "صحن قورما مع سرفيس", "price": 5.00},
            ]},
        ]
    },
    {
        "name": "Mido's",
        "name_ar": "ميدوز",
        "category": "Sandwiches",
        "menu": [
            {"category_en": "Sandwiches", "category_ar": "ساندويشات", "items": [
                {"name": "Chicken Sub", "description": "Grilled Chicken, Soy Sauce, Tomato, Pickles, Iceberg, Garlic, Mayo and Mozzarella", "price": 8.33},
                {"name": "Crispy Chicken", "description": "Crispy, Tomato, Iceberg, Mayo and Cheddar", "price": 7.22},
                {"name": "Turkey N' Cheese", "description": "Turkey, Cheese, Tomato, Iceberg, Pickles, Mustard and Mayo", "price": 5.56},
                {"name": "Roast Beef", "description": "Roast Beef, Tomato, Iceberg, Pickles, Mustard and Mayo", "price": 8.33},
                {"name": "Mido's Chicken", "description": "Grilled Chicken, Cheddar, Corn, Tomato, Iceberg and Mayo", "price": 8.89},
                {"name": "Philadelphia", "description": "Shredded Beef, Soy Sauce, Onion, Mushroom, Capsicum, Iceberg and Mayo", "price": 9.56},
                {"name": "Fajita", "description": "Grilled Chicken, Soy Sauce, Mozzarella, Onion, Mushroom, Capsicum, Iceberg and Mayo", "price": 9.33},
                {"name": "Francisco", "description": "Grilled Chicken, Mozzarella, Corn, Soy Sauce, Pickles, Iceberg and Mayo", "price": 8.33},
            ]},
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "Midos Burger", "description": "Grilled Chicken, Mozzarella Patty, Honey Mustard and Lettuce", "price": 10.00},
                {"name": "Lebanese Burger", "description": "Beef Burger, French Fries, Coleslaw and Ketchup", "price": 7.78},
                {"name": "Swiss Mushroom Burger", "description": "Beef Burger, Swiss Cheese, Fresh Mushroom and Special Sauce", "price": 9.56},
                {"name": "Smash Burger", "description": "Beef Patties (2) each 70gr, Cocktail Sauce, Cheddar Slice, Onions and Pickles", "price": 8.33},
                {"name": "Truffle Burger", "description": "Beef Patty, Truffle Sauce and Swiss Cheese", "price": 10.00},
            ]},
            {"category_en": "Salads", "category_ar": "سلطات", "items": [
                {"name": "Chef Salad", "description": "Iceberg, Cucumber, Tomato, Corn, Carrot, Fresh Mushroom, Turkey, Mozzarella Cheese", "price": 10.00},
                {"name": "Greek Salad", "description": "Iceberg, Cucumber, Tomato, Olives, Vita Cheese and Oregano", "price": 6.44},
                {"name": "Caesar Salad", "description": "Iceberg, Parmesan Cheese, Grilled Chicken and Toast Pieces", "price": 10.00},
            ]},
            {"category_en": "Starters", "category_ar": "مقبلات", "items": [
                {"name": "Mozzarella Sticks", "description": "4pcs Mozzarella Sticks & BBQ", "price": 4.44},
                {"name": "Wedges Box", "description": "Fried Wedges & Ketchup Dip", "price": 5.00},
                {"name": "Curly Fries", "description": "Fried Curly & Cocktail Dip", "price": 6.67},
                {"name": "French Fries Box", "description": "Fried Potato, Special Spices & Ketchup", "price": 4.44},
            ]},
            {"category_en": "Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Soft Drinks", "name_ar": "مشروبات غازية", "description": "Pepsi, Mirinda, 7up", "price": 1.67},
                {"name": "Water", "name_ar": "مياه", "price": 1.11},
            ]},
        ]
    },
    {
        "name": "3AJINEH",
        "name_ar": "عجينة",
        "category": "Bakery",
        "menu": [
            {"category_en": "Manakeesh & Savory Pastries", "category_ar": "مناقيش ومعجنات", "items": [
                {"name": "Zaatar", "name_ar": "زعتر", "price": 1.10},
                {"name": "Zaatar And Labneh", "name_ar": "زعتر ولبنة", "price": 2.78},
                {"name": "Keshek", "name_ar": "كشك", "price": 2.78},
                {"name": "Akkawi Cheese", "name_ar": "جبنة عكاوي", "price": 2.50},
                {"name": "Mozzerella", "name_ar": "موزاريلا", "price": 4.00},
                {"name": "Halloum And Mozzarella", "name_ar": "حلوم وموزاريلا", "price": 4.00},
                {"name": "Four Cheese", "name_ar": "4 أجبان", "price": 4.60},
                {"name": "Sojok and Mozzarella", "name_ar": "سجق وموزاريلا", "price": 4.00},
                {"name": "Kafta and Mozzarella", "name_ar": "كفتة وموزاريلا", "price": 5.00},
                {"name": "Kawarma And mozzarella", "name_ar": "قاورما وموزاريلا", "price": 5.00},
                {"name": "Tawook and Cheese", "name_ar": "طاووق وجبنة", "price": 4.50},
            ]},
            {"category_en": "Pizza", "category_ar": "بيتزا", "items": [
                {"name": "Sweet & Chilli Pizza", "description": "Sweet And Chilli Sauce, Chicken, Mozzarella Cheese", "price": 6.00},
                {"name": "BBQ Chicken Pizza", "name_ar": "بيتزا دجاج باربكيو", "price": 6.00},
                {"name": "Pizza Margherita", "name_ar": "بيتزا مارغريتا", "price": 6.00},
                {"name": "Vegetarian Pizza", "name_ar": "بيتزا خضار", "price": 6.00},
                {"name": "American Peperoni Pizza", "name_ar": "بيتزا بيبروني أمريكي", "price": 6.00},
            ]},
            {"category_en": "Wraps", "category_ar": "راب", "items": [
                {"name": "Turkey Wrap", "name_ar": "راب حبش", "price": 6.00},
                {"name": "Sweet Chilli Wrap", "name_ar": "راب سويت تشيلي", "price": 6.00},
                {"name": "BBQ Chicken Wrap", "name_ar": "راب دجاج باربكيو", "price": 6.00},
                {"name": "Kawarma Wrap", "name_ar": "راب قاورما", "price": 6.00},
                {"name": "Labneh wrap", "name_ar": "راب لبنة", "price": 3.00},
            ]},
            {"category_en": "Pasta", "category_ar": "باستا", "items": [
                {"name": "Mushroom Pasta", "name_ar": "باستا فطر", "price": 7.00},
                {"name": "Pesto Pasta", "name_ar": "باستا بيستو", "price": 7.00},
                {"name": "Rose Pasta", "name_ar": "باستا روز", "price": 7.00},
            ]},
            {"category_en": "Sweets", "category_ar": "حلويات", "items": [
                {"name": "Chocolate man2oshi", "name_ar": "منقوشة شوكولا", "price": 4.00},
                {"name": "Knefe Manouchi", "name_ar": "منقوشة كنافة", "price": 4.00},
                {"name": "Nuttella Pistachio Panuzzo", "name_ar": "بانوزو نوتيلا فستق", "price": 6.00},
            ]},
            {"category_en": "Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Pepsi", "name_ar": "بيبسي", "price": 1.10},
                {"name": "Water", "name_ar": "مياه", "price": 0.30},
                {"name": "Laban", "name_ar": "لبن", "price": 1.10},
            ]},
        ]
    },
    {
        "name": "PEPO'S DINER",
        "name_ar": "بيبوز داينر",
        "category": "Burgers",
        "menu": [
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "CEASAR BURGER", "price": 4.5},
                {"name": "SIMPLE CHICKEN BURGER", "price": 5.0},
                {"name": "PEPOS CHICKEN BURGER", "price": 5.0},
                {"name": "PEPOS BEEF CHEESE BURGER", "price": 5.5},
                {"name": "HONEY MUSTARD CHICKEN", "price": 5.0},
                {"name": "HONEY MUSTARD BEEF", "price": 5.5},
                {"name": "CHICKEN MUSHROOM BURGER", "price": 5.5},
                {"name": "BEEF MUSHROOM BURGER", "price": 6.0},
                {"name": "DOUBLE BEEF BURGER", "price": 7.0},
            ]},
            {"category_en": "Sandwiches", "category_ar": "ساندويشات", "items": [
                {"name": "CHICKEN CEASER", "price": 4.0},
                {"name": "TAOUK", "price": 4.0},
                {"name": "CHICKEN SUB", "price": 4.0},
                {"name": "FRANCISCO", "price": 4.0},
                {"name": "CRISPY SANDWICH", "price": 5.0},
                {"name": "FAJITA", "price": 5.0},
            ]},
            {"category_en": "Plates", "category_ar": "أطباق", "items": [
                {"name": "TWO CHICKEN BREASTS", "price": 7.0},
                {"name": "HONEY MUSTARD", "price": 7.5},
                {"name": "CRISPY PLATE", "price": 8.0},
                {"name": "MUSHROOM", "price": 9.0},
            ]},
            {"category_en": "Appetizers", "category_ar": "مقبلات", "items": [
                {"name": "FRIES", "price": 2.5},
                {"name": "LARGE FRIES", "price": 5.0},
                {"name": "CHEESY FRIES", "price": 4.0},
                {"name": "MOZZARELLA STICKS", "price": 3.5},
                {"name": "SOFT DRINK", "price": 0.8},
                {"name": "WATER", "price": 0.3},
            ]},
        ]
    },
    {
        "name": "Spuntino",
        "name_ar": "سبونتينو",
        "category": "Fried Chicken",
        "menu": [
            {"category_en": "Salad Shakers", "category_ar": "سلطات", "items": [
                {"name": "Ceasar Salad", "price": 5.00},
                {"name": "Chicken Ceaser Salad", "price": 7.50},
                {"name": "Pasta Tuna Salad", "price": 7.50},
                {"name": "Chicken Pasta Salad", "price": 7.50},
            ]},
            {"category_en": "Starters", "category_ar": "مقبلات", "items": [
                {"name": "Mozzarella Sticks", "price": 4.50},
                {"name": "Onion Rings", "price": 4.00},
                {"name": "Wedges Fries", "price": 4.00},
                {"name": "Curly Fries", "price": 4.80},
                {"name": "Wings Shaker 8 pc", "price": 7.50},
            ]},
            {"category_en": "Sandwiches", "category_ar": "ساندويشات", "items": [
                {"name": "Chicken Sub", "price": 5.50},
                {"name": "Fajitas Sandwich", "price": 7.50},
                {"name": "Francisco Sandwich", "price": 5.50},
                {"name": "Crispy Sandwich", "price": 5.50},
                {"name": "TWISTER", "price": 4.90},
            ]},
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "Hamburger", "price": 6.50},
                {"name": "Spuntino Burger", "price": 6.50},
                {"name": "Chicken Fillet", "price": 5.50},
                {"name": "Mushroom Burger", "price": 8.50},
                {"name": "Zinger", "price": 5.50},
            ]},
            {"category_en": "Fried Chicken", "category_ar": "دجاج مقلي", "items": [
                {"name": "Dinner 2 Pcs", "price": 8.50},
                {"name": "Dinner 3 Pcs", "price": 9.40},
                {"name": "Dinner 4 Pcs", "price": 10.35},
                {"name": "Dinner 9 Pcs", "price": 26.30},
                {"name": "Dinner 15 Pcs", "price": 39.90},
            ]},
            {"category_en": "Crispy", "category_ar": "كريسبي", "items": [
                {"name": "CRISPY 3 PCS", "price": 8.90},
                {"name": "CRISPY 5 PCS", "price": 10.60},
                {"name": "CRISPY 10 PCS", "price": 21.80},
                {"name": "CRISPY 15 PCS", "price": 32.50},
                {"name": "CRISPY 20 PCS", "price": 39.90},
            ]},
        ]
    },
    {
        "name": "Fayez Burger",
        "name_ar": "فايز برغر",
        "category": "Burgers",
        "menu": [
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "Classic Beef", "price": 5.5},
                {"name": "Classic Chicken", "price": 5.3},
                {"name": "Honey Mustard Chicken", "price": 5.4},
                {"name": "Honey Mustard Beef", "price": 5.6},
                {"name": "Smoke House Chicken", "price": 5.5},
                {"name": "Mushroom Chicken", "price": 5.7},
                {"name": "Mushroom Beef", "price": 5.9},
                {"name": "BBQ Chicken", "price": 5.5},
                {"name": "Truffle Chicken", "price": 6.0},
                {"name": "Truffle Beef", "price": 6.3},
                {"name": "Mini Burger", "price": 4.5},
            ]},
            {"category_en": "Sandwiches", "category_ar": "ساندويشات", "items": [
                {"name": "Tawouk", "price": 4.7},
                {"name": "Francisco", "price": 4.8},
                {"name": "Fajita", "price": 5.3},
                {"name": "Crispy", "price": 4.8},
                {"name": "Twister", "price": 5.3},
                {"name": "Chicken Sub", "price": 4.7},
                {"name": "Philadelphia Sandwich", "price": 6.0},
                {"name": "Shrimp Sandwich", "price": 6.0},
            ]},
            {"category_en": "Plates", "category_ar": "أطباق", "items": [
                {"name": "Mushroom Chicken", "price": 8.0},
                {"name": "Grilled Plate", "price": 8.0},
                {"name": "Honey Mustard", "price": 8.0},
                {"name": "Crispy Plate (5 Pcs)", "price": 8.0},
            ]},
            {"category_en": "Fries", "category_ar": "بطاطا", "items": [
                {"name": "Large Fries", "price": 4.5},
                {"name": "Small Fries", "price": 3.5},
                {"name": "Large Cheesy Fries", "price": 5.7},
                {"name": "Large Mushroom Fries", "price": 5.9},
            ]},
            {"category_en": "Soft Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Pepsi", "price": 1.0},
                {"name": "7up", "price": 1.0},
                {"name": "Mirinda", "price": 1.0},
                {"name": "Water", "price": 0.4},
            ]},
        ]
    },
    {
        "name": "Papa Joe",
        "name_ar": "بابا جو",
        "category": "Pizza",
        "menu": [
            {"category_en": "Appetizers", "category_ar": "مقبلات", "items": [
                {"name": "French Fries", "price": 3.00},
                {"name": "Fries Cheddar", "description": "French fries with cheddar cheese sauce", "price": 4.00},
                {"name": "Fries Truffle", "description": "French fries topped with sauteed fresh mushroom and truffle sauce", "price": 7.00},
                {"name": "Wings 8 pcs", "description": "Chicken wings glazed in your choice of BBQ, Buffalo or honey mustard", "price": 7.00},
                {"name": "Mozzarella Sticks", "price": 7.00},
                {"name": "Crispy Chicken", "price": 8.00},
            ]},
            {"category_en": "Salads", "category_ar": "سلطات", "items": [
                {"name": "Caesar Salad", "price": 5.00},
                {"name": "Chicken Caesar Salad", "price": 8.00},
                {"name": "Greek Salad", "price": 5.00},
                {"name": "Crab Salad", "price": 9.00},
            ]},
            {"category_en": "Chicago Pizza", "category_ar": "بيتزا شيكاغو", "items": [
                {"name": "Chicago Pepperoni", "description": "Tomato Sauce, Mozzarella, Emmental, Pepperoni, Parmesan", "price": 15.00},
                {"name": "Chicago Pesto", "description": "Pesto Sauce, Mozzarella, Emmental, Turkey, Parmesan", "price": 15.00},
                {"name": "Chicago 4 Cheese", "description": "Alfredo Sauce, Mozzarella, Provolone, Emmental, Parmesan, Turkey", "price": 15.00},
                {"name": "Chicago Truffle", "description": "Chicken, Truffle Sauce, Mozzarella, Provolone, Emmental, Parmesan, Rocca", "price": 17.00},
            ]},
            {"category_en": "Classic Pizza", "category_ar": "بيتزا كلاسيك", "items": [
                {"name": "Margarita", "price": 7.00},
                {"name": "Four Cheese", "price": 8.00},
                {"name": "Vegetarian", "price": 8.00},
                {"name": "Loaded Pizza", "price": 9.00},
                {"name": "Chicken Ranch", "price": 10.00},
            ]},
            {"category_en": "Chicken Pizza", "category_ar": "بيتزا دجاج", "items": [
                {"name": "Chicken B.B.Q", "price": 9.00},
                {"name": "Cordon Blue", "price": 10.00},
                {"name": "Teriyaki Chicken", "price": 10.00},
                {"name": "Sweet & Sour", "price": 10.00},
                {"name": "Dynamite", "price": 10.00},
                {"name": "Chicken Alfredo", "price": 10.00},
            ]},
            {"category_en": "Pasta", "category_ar": "باستا", "items": [
                {"name": "Fettuccine Chicken", "description": "Alfredo sauce, chicken, fresh mushroom & Parmesan cheese", "price": 10.00},
                {"name": "Fettuccine Shrimp", "price": 12.00},
                {"name": "Fettuccine Chicken Truffle", "price": 13.00},
                {"name": "Penne Arrabbiata", "price": 6.00},
            ]},
            {"category_en": "Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Soft Drink", "price": 1.50},
                {"name": "Water", "price": 0.50},
                {"name": "Sparkling Water", "price": 1.50},
            ]},
        ]
    },
    {
        "name": "Fahem",
        "name_ar": "فاهم",
        "category": "Grills",
        "menu": [
            {"category_en": "Appetizers & Sides", "category_ar": "مقبلات وجوانب", "items": [
                {"name": "French Fries Box", "price": 3.33},
                {"name": "Wedges Box", "price": 4.00},
                {"name": "Cheese and Fries", "price": 5.00},
                {"name": "Cheese Balls", "price": 4.00},
                {"name": "Mozzarella Sticks", "price": 4.00},
                {"name": "Hummus Plate", "price": 3.00},
                {"name": "Coleslaw Box", "price": 1.00},
            ]},
            {"category_en": "Salads", "category_ar": "سلطات", "items": [
                {"name": "Chicken Ceaser", "description": "grilled chicken, iceberg, crouton bread, parmesan cheese", "price": 6.50},
                {"name": "Fattouch", "price": 4.50},
            ]},
            {"category_en": "Sandwiches & Wraps", "category_ar": "ساندويشات وراب", "items": [
                {"name": "Djej 3al Fahem", "name_ar": "دجاج على الفحم", "description": "Charcoal grilled chicken, three flavors garlic, pickles", "price": 5.00},
                {"name": "Tawouk", "name_ar": "طاووق", "price": 5.00},
                {"name": "Kafta", "name_ar": "كفتة", "price": 5.00},
                {"name": "Makanek", "name_ar": "مقانق", "price": 5.00},
                {"name": "Fajita", "name_ar": "فاهيتا", "price": 5.56},
                {"name": "Francisco", "name_ar": "فرانسيسكو", "price": 5.56},
                {"name": "Chicken Sub", "name_ar": "تشيكن ساب", "price": 5.56},
                {"name": "Twister", "name_ar": "تويستر", "price": 6.00},
                {"name": "Zinger", "name_ar": "زنجر", "price": 7.50},
            ]},
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "American Burger", "price": 5.50},
                {"name": "Lebanese Burger", "price": 5.00},
                {"name": "Chicken Burger", "price": 4.50},
                {"name": "BBQ Burger", "price": 6.50},
                {"name": "Crunchy BBQ", "price": 7.00},
            ]},
            {"category_en": "Chicken & Grill Meals", "category_ar": "وجبات دجاج ومشاوي", "items": [
                {"name": "Half Farrouj 3al Fa7em", "name_ar": "نص فروج على الفحم", "price": 7.78},
                {"name": "Farrouj 3al Fa7em", "name_ar": "فروج على الفحم", "price": 15.56},
                {"name": "Tawouk Meal", "name_ar": "وجبة طاووق", "price": 12.00},
            ]},
            {"category_en": "Broasted & Wings", "category_ar": "بروستد وأجنحة", "items": [
                {"name": "Broasted Wings (8 piece)", "price": 5.00},
                {"name": "Buffalo Broasted Wings (8 piece)", "price": 5.00},
                {"name": "Broasted Chicken Meal – 4 Pcs", "price": 12.22},
                {"name": "Crispy Meal – 5 Pcs", "price": 11.67},
            ]},
            {"category_en": "Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Soft Drink", "price": 1.00},
                {"name": "Water 500ml", "price": 0.56},
                {"name": "Laban Ayran", "price": 1.00},
            ]},
        ]
    },
    {
        "name": "Linguine",
        "name_ar": "لينغويني",
        "category": "Pasta",
        "menu": [
            {"category_en": "Pasta", "category_ar": "باستا", "items": [
                {"name": "Fettuccine Alfredo", "price": 7.5},
                {"name": "Chicken Rose", "price": 8.0},
                {"name": "Chicken Curry", "price": 7.5},
                {"name": "Mac & cheese", "price": 6.5},
                {"name": "Lasagna", "price": 7.5},
                {"name": "Shrimp Rose", "price": 9.0},
                {"name": "Shrimp fettuccine", "price": 8.5},
            ]},
            {"category_en": "Wraps", "category_ar": "راب", "items": [
                {"name": "Double B", "price": 6.5},
                {"name": "Steak Betello", "price": 5.0},
                {"name": "Zinger", "price": 6.0},
                {"name": "Twister", "price": 5.5},
            ]},
            {"category_en": "Appetizers", "category_ar": "مقبلات", "items": [
                {"name": "Loaded Fries", "price": 7.0},
                {"name": "Mozzarella sticks", "price": 4.0},
                {"name": "Curly Fries", "price": 5.5},
                {"name": "Cheese Fries", "price": 5.0},
                {"name": "Fries", "price": 3.5},
                {"name": "Alfredo Fries", "price": 7.5},
            ]},
            {"category_en": "Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Soft Drinks", "price": 1.0},
                {"name": "Sparkling Water", "price": 1.0},
                {"name": "Water", "price": 0.5},
            ]},
        ]
    },
    {
        "name": "Senor Pizza",
        "name_ar": "سنيور بيتزا",
        "category": "Pizza",
        "menu": [
            {"category_en": "Delux Pizza", "category_ar": "بيتزا ديلوكس", "items": [
                {"name": "Vegeterian", "has_variants": True, "variants": [
                    {"name": "Small 25 cm", "price": 7.50},
                    {"name": "Medium 30 cm", "price": 9.50},
                    {"name": "Large 35 cm", "price": 11.50},
                    {"name": "X-Large 40 cm", "price": 14.50},
                ]},
                {"name": "Greek", "has_variants": True, "variants": [
                    {"name": "Small 25 cm", "price": 7.50},
                    {"name": "Medium 30 cm", "price": 9.50},
                    {"name": "Large 35 cm", "price": 11.50},
                    {"name": "X-Large 40 cm", "price": 14.50},
                ]},
                {"name": "Margherita", "has_variants": True, "variants": [
                    {"name": "Small 25 cm", "price": 7.50},
                    {"name": "Medium 30 cm", "price": 9.50},
                    {"name": "Large 35 cm", "price": 11.50},
                    {"name": "X-Large 40 cm", "price": 14.50},
                ]},
            ]},
            {"category_en": "Premium Chicken Pizza", "category_ar": "بيتزا دجاج بريميوم", "items": [
                {"name": "Four Cheese", "has_variants": True, "variants": [
                    {"name": "Small 25 cm", "price": 10.00},
                    {"name": "Medium 30 cm", "price": 13.00},
                    {"name": "Large 35 cm", "price": 15.00},
                    {"name": "X-Large 40 cm", "price": 18.00},
                ]},
                {"name": "Pepperoni", "has_variants": True, "variants": [
                    {"name": "Small 25 cm", "price": 10.00},
                    {"name": "Medium 30 cm", "price": 13.00},
                    {"name": "Large 35 cm", "price": 15.00},
                    {"name": "X-Large 40 cm", "price": 18.00},
                ]},
                {"name": "Chicken Fajita", "has_variants": True, "variants": [
                    {"name": "Small 25 cm", "price": 10.00},
                    {"name": "Medium 30 cm", "price": 13.00},
                    {"name": "Large 35 cm", "price": 15.00},
                    {"name": "X-Large 40 cm", "price": 18.00},
                ]},
                {"name": "BBQ Chicken", "has_variants": True, "variants": [
                    {"name": "Small 25 cm", "price": 10.00},
                    {"name": "Medium 30 cm", "price": 13.00},
                    {"name": "Large 35 cm", "price": 15.00},
                    {"name": "X-Large 40 cm", "price": 18.00},
                ]},
            ]},
            {"category_en": "Penne Pasta", "category_ar": "باستا بيني", "items": [
                {"name": "AlFredo Al Forno - Chicken", "has_variants": True, "variants": [
                    {"name": "Grand", "price": 9.50},
                    {"name": "Multi-Grand", "price": 13.00},
                ]},
                {"name": "La Rosa - Chicken", "has_variants": True, "variants": [
                    {"name": "Grand", "price": 9.50},
                    {"name": "Multi-Grand", "price": 13.00},
                ]},
                {"name": "Four Cheese - Chicken", "has_variants": True, "variants": [
                    {"name": "Grand", "price": 9.50},
                    {"name": "Multi-Grand", "price": 13.00},
                ]},
            ]},
            {"category_en": "Appetizers", "category_ar": "مقبلات", "items": [
                {"name": "Fries", "price": 3.00},
                {"name": "Twisted Fries (Curly Fries)", "price": 6.00},
                {"name": "Wedges", "price": 4.00},
                {"name": "Truffle Fries", "price": 7.00},
                {"name": "Mozzarella Sticks (6 Pcs)", "price": 6.00},
                {"name": "Crispy Chicken Tenders (5 Pcs)", "price": 7.00},
                {"name": "Chicken Wings (6 Pcs)", "price": 8.00},
            ]},
            {"category_en": "Burgers", "category_ar": "برغر", "items": [
                {"name": "Classic Chicken Burger", "price": 7.00},
                {"name": "Classic Beef Burger", "price": 7.00},
                {"name": "Zinger Burger", "price": 7.00},
                {"name": "Alfredo Burger", "price": 7.00},
                {"name": "Senor Special Burger", "price": 7.00},
            ]},
            {"category_en": "Drinks", "category_ar": "مشروبات", "items": [
                {"name": "Small Water", "price": 0.50},
                {"name": "Soft Drink (330ml)", "price": 1.50},
                {"name": "Kinza", "price": 1.00},
                {"name": "Sparkling Water", "price": 2.00},
            ]},
        ]
    },
    {
        "name": "Sahha w Hana",
        "name_ar": "صحة وهنا",
        "category": "Lebanese",
        "menu": [
            {"category_en": "Meals (Al Wajbat)", "category_ar": "الوجبات", "items": [
                {"name": "1kg Cooked Fawaregh", "name_ar": "كيلو فوارغ مطبوخ", "price": 20},
                {"name": "0.5kg Cooked Fawaregh", "name_ar": "نص كيلو فوارغ مطبوخ", "price": 10},
                {"name": "Kura'in Meal", "name_ar": "وجبة كراعين", "price": 10},
                {"name": "Ras Nifa", "name_ar": "راس نيفا", "price": 15},
                {"name": "Veal Meat Mansaf (5 Persons)", "name_ar": "منسف لحمة عجل 5 أشخاص", "price": 35},
                {"name": "Lamb Meat Mansaf (5 Persons)", "name_ar": "منسف لحمة غنم 5 أشخاص", "price": 45},
                {"name": "Chicken Kabsa (5 Persons)", "name_ar": "كبسة دجاج 5 أشخاص", "price": 30},
                {"name": "1kg Cooked Grape Leaves with Meat", "name_ar": "كيلو ورق بلحمة مطبوخ", "price": 20},
                {"name": "1kg Cooked Grape Leaves with Oil", "name_ar": "كيلو ورق بزيت مطبوخ", "price": 12},
                {"name": "1kg Cabbage (Malfouf)", "name_ar": "كيلو ملفوف", "price": 10},
            ]},
            {"category_en": "Frozen Items (Al Mufarrazat)", "category_ar": "المفرزات", "items": [
                {"name": "Dozen Kibbeh", "name_ar": "دزينة الكبة", "price": 8},
                {"name": "Dozen Cheese Sambousek", "name_ar": "دزينة سمبوسك جبنة", "price": 6},
                {"name": "Dozen Meat Sambousek", "name_ar": "دزينة سمبوسك لحمة", "price": 7},
                {"name": "Dozen Cheese Rolls (Rakakat)", "name_ar": "دزينة رقاقات جبنة", "price": 5},
                {"name": "Dozen Meat Rolls (Rakakat)", "name_ar": "دزينة رقاقات لحمة", "price": 6},
                {"name": "1kg Grape Leaves with Oil", "name_ar": "كيلو ورق بزيت", "price": 10},
                {"name": "1kg Grape Leaves with Meat", "name_ar": "كيلو ورق بلحمة", "price": 15},
            ]},
        ]
    },
]

# Category mappings - matching the database categories
CATEGORY_MAP = {
    "Bakery": "Manakish",  # Map bakery items to Manakish
    "Sandwiches": "Sandwiches",
    "Breakfast": "Breakfast",
    "Burgers": "Sandwiches",  # No Burgers category, use Sandwiches
    "Pizza": "Pizza",
    "Fried Chicken": "Sandwiches",  # No Fried Chicken, use Sandwiches
    "Grills": "Grills",
    "Pasta": "Sandwiches",  # No Pasta category, use Sandwiches
    "Lebanese": "Home Food",
}


async def get_category(session, cat_key: str):
    """Get restaurant category from database"""
    cat_name = CATEGORY_MAP.get(cat_key, "Sandwiches")

    result = await session.execute(
        select(RestaurantCategory).where(RestaurantCategory.name == cat_name)
    )
    cat = result.scalars().first()
    return cat


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
                category_id=category.id,
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
                    name=cat_data.get("category_en", cat_data.get("category", "Other")),
                    name_ar=cat_data.get("category_ar"),
                    order=cat_order
                )
                session.add(menu_category)
                await session.flush()

                # Create items
                for item_order, item_data in enumerate(cat_data.get("items", [])):
                    has_variants = item_data.get("has_variants", False)
                    variants_data = item_data.get("variants", [])

                    # Calculate price range for variant items
                    if has_variants and variants_data:
                        prices = [v["price"] for v in variants_data]
                        price_min = min(prices)
                        price_max = max(prices)
                        price = None
                    else:
                        price = item_data.get("price")
                        price_min = None
                        price_max = None

                    menu_item = MenuItem(
                        category_id=menu_category.id,
                        name=item_data.get("name", item_data.get("name_ar", "")),
                        name_ar=item_data.get("name_ar"),
                        description=item_data.get("description"),
                        price=price,
                        price_min=price_min,
                        price_max=price_max,
                        has_variants=has_variants,
                        is_available=True,
                        order=item_order
                    )
                    session.add(menu_item)
                    await session.flush()

                    # Create variants if any
                    if has_variants and variants_data:
                        for var_order, var_data in enumerate(variants_data):
                            variant = MenuItemVariant(
                                menu_item_id=menu_item.id,
                                name=var_data["name"],
                                price=var_data["price"],
                                order=var_order
                            )
                            session.add(variant)

            print(f"  ✓ Created {rest_data['name']}")

        await session.commit()
        print("\n✅ All restaurants imported successfully!")


if __name__ == "__main__":
    asyncio.run(import_restaurants())
