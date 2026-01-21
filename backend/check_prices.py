#!/usr/bin/env python3
"""Check prices in database"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def check_prices():
    async with AsyncSessionLocal() as session:
        # Check for NULL prices (items without variants)
        result = await session.execute(text('''
            SELECT mi.name, mi.name_ar, mi.price, r.name as restaurant
            FROM menuitem mi
            JOIN category c ON mi.category_id = c.id
            JOIN menu m ON c.menu_id = m.id
            JOIN restaurant r ON m.restaurant_id = r.id
            WHERE mi.price IS NULL AND mi.has_variants = FALSE
            ORDER BY r.name, mi.name
        '''))
        null_prices = result.fetchall()

        if null_prices:
            print(f'❌ {len(null_prices)} items WITHOUT prices:')
            for row in null_prices:
                print(f'  - {row[3]}: {row[0]} ({row[1]})')
        else:
            print('✅ All items have prices or variants')

        # Check for high prices (might be LBP not converted)
        result = await session.execute(text('''
            SELECT mi.name, mi.name_ar, mi.price, r.name as restaurant
            FROM menuitem mi
            JOIN category c ON mi.category_id = c.id
            JOIN menu m ON c.menu_id = m.id
            JOIN restaurant r ON m.restaurant_id = r.id
            WHERE mi.price > 50
            ORDER BY mi.price DESC
        '''))
        high_prices = result.fetchall()

        if high_prices:
            print(f'\n⚠️ {len(high_prices)} items with high prices (> $50):')
            for row in high_prices:
                print(f'  - {row[3]}: {row[0]} = ${row[2]}')
        else:
            print('\n✅ No suspiciously high prices')

        # Overall stats
        result = await session.execute(text('''
            SELECT
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(price) as avg_price,
                COUNT(*) as total
            FROM menuitem
            WHERE price IS NOT NULL
        '''))
        stats = result.fetchone()
        print(f'\n📊 Menu Item Statistics:')
        print(f'  - Total items with prices: {stats[3]}')
        print(f'  - Min price: ${stats[0]:.2f}')
        print(f'  - Max price: ${stats[1]:.2f}')
        print(f'  - Avg price: ${stats[2]:.2f}')

        # Variant stats
        result = await session.execute(text('''
            SELECT MIN(price), MAX(price), COUNT(*)
            FROM menuitemvariant
        '''))
        var_stats = result.fetchone()
        if var_stats[2] > 0:
            print(f'\n📊 Variant Statistics:')
            print(f'  - Total variants: {var_stats[2]}')
            print(f'  - Min: ${var_stats[0]:.2f}, Max: ${var_stats[1]:.2f}')

asyncio.run(check_prices())
