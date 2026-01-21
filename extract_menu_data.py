#!/usr/bin/env python3
import json
import re

def extract_from_json_like(content):
    """Extract JSON objects from markdown content"""
    restaurants = []
    
    # Find all JSON-like blocks
    pattern = r'\{[^}]*"restaurant_info"[^}]*\}'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        try:
            # Clean up the JSON
            cleaned = match.replace('\\', '')
            data = json.loads(cleaned)
            restaurants.append(data)
        except:
            pass
    
    return restaurants

def process_res_md(filepath):
    """Process res.md file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    restaurants = extract_from_json_like(content)
    return restaurants

def process_rest2_md(filepath):
    """Process rest2.md file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    restaurants = extract_from_json_like(content)
    return restaurants

def format_restaurant_text(restaurant):
    """Format restaurant data as text"""
    text = ""
    
    if 'restaurant_info' in restaurant:
        info = restaurant['restaurant_info']
        text += f"\n{'='*60}\n"
        text += f"مطعم: {info.get('name', 'N/A')}\n"
        if 'slogan' in info:
            text += f"شعار: {info['slogan']}\n"
        text += f"{'='*60}\n\n"
    
    if 'menu' in restaurant:
        menu = restaurant['menu']
        
        # Handle different menu formats
        if isinstance(menu, list):
            for category in menu:
                cat_ar = category.get('category_ar', '')
                cat_en = category.get('category_en', '')
                items = category.get('items', [])
                
                text += f"📁 {cat_ar} ({cat_en})\n"
                text += f"{'─'*60}\n"
                
                for item in items:
                    name_ar = item.get('item_ar', item.get('item', ''))
                    name_en = item.get('item_en', '')
                    price_lbp = item.get('price_lbp', 0)
                    price_usd = item.get('price_usd', 0)
                    
                    if name_ar:
                        text += f"  • {name_ar}"
                        if name_en:
                            text += f" ({name_en})"
                        text += f" - {price_lbp:,} LBP (${price_usd:.2f})\n"
                
                text += "\n"
        
        elif isinstance(menu, dict):
            for cat_name, items in menu.items():
                text += f"📁 {cat_name.replace('_', ' ').title()}\n"
                text += f"{'─'*60}\n"
                
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            name = item.get('item', item.get('item_ar', ''))
                            price = item.get('price', 0)
                            desc = item.get('description', '')
                            
                            text += f"  • {name}"
                            if desc:
                                text += f" - {desc}"
                            text += f" - ${price:.2f}\n"
                
                text += "\n"
    
    return text

def main():
    output_file = "/Users/hasanelzein/Desktop/lionbot/restaurants_data.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("بيانات المطاعم والقوائم\n")
        f.write("="*60 + "\n\n")
        
        # Process res.md
        try:
            print("Processing res.md...")
            restaurants = process_res_md("/Users/hasanelzein/Desktop/lionbot/res.md")
            for rest in restaurants:
                f.write(format_restaurant_text(rest))
        except Exception as e:
            f.write(f"Error processing res.md: {e}\n\n")
        
        # Process rest2.md
        try:
            print("Processing rest2.md...")
            restaurants = process_rest2_md("/Users/hasanelzein/Desktop/lionbot/admin_app/rest2.md")
            for rest in restaurants:
                f.write(format_restaurant_text(rest))
        except Exception as e:
            f.write(f"Error processing rest2.md: {e}\n\n")
        
        # Note about docx files
        f.write("\n" + "="*60 + "\n")
        f.write("ملاحظة: ملفات DOCX تحتاج إلى مكتبة python-docx لقراءتها\n")
        f.write("يمكنك تثبيتها بـ: pip install python-docx\n")
    
    print(f"Done! Data saved to {output_file}")

if __name__ == "__main__":
    main()
