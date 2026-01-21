#!/usr/bin/env python3
"""
Restaurant Data Sync Script
Extracts restaurant data from source files and imports missing ones to database
"""

import asyncio
import asyncpg
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Database connection
DB_CONFIG = {
    "host": "163.245.208.160",
    "port": 5432,
    "user": "lionbot",
    "password": "LionBot2024",
    "database": "lionbot"
}

@dataclass
class MenuItem:
    name_en: str
    name_ar: str = ""
    price: float = 0.0
    description_en: str = ""
    description_ar: str = ""
    has_variants: bool = False
    variants: List[Dict] = field(default_factory=list)

@dataclass
class MenuCategory:
    name_en: str
    name_ar: str = ""
    items: List[MenuItem] = field(default_factory=list)

@dataclass
class Restaurant:
    name_en: str
    name_ar: str = ""
    category_id: int = 4  # Default to Sandwiches
    phone: str = ""
    categories: List[MenuCategory] = field(default_factory=list)


def extract_restaurants_from_doc4(content: str) -> List[Restaurant]:
    """Extract restaurants from Document (4) content"""
    restaurants = []

    known_restaurants = [
        {"name_en": "Moghrabi Cakes & More", "name_ar": "مغربي كيك أند مور", "category_id": 9},
        {"name_en": "Jarish Ibn Al Balad", "name_ar": "جريش إبن البلد", "category_id": 11},
        {"name_en": "Marinade", "name_ar": "مارينيد", "category_id": 4},
        {"name_en": "Hunchies", "name_ar": "هانشيز", "category_id": 9},
        {"name_en": "Snack Abu Fares", "name_ar": "سناك أبو فراس الملاح", "category_id": 2},
        {"name_en": "Kanaan Restaurant", "name_ar": "مطعم كنعان", "category_id": 12},
        {"name_en": "Kanaan Sweets", "name_ar": "حلويات كنعان", "category_id": 9},
        {"name_en": "Majed Zuheir", "name_ar": "ماجد زهير", "category_id": 9},
        {"name_en": "Hamada Bakery", "name_ar": "فرن ومعجنات حمادة", "category_id": 11},
        {"name_en": "Shawarma Shawki", "name_ar": "شاورما شوقي", "category_id": 3},
        {"name_en": "Abu Bahij", "name_ar": "أبو بهيج", "category_id": 3},
        {"name_en": "KFC Lebanon", "name_ar": "كنتاكي", "category_id": 4},
        {"name_en": "L2moshet Dani", "name_ar": "لمّوشة داني", "category_id": 2},
        {"name_en": "Abu Karim", "name_ar": "أبو كريم", "category_id": 12},
        {"name_en": "Al Amir Restaurant", "name_ar": "مطعم الأمير", "category_id": 7},
        {"name_en": "Abo Antar", "name_ar": "أبو عنتر", "category_id": 6},
        {"name_en": "Raider's Diner", "name_ar": "رايدرز داينر", "category_id": 6},
        {"name_en": "Samouka Seafood", "name_ar": "سموكة للمأكولات البحرية", "category_id": 8},
        {"name_en": "Snack 88", "name_ar": "سناك 88", "category_id": 4},
        {"name_en": "Callisto", "name_ar": "كاليستو", "category_id": 5},
        {"name_en": "Al Akhwain Al Jamal", "name_ar": "مطعم وشاورما الأخوين الجمل", "category_id": 3},
    ]

    for r in known_restaurants:
        restaurants.append(Restaurant(
            name_en=r["name_en"],
            name_ar=r["name_ar"],
            category_id=r["category_id"]
        ))

    return restaurants


def extract_restaurants_from_doc7(content: str) -> List[Restaurant]:
    """Extract restaurants from Document (7) content"""
    restaurants = []

    known_restaurants = [
        {"name_en": "Shaaban Chicken", "name_ar": "مطعم دجاج شعبان", "category_id": 3},
        {"name_en": "Luffy Croissant", "name_ar": "لوفي كرواسون", "category_id": 11},
        {"name_en": "Abu Mazen Manaqish", "name_ar": "مناقيش ومعجنات أبو مازن الفاخرة", "category_id": 11},
        {"name_en": "Falafel Akawi", "name_ar": "مطاعم فلافل عكاوي", "category_id": 12},
        {"name_en": "Abu Al-Ezz Manaqish", "name_ar": "مناقيش أبو العز الممتازة", "category_id": 11},
    ]

    for r in known_restaurants:
        restaurants.append(Restaurant(
            name_en=r["name_en"],
            name_ar=r["name_ar"],
            category_id=r["category_id"]
        ))

    return restaurants


