# LionBot - Server & Database Reference

## Quick Access Commands

```bash
# SSH to server
ssh root@lion.hmz.technology
# Password: Hasan123$$2026

# Run command on server
sshpass -p 'Hasan123$$2026' ssh root@lion.hmz.technology "YOUR_COMMAND"

# Copy file to server
sshpass -p 'Hasan123$$2026' scp file.py root@lion.hmz.technology:/root/

# Run Python in Docker container
docker exec lionbot-backend-1 python your_script.py
```

---

## Server Details

| Item | Value |
|------|-------|
| **Host** | `lion.hmz.technology` |
| **SSH User** | `root` |
| **SSH Password** | `Hasan123$$2026` |
| **Docker Container** | `lionbot-backend-1` |

---

## Database Details

| Item | Value |
|------|-------|
| **Type** | PostgreSQL |
| **Host** | `163.245.208.160` |
| **Database Name** | `lionbot` |
| **Username** | `lionbot` |
| **Password** | `LionBot2024` |
| **Port** | `5432` |

### Connection String
```
postgresql://lionbot:LionBot2024@163.245.208.160:5432/lionbot
postgresql+asyncpg://lionbot:LionBot2024@163.245.208.160:5432/lionbot
```

---

## Database Tables

### Main Tables:
| Table | Description |
|-------|-------------|
| `restaurant` | المطاعم |
| `restaurant_category` | تصنيفات المطاعم |
| `branch` | فروع المطاعم |
| `menu` | قوائم الطعام |
| `category` | فئات القائمة |
| `menuitem` | أصناف الطعام |
| `menuitemvariant` | أحجام الأصناف (S/M/L) |
| `user` | المستخدمين |
| `order` | الطلبات |

### Key Relationships:
```
Restaurant → Menu → Category → MenuItem → MenuItemVariant
Restaurant → RestaurantCategory
Restaurant → Branch
```

---

## Useful Database Queries

### Count restaurants
```sql
SELECT COUNT(*) FROM restaurant;
```

### List restaurants by category
```sql
SELECT rc.name, r.name, r.name_ar
FROM restaurant r
LEFT JOIN restaurant_category rc ON r.category_id = rc.id
ORDER BY rc.name;
```

### Check items without prices
```sql
SELECT r.name, mi.name, mi.price
FROM menuitem mi
JOIN category c ON mi.category_id = c.id
JOIN menu m ON c.menu_id = m.id
JOIN restaurant r ON m.restaurant_id = r.id
WHERE mi.price IS NULL AND mi.has_variants = FALSE;
```

### Price statistics
```sql
SELECT MIN(price), MAX(price), AVG(price), COUNT(*)
FROM menuitem WHERE price IS NOT NULL;
```

---

## Running Scripts on Server

### Method 1: Copy and Run
```bash
# Copy script
sshpass -p 'Hasan123$$2026' scp script.py root@lion.hmz.technology:/root/

# Run in Docker
sshpass -p 'Hasan123$$2026' ssh root@lion.hmz.technology "docker cp /root/script.py lionbot-backend-1:/app/ && docker exec lionbot-backend-1 python /app/script.py"
```

### Method 2: Direct Python Command
```bash
sshpass -p 'Hasan123$$2026' ssh root@lion.hmz.technology 'docker exec lionbot-backend-1 python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(\"SELECT COUNT(*) FROM restaurant\"))
        print(result.scalar())

asyncio.run(run())
"'
```

---

## Import Script Template

```python
#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.restaurant import Restaurant, RestaurantCategory
from app.models.menu import Menu, Category, MenuItem, MenuItemVariant

async def main():
    async with AsyncSessionLocal() as session:
        # Your code here
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Restaurant Categories (Existing)

| ID | Name | Arabic | Icon |
|----|------|--------|------|
| 1 | Offers | عروض | 🔥 |
| 2 | Snacks | سناك | 🍿 |
| 3 | Shawarma | شاورما | 🌯 |
| 4 | Sandwiches | ساندويشات | 🥪 |
| 5 | Pizza | بيتزا | 🍕 |
| 6 | Burgers | برغر | 🍔 |
| 7 | Grills | مشاوي | 🍖 |
| 8 | Home Food | أكل بيتي | 🍲 |
| 9 | Sweets | حلويات | 🍰 |
| 10 | Beverages | مشروبات | 🥤 |
| 11 | Manakish | مناقيش | 🫓 |
| 12 | Breakfast | فطور | 🍳 |

---

## Currency Conversion

| From | To | Rate |
|------|-----|------|
| LBP | USD | ÷ 90,000 |
| USD | LBP | × 90,000 |

Example: 450,000 LBP = $5.00 USD

---

## File Locations

### Backend
- **Main App**: `/Users/hasanelzein/Desktop/lionbot/backend/app/`
- **Models**: `/Users/hasanelzein/Desktop/lionbot/backend/app/models/`
- **Database Session**: `/Users/hasanelzein/Desktop/lionbot/backend/app/db/session.py`
- **Import Scripts**: `/Users/hasanelzein/Desktop/lionbot/backend/`

### Admin App
- **Flutter App**: `/Users/hasanelzein/Desktop/lionbot/admin_app/`

### Data Files
- **Restaurant Data**: `/Users/hasanelzein/Desktop/lionbot/admin_app/rest2.md`

---

## Current Stats (Jan 2026)

- **Total Restaurants**: 63
- **Total Menu Items**: 868
- **Items with Direct Price**: 835
- **Items with Variants**: 51
- **Total Variants**: 80
- **Price Range**: $0.20 - $58.89
- **Average Price**: $6.34

---

## Important Notes

1. **Never use local IP** - Database only accessible from server
2. **Always run scripts inside Docker** container
3. **Prices are in USD** - Convert from LBP ÷ 90,000
4. **Use existing categories only** - Don't create new ones unless needed
5. **Check for duplicates** before importing restaurants

---

## Contact / Support

For any issues, check:
1. Docker logs: `docker logs lionbot-backend-1`
2. Database connection: Test with simple SELECT query
3. SSH access: Verify password hasn't changed
