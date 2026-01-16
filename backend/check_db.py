
import asyncio
from sqlalchemy import text
from app.db.session import engine

async def check_db():
    print("Checking columns...")
    try:
        async with engine.connect() as conn:
            # Check user table
            res = await conn.execute(text("SELECT * FROM \"user\" LIMIT 1"))
            print(f"User columns: {res.keys()}")
            
            # Check menu table
            res = await conn.execute(text("SELECT * FROM menu LIMIT 1"))
            print(f"Menu columns: {res.keys()}")
            
            # Check category table
            res = await conn.execute(text("SELECT * FROM category LIMIT 1"))
            print(f"Category columns: {res.keys()}")
            
            # Check menuitem table
            res = await conn.execute(text("SELECT * FROM menuitem LIMIT 1"))
            print(f"MenuItem columns: {res.keys()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