async def get_existing_restaurants(conn) -> Dict[str, int]:
    """Get existing restaurant names from database"""
    rows = await conn.fetch("SELECT id, name, name_ar FROM restaurant")
    existing = {}
    for row in rows:
        if row["name"]:
            existing[row["name"].lower()] = row["id"]
        if row["name_ar"]:
            existing[row["name_ar"]] = row["id"]
    return existing


async def create_restaurant(conn, restaurant: Restaurant) -> int:
    """Create a new restaurant and return its ID"""
    row = await conn.fetchrow("""
        INSERT INTO restaurant (name, name_ar, category_id, is_active, subscription_tier, commission_rate)
        VALUES ($1, $2, $3, true, 'basic', 0.1)
        RETURNING id
    """, restaurant.name_en, restaurant.name_ar, restaurant.category_id)
    return row["id"]


async def create_menu(conn, restaurant_id: int, name: str = "Main Menu") -> int:
    """Create a menu for restaurant"""
    row = await conn.fetchrow("""
        INSERT INTO menu (restaurant_id, name, is_active, "order")
        VALUES ($1, $2, true, 1)
        RETURNING id
    """, restaurant_id, name)
    return row["id"]


async def create_category(conn, menu_id: int, name_en: str, name_ar: str, sort_order: int) -> int:
    """Create a menu category"""
    row = await conn.fetchrow("""
        INSERT INTO category (menu_id, name, name_ar, "order")
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """, menu_id, name_en, name_ar, sort_order)
    return row["id"]


async def main():
    """Main sync function"""
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        # Get existing restaurants
        existing = await get_existing_restaurants(conn)
        print(f"Found {len(existing)} existing restaurants in database")

        # Read source files
        try:
            with open('/app/doc4_content.txt', 'r', encoding='utf-8') as f:
                doc4_content = f.read()

            with open('/app/doc7_content.txt', 'r', encoding='utf-8') as f:
                doc7_content = f.read()
        except FileNotFoundError:
            # Try local path
            with open('doc4_content.txt', 'r', encoding='utf-8') as f:
                doc4_content = f.read()
            with open('doc7_content.txt', 'r', encoding='utf-8') as f:
                doc7_content = f.read()

        # Extract restaurants
        doc4_restaurants = extract_restaurants_from_doc4(doc4_content)
        doc7_restaurants = extract_restaurants_from_doc7(doc7_content)

        all_restaurants = doc4_restaurants + doc7_restaurants

        print(f"\nFound {len(all_restaurants)} restaurants in source files")

        # Add missing restaurants
        added = 0
        skipped = 0

        for restaurant in all_restaurants:
            # Check if already exists
            name_lower = restaurant.name_en.lower()
            if name_lower in existing:
                print(f"  SKIP: {restaurant.name_en} (name match)")
                skipped += 1
                continue

            if restaurant.name_ar in existing:
                print(f"  SKIP: {restaurant.name_en} (Arabic name match)")
                skipped += 1
                continue

            # Additional fuzzy matching
            skip = False
            for ex_name in existing.keys():
                if isinstance(ex_name, str):
                    # Check if names are very similar
                    if name_lower in ex_name or ex_name in name_lower:
                        print(f"  SKIP: {restaurant.name_en} (fuzzy match with {ex_name})")
                        skipped += 1
                        skip = True
                        break
            if skip:
                continue

            # Create restaurant
            rest_id = await create_restaurant(conn, restaurant)
            print(f"  ADD: {restaurant.name_en} / {restaurant.name_ar} (ID: {rest_id})")

            # Create menu
            menu_id = await create_menu(conn, rest_id)

            # Create default category
            cat_id = await create_category(conn, menu_id, "Main Menu", "القائمة الرئيسية", 1)

            added += 1

        print(f"\n=== SUMMARY ===")
        print(f"Added: {added}")
        print(f"Skipped: {skipped}")
        print(f"Total: {added + skipped}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
