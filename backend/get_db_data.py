#!/usr/bin/env python3
import asyncio
import asyncpg
import json

async def get_db_data():
    conn = await asyncpg.connect(
        host="163.245.208.160",
        port=5432,
        user="lionbot",
        password="LionBot2024",
        database="lionbot"
    )

    # Get categories
    categories = await conn.fetch("SELECT * FROM restaurant_category ORDER BY id")
    print("=== RESTAURANT CATEGORIES ===")
    for c in categories:
        cid = c["id"]
        name = c["name"]
        name_ar = c.get("name_ar", "")
        print(f"{cid}|{name}|{name_ar}")

    # Get restaurants count
    count = await conn.fetchval("SELECT COUNT(*) FROM restaurant")
    print(f"\n=== TOTAL RESTAURANTS: {count} ===")

    # Get all restaurants
    restaurants = await conn.fetch("SELECT id, name, name_ar, category_id FROM restaurant ORDER BY id")
    print("\n=== RESTAURANTS ===")
    for r in restaurants:
        rid = r["id"]
        name = r["name"] or ""
        name_ar = r["name_ar"] or ""
        cat_id = r["category_id"]
        print(f"{rid}|{name}|{name_ar}|{cat_id}")

    # Get menu items count
    item_count = await conn.fetchval("SELECT COUNT(*) FROM menuitem")
    print(f"\n=== TOTAL MENU ITEMS: {item_count} ===")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(get_db_data())
