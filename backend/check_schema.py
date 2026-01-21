#!/usr/bin/env python3
import asyncio
import asyncpg

async def check_schema():
    conn = await asyncpg.connect(
        host="163.245.208.160",
        port=5432,
        user="lionbot",
        password="LionBot2024",
        database="lionbot"
    )

    # Get restaurant table columns
    columns = await conn.fetch("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'restaurant'
        ORDER BY ordinal_position
    """)

    print("=== RESTAURANT TABLE SCHEMA ===")
    for c in columns:
        print(f"  {c['column_name']}: {c['data_type']} (nullable: {c['is_nullable']})")

    # Get menu table columns
    columns = await conn.fetch("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'menu'
        ORDER BY ordinal_position
    """)

    print("\n=== MENU TABLE SCHEMA ===")
    for c in columns:
        print(f"  {c['column_name']}: {c['data_type']} (nullable: {c['is_nullable']})")

    # Get category table columns
    columns = await conn.fetch("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'category'
        ORDER BY ordinal_position
    """)

    print("\n=== CATEGORY TABLE SCHEMA ===")
    for c in columns:
        print(f"  {c['column_name']}: {c['data_type']} (nullable: {c['is_nullable']})")

    # Get menuitem table columns
    columns = await conn.fetch("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'menuitem'
        ORDER BY ordinal_position
    """)

    print("\n=== MENUITEM TABLE SCHEMA ===")
    for c in columns:
        print(f"  {c['column_name']}: {c['data_type']} (nullable: {c['is_nullable']})")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_schema())
