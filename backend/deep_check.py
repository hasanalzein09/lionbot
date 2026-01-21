#!/usr/bin/env python3
"""Deep database price check"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Direct connection
DATABASE_URL = "postgresql+asyncpg://lionbot:LionBot2024@163.245.208.160:5432/lionbot"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def deep_check():
    async with AsyncSessionLocal() as session:
        print("=" * 70)
        print("🔍 DEEP DATABASE PRICE ANALYSIS")
        print("=" * 70)
        
        # 1. Items without prices AND without variants
        print("\n📌 1. Menu Items WITHOUT prices (and no variants):")
        result = await session.execute(text("""
            SELECT r.name as restaurant, c.name as category, mi.name, mi.name_ar, mi.has_variants
            FROM menuitem mi
            JOIN category c ON mi.category_id = c.id
            JOIN menu m ON c.menu_id = m.id
            JOIN restaurant r ON m.restaurant_id = r.id
            WHERE mi.price IS NULL AND mi.has_variants = FALSE
            ORDER BY r.name
        """))
        rows = result.fetchall()
        if rows:
            print(f"   ❌ Found {len(rows)} items without prices:")
            for row in rows:
                print(f"      • {row[0]} > {row[1]} > {row[2]} ({row[3]})")
        else:
            print("   ✅ All items have prices or variants")
        
        # 2. Items with suspiciously HIGH prices (might be LBP)
        print("\n📌 2. Items with HIGH prices (> $50 - might be LBP):")
        result = await session.execute(text("""
            SELECT r.name, mi.name, mi.name_ar, mi.price
            FROM menuitem mi
            JOIN category c ON mi.category_id = c.id
            JOIN menu m ON c.menu_id = m.id
            JOIN restaurant r ON m.restaurant_id = r.id
            WHERE mi.price > 50
            ORDER BY mi.price DESC
        """))
        rows = result.fetchall()
        if rows:
            print(f"   ⚠️ Found {len(rows)} items with high prices:")
            for row in rows:
                print(f"      • {row[0]}: {row[1]} ({row[2]}) = ${row[3]}")
        else:
            print("   ✅ No suspiciously high prices")
        
        # 3. Items with very LOW prices (might be wrong)
        print("\n📌 3. Items with very LOW prices (< $0.50):")
        result = await session.execute(text("""
            SELECT r.name, mi.name, mi.name_ar, mi.price
            FROM menuitem mi
            JOIN category c ON mi.category_id = c.id
            JOIN menu m ON c.menu_id = m.id
            JOIN restaurant r ON m.restaurant_id = r.id
            WHERE mi.price < 0.50 AND mi.price > 0
            ORDER BY mi.price ASC
        """))
        rows = result.fetchall()
        if rows:
            print(f"   📋 Found {len(rows)} items with low prices:")
            for row in rows[:15]:
                print(f"      • {row[0]}: {row[1]} ({row[2]}) = ${row[3]}")
            if len(rows) > 15:
                print(f"      ... and {len(rows) - 15} more")
        else:
            print("   ✅ No very low prices")
        
        # 4. Variants without prices
        print("\n📌 4. Variants WITHOUT prices:")
        result = await session.execute(text("""
            SELECT r.name, mi.name, v.name as variant_name, v.price
            FROM menuitemvariant v
            JOIN menuitem mi ON v.menu_item_id = mi.id
            JOIN category c ON mi.category_id = c.id
            JOIN menu m ON c.menu_id = m.id
            JOIN restaurant r ON m.restaurant_id = r.id
            WHERE v.price IS NULL OR v.price = 0
        """))
        rows = result.fetchall()
        if rows:
            print(f"   ❌ Found {len(rows)} variants without prices:")
            for row in rows:
                print(f"      • {row[0]}: {row[1]} > {row[2]}")
        else:
            print("   ✅ All variants have prices")
        
        # 5. Variants with high prices
        print("\n📌 5. Variants with HIGH prices (> $50):")
        result = await session.execute(text("""
            SELECT r.name, mi.name, v.name as variant_name, v.price
            FROM menuitemvariant v
            JOIN menuitem mi ON v.menu_item_id = mi.id
            JOIN category c ON mi.category_id = c.id
            JOIN menu m ON c.menu_id = m.id
            JOIN restaurant r ON m.restaurant_id = r.id
            WHERE v.price > 50
            ORDER BY v.price DESC
        """))
        rows = result.fetchall()
        if rows:
            print(f"   ⚠️ Found {len(rows)} variants with high prices:")
            for row in rows:
                print(f"      • {row[0]}: {row[1]} > {row[2]} = ${row[3]}")
        else:
            print("   ✅ No high variant prices")
        
        # 6. Price Distribution
        print("\n📌 6. PRICE DISTRIBUTION:")
        result = await session.execute(text("""
            SELECT 
                CASE 
                    WHEN price < 1 THEN '< $1'
                    WHEN price < 5 THEN '$1 - $5'
                    WHEN price < 10 THEN '$5 - $10'
                    WHEN price < 20 THEN '$10 - $20'
                    WHEN price < 50 THEN '$20 - $50'
                    ELSE '> $50'
                END as price_range,
                COUNT(*) as count
            FROM menuitem
            WHERE price IS NOT NULL
            GROUP BY 1
            ORDER BY MIN(price)
        """))
        rows = result.fetchall()
        print("   Price Range    | Count")
        print("   " + "-" * 25)
        for row in rows:
            print(f"   {row[0]:14} | {row[1]}")
        
        # 7. Overall Statistics
        print("\n📌 7. OVERALL STATISTICS:")
        result = await session.execute(text("""
            SELECT 
                COUNT(*) as total_items,
                COUNT(price) as items_with_price,
                COUNT(*) - COUNT(price) as items_without_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                ROUND(AVG(price)::numeric, 2) as avg_price
            FROM menuitem
        """))
        stats = result.fetchone()
        print(f"   • Total menu items: {stats[0]}")
        print(f"   • Items with price: {stats[1]}")
        print(f"   • Items without price: {stats[2]}")
        print(f"   • Min price: ${stats[3]}")
        print(f"   • Max price: ${stats[4]}")
        print(f"   • Avg price: ${stats[5]}")
        
        # Variant stats
        result = await session.execute(text("""
            SELECT COUNT(*), MIN(price), MAX(price), ROUND(AVG(price)::numeric, 2)
            FROM menuitemvariant
        """))
        var_stats = result.fetchone()
        print(f"\n   • Total variants: {var_stats[0]}")
        print(f"   • Variant min: ${var_stats[1]}")
        print(f"   • Variant max: ${var_stats[2]}")
        print(f"   • Variant avg: ${var_stats[3]}")
        
        # 8. Check for LBP-like prices (thousands)
        print("\n📌 8. CHECK FOR LBP PRICES (> 1000):")
        result = await session.execute(text("""
            SELECT r.name, mi.name, mi.price
            FROM menuitem mi
            JOIN category c ON mi.category_id = c.id
            JOIN menu m ON c.menu_id = m.id
            JOIN restaurant r ON m.restaurant_id = r.id
            WHERE mi.price > 1000
        """))
        rows = result.fetchall()
        if rows:
            print(f"   🚨 FOUND {len(rows)} items that might be in LBP:")
            for row in rows:
                print(f"      • {row[0]}: {row[1]} = {row[2]} (LBP?)")
        else:
            print("   ✅ No prices above 1000 - all converted to USD")
        
        print("\n" + "=" * 70)
        print("✅ DEEP ANALYSIS COMPLETE")
        print("=" * 70)

asyncio.run(deep_check())
