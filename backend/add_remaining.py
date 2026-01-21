#!/usr/bin/env python3
"""
Add remaining restaurants that were skipped incorrectly
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

# Restaurants that were incorrectly skipped
remaining = [
    {"name_en": "Kanaan Restaurant", "name_ar": "مطعم كنعان", "category_id": 12},
    {"name_en": "Al Amir Restaurant", "name_ar": "مطعم الأمير", "category_id": 7},
]


async def main():
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        for r in remaining:
            # Check if truly doesn't exist
            exists = await conn.fetchval(
                "SELECT id FROM restaurant WHERE name = $1", r["name_en"]
            )
            if exists:
                print(f"SKIP: {r['name_en']} already exists (ID: {exists})")
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

        # Final count
        count = await conn.fetchval("SELECT COUNT(*) FROM restaurant")
        print(f"\n=== TOTAL RESTAURANTS NOW: {count} ===")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
