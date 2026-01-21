#!/usr/bin/env python3
import json
import re

def parse_markdown_json(filepath):
    """Parse JSON objects from markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    restaurants = []
    
    # Find all restaurant blocks
    pattern = r'\{[^}]*"restaurant_info"[^}]*"menu"[^}]*\}'
    
    # Better approach: split by restaurant_info and parse each
    parts = content.split('"restaurant_info"')
    
    for i in range(1, len(parts)):
        part = parts[i]
        
        # Extract restaurant name
        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', part)
        if not name_match:
            continue
        
        name = name_match.group(1)
        
        # Find menu section
        menu_start = part.find('"menu"')
        if menu_start == -1:
            continue
        
        menu_part = part[menu_start:]
        
        # Count braces to find the end of menu
        brace_count = 0
        in_string = False
        escape_next = False
        menu_json = ""
        
        for char in menu_part:
            if escape_next:
                escape_next = False
                menu_json += char
                continue
            
            if char == '\\':
                escape_next = True
                menu_json += char
                continue
            
            if char == '"':
                in_string = not in_string
                menu_json += char
                continue
            
            if not in_string:
                if char in ['{', '[']:
                    brace_count += 1
                    menu_json += char
                elif char in ['}', ']']:
                    brace_count -= 1
                    menu_json += char
                    if brace_count == 0:
                        break
            else:
                menu_json += char
        
        try:
            # Clean and parse
            menu_json = menu_json.replace('\\_', '_').replace('\\', '')
            menu_data = json.loads(menu_json)
            
            restaurants.append({
                'restaurant_info': {'name': name},
                'menu': menu_data
            })
        except Exception as e:
            print(f"Error parsing {name}: {e}")
            continue
    
    return restaurants

def format_restaurant_text(restaurant):
    """Format restaurant data as readable text"""
    text = ""
    
    name = restaurant.get('restaurant_info', {}).get('name', 'Unknown')
    text += f"\n{'='*70}\n"
    text += f"مطعم: {name}\n"
    text += f"{'='*70}\n\n"
    
    menu = restaurant.get('menu', {})
    
    if isinstance(menu, dict):
        for cat_name, items in menu.items():
            cat_title = cat_name.replace('_', ' ').title()
            text += f"📁 {cat_title}\n"
            text += "─" * 70 + "\n"
            
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        item_name = item.get('item', item.get('item_ar', ''))
                        price = item.get('price', 0)
                        price_lbp = item.get('price_lbp', 0)
                        price_usd = item.get('price_usd', 0)
                        desc = item.get('description', '')
                        
                        text += f"  • {item_name}"
                        if desc:
                            text += f" - {desc}"
                        if price_lbp:
                            text += f" - {price_lbp:,} LBP"
                        if price_usd:
                            text += f" (${price_usd:.2f})"
                        elif price:
                            text += f" - ${price:.2f}"
                        text += "\n"
            
            text += "\n"
    
    elif isinstance(menu, list):
        for category in menu:
            cat_ar = category.get('category_ar', category.get('category', ''))
            cat_en = category.get('category_en', '')
            items = category.get('items', [])
            
            if cat_ar:
                text += f"📁 {cat_ar}"
                if cat_en:
                    text += f" ({cat_en})"
                text += "\n"
                text += "─" * 70 + "\n"
                
                for item in items:
                    name_ar = item.get('item_ar', item.get('item', ''))
                    name_en = item.get('item_en', '')
                    price_lbp = item.get('price_lbp', 0)
                    price_usd = item.get('price_usd', item.get('price', 0))
                    
                    if name_ar:
                        text += f"  • {name_ar}"
                        if name_en:
                            text += f" ({name_en})"
                        if price_lbp:
                            text += f" - {price_lbp:,} LBP"
                        if price_usd:
                            text += f" (${price_usd:.2f})"
                        text += "\n"
                
                text += "\n"
    
    return text

def main():
    output_file = "/Users/hasanelzein/Desktop/lionbot/restaurants_data.txt"
    
    all_restaurants = []
    
    # Process res.md
    try:
        print("Processing res.md...")
        restaurants = parse_markdown_json("/Users/hasanelzein/Desktop/lionbot/res.md")
        print(f"Found {len(restaurants)} restaurants in res.md")
        all_restaurants.extend(restaurants)
    except Exception as e:
        print(f"Error processing res.md: {e}")
    
    # Process rest2.md
    try:
        print("Processing rest2.md...")
        restaurants = parse_markdown_json("/Users/hasanelzein/Desktop/lionbot/admin_app/rest2.md")
        print(f"Found {len(restaurants)} restaurants in rest2.md")
        all_restaurants.extend(restaurants)
    except Exception as e:
        print(f"Error processing rest2.md: {e}")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("بيانات المطاعم والقوائم\n")
        f.write("=" * 70 + "\n\n")
        
        for rest in all_restaurants:
            f.write(format_restaurant_text(rest))
    
    print(f"Done! Data saved to {output_file}")
    print(f"Total restaurants: {len(all_restaurants)}")

if __name__ == "__main__":
    main()
