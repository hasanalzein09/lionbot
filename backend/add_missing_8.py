#!/usr/bin/env python3
"""
Add the 8 missing restaurants identified from source files
"""
import asyncio
import asyncpg

DB_CONFIG = {
    "host": "163.245.208.160",
    "port": 5432,
    "user": "lionbot",
    "password": "LionBot2024",
    "database": "lionbot"
}

# Missing restaurants to add
missing_restaurants = [
    {"name_en": "Abo Malek", "name_ar": "أبو مالك", "category_id": 4},
    {"name_en": "Boneless House", "name_ar": "بونلس هاوس", "category_id": 3},
    {"name_en": "Farrouj Shahine", "name_ar": "فروج شاهين", "category_id": 3},
    {"name_en": "Malak Al Moaajinat Bakery", "name_ar": "ملك المعجنات", "category_id": 11},
    {"name_en": "Sandwich Farid", "name_ar": "ساندويش فريد", "category_id": 4},
    {"name_en": "Sofret Amal", "name_ar": "سفرة أمل", "category_id": 7},
    {"name_en": "Soubra's", "name_ar": "صبرا", "category_id": 4},
    {"name_en": "fared", "name_ar": "فارد", "category_id": 4},
]


async def main():
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        added = 0
        skipped = 0

        for r in missing_restaurants:
            # Check if already exists
            exists = await conn.fetchval(
                "SELECT id FROM restaurant WHERE LOWER(name) = LOWER($1)",
                r["name_en"]
            )
            if exists:
                print(f"SKIP: {r['name_en']} already exists (ID: {exists})")
                skipped += 1
                continue

            # Create restaurant
            row = await conn.fetchrow("""
                INSERT INTO restaurant (name, name_ar, category_id, is_active, subscription_tier, commission_rate)
                VALUES ($1, $2, $3, true, 'basic', 0.1)
                RETURNING id
            """, r["name_en"], r["name_ar"], r["category_id"])
            rest_id = row["id"]
            print(f"ADD: {r['name_en']} / {r['name_ar']} (ID: {rest_id})")

            # Create menu
            menu_row = await conn.fetchrow("""
                INSERT INTO menu (restaurant_id, name, is_active, "order")
                VALUES ($1, 'Main Menu', true, 1)
                RETURNING id
            """, rest_id)
            menu_id = menu_row["id"]

            # Create default category
            await conn.execute("""
                INSERT INTO category (menu_id, name, name_ar, "order")
                VALUES ($1, 'Main Menu', 'القائمة الرئيسية', 1)
            """, menu_id)

            added += 1

        # Final count
        count = await conn.fetchval("SELECT COUNT(*) FROM restaurant")

        print(f"\n=== SUMMARY ===")
        print(f"Added: {added}")
        print(f"Skipped: {skipped}")
        print(f"Total restaurants now: {count}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
