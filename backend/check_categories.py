#!/usr/bin/env python3
import asyncio
import asyncpg

async def check_categories():
    conn = await asyncpg.connect(
        host="163.245.208.160",
        port=5432,
        user="lionbot",
        password="LionBot2024",
        database="lionbot"
    )

    categories = await conn.fetch("SELECT * FROM restaurant_category ORDER BY id")
    print("=== RESTAURANT CATEGORIES ===")
    for c in categories:
        print(f"  {c['id']}: {c['name']} / {c.get('name_ar', '')}")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_categories())
