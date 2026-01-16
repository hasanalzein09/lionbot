"""Script to clean up all restaurants and related data"""
import asyncio
from sqlalchemy import text
from app.db.session import async_engine

async def cleanup():
    async with async_engine.begin() as conn:
        # Delete in order of dependencies
        print("Deleting order_items...")
        await conn.execute(text("DELETE FROM order_items"))

        print("Deleting orders...")
        await conn.execute(text("DELETE FROM orders"))

        print("Deleting menu_items...")
        await conn.execute(text("DELETE FROM menu_items"))

        print("Deleting categories...")
        await conn.execute(text("DELETE FROM categories"))

        print("Deleting menus...")
        await conn.execute(text("DELETE FROM menus"))

        print("Deleting restaurants...")
        await conn.execute(text("DELETE FROM restaurants"))

        print("Done! All restaurants and related data deleted.")

if __name__ == "__main__":
    asyncio.run(cleanup())
