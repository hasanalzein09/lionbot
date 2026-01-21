#!/usr/bin/env python3
import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect(
        host="163.245.208.160",
        port=5432,
        user="lionbot",
        password="LionBot2024",
        database="lionbot"
    )
    rows = await conn.fetch("SELECT id, name, name_ar FROM restaurant ORDER BY id")
    print(f"Total: {len(rows)}")
    for row in rows:
        name = row["name"] or ""
        name_ar = row["name_ar"] or ""
        print(f"{row['id']:3}. {name} | {name_ar}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
