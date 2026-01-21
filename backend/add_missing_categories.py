#!/usr/bin/env python3
import asyncio
import asyncpg

async def add_categories():
    conn = await asyncpg.connect(
        host="163.245.208.160",
        port=5432,
        user="lionbot",
        password="LionBot2024",
        database="lionbot"
    )

    # Add missing categories
    missing = [
        (2, "Snacks", "سناك"),
        (6, "Burgers", "برغر"),
    ]

    for cat_id, name, name_ar in missing:
        try:
            await conn.execute("""
                INSERT INTO restaurant_category (id, name, name_ar)
                VALUES ($1, $2, $3)
            """, cat_id, name, name_ar)
            print(f"Added category {cat_id}: {name} / {name_ar}")
        except Exception as e:
            print(f"Error adding category {cat_id}: {e}")

    # Verify
    categories = await conn.fetch("SELECT * FROM restaurant_category ORDER BY id")
    print("\n=== ALL CATEGORIES NOW ===")
    for c in categories:
        print(f"  {c['id']}: {c['name']} / {c.get('name_ar', '')}")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(add_categories())
