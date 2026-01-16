import google.generativeai as genai
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.menu import MenuItem, Category, Menu
from app.models.restaurant import Restaurant, RestaurantCategory
from sqlalchemy import select
import logging
import json
import re
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# Lebanese Marketing Phrases
MARKETING_PHRASES = {
    "greeting": [
        "أهلا وسهلا! 😊",
        "مرحبا فيك! 🌟",
        "نورتنا! ✨",
    ],
    "confirmation": [
        "تكرم عينك! ✅",
        "على راسي! 👍",
        "أمرك! ✨",
        "بالخدمة! 🙌",
    ],
    "upsell": [
        "شو رأيك تضيف معها {item}؟ 🔥",
        "بتحلى أكتر مع {item}! 😋",
        "ما تنسى {item}! 👌",
        "جرب كمان {item}! ⭐",
    ],
    "cart_added": [
        "تم! {item} انضافت للسلة 🛒",
        "حاضر! {item} صارت بالسلة ✅",
        "جاهز! ضفنا {item} 👍",
    ],
    "enjoy": [
        "صحتين وعافية! 🍽️",
        "بالعافية مقدماً! 😋",
        "يسلمو إيديك اللي طلب! ❤️",
    ],
    "searching": [
        "عم دور لك... 🔍",
        "لحظة معي... 🔎",
    ],
    "found_restaurants": [
        "لقيتلك {count} مطعم عندهم {item}! 🏪",
        "في {count} مطاعم بتقدم {item}! 🍽️",
    ],
    "no_results": [
        "ما لقيت {item} بالمطاعم 😕 جرب شي ثاني!",
        "للأسف ما في {item} هلق، بس جرب غيرها! 🙏",
    ],
    "suggest_more": [
        "بدك شي ثاني؟ 🤔",
        "في شي ثاني بتحب تضيفه؟ 😊",
    ],
}

import random
def get_phrase(category: str, **kwargs) -> str:
    """Get random marketing phrase from category"""
    phrases = MARKETING_PHRASES.get(category, [""])
    phrase = random.choice(phrases)
    return phrase.format(**kwargs) if kwargs else phrase


class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("✅ Gemini AI initialized successfully")
        else:
            logger.warning("GEMINI_API_KEY not found. AI features will be disabled.")
            self.model = None

    async def process_smart_order(
        self,
        text: str,
        language: str = "ar",
        restaurant_id: Optional[int] = None,
        user_data: Optional[dict] = None,
        conversation_history: str = ""
    ) -> Dict[str, Any]:
        """
        Smart AI processing with intent detection and conversation memory:
        - search_product: User searching for a product type (show restaurants)
        - order_item: User ordering specific item (add to cart)
        - discover_category: User exploring a category
        - ask_question: User asking a question
        - reorder: User wants to repeat previous order
        - modify_cart: User wants to modify cart
        """
        if not self.model:
            return {"success": False, "intent": "error", "message": "AI غير متاح"}

        try:
            # Get smart context based on current state
            products_context = await self._get_smart_products_context(restaurant_id, text)
            restaurants_context = await self._get_restaurants_with_categories()
            categories_context = await self._get_categories_context()

            # Build smart prompt with conversation history
            prompt = self._build_smart_prompt(
                text, language, products_context,
                restaurants_context, categories_context,
                restaurant_id, conversation_history
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    response_mime_type="application/json"
                )
            )
            
            result = self._parse_ai_response(response.text)
            
            # Enrich result with database info
            result = await self._enrich_result(result, restaurant_id)
            
            return result
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return {
                "success": False,
                "intent": "error",
                "message": "عذراً، صار في مشكلة. جرب كمان مرة! 🙏"
            }

    def _build_smart_prompt(
        self, text: str, language: str,
        products: str, restaurants: str, categories: str,
        current_restaurant_id: Optional[int],
        conversation_history: str = ""
    ) -> str:
        """Build intelligent prompt for intent detection and smart responses with conversation memory"""

        restaurant_context = f"المستخدم حالياً في مطعم ID: {current_restaurant_id}" if current_restaurant_id else "المستخدم لم يختار مطعم بعد"

        # Add conversation history context
        history_context = ""
        if conversation_history:
            history_context = f"""
المحادثة السابقة:
{conversation_history}

ملاحظة مهمة: إذا قال المستخدم "من الأول/الثاني/الثالث" فهو يقصد من نتائج البحث السابقة.
إذا قال "نفسه" أو "هيك" فهو يقصد نفس الشيء السابق.
إذا قال "كمان واحد" فهو يقصد إضافة 1 من آخر منتج.
"""

        return f"""أنت مساعد ذكاء اصطناعي لخدمة توصيل طعام. أنت بائع محترف وودود.

مهمتك:
1. فهم نية المستخدم (intent)
2. اقتراح منتجات مكملة (upsell)
3. الرد بأسلوب لبناني ودود
4. فهم السياق من المحادثة السابقة
5. فهم الطلبات الكاملة (one-shot) التي تتضمن الصنف والمطعم والعنوان

{restaurant_context}
{history_context}

التصنيفات المتاحة:
{categories}

المطاعم المتاحة:
{restaurants}

المنتجات المتاحة (اسم: سعر @ مطعم):
{products}

أرجع JSON بهذا الشكل:
{{
    "intent": "search_product" | "order_item" | "discover_category" | "ask_question" | "greeting" | "reorder" | "modify_cart" | "one_shot_order",
    "understood": true/false,
    "product_query": "اسم المنتج المطلوب (مثل: برغر، شاورما، مناقيش)",
    "category_query": "اسم التصنيف (مثل: Manakish, Breakfast)",
    "restaurant_name": "اسم المطعم إذا ذكره",
    "delivery_address": "عنوان التوصيل إذا ذكره (null إذا لم يذكر)",
    "items": [
        {{"name": "اسم الصنف بالضبط من القائمة", "quantity": 1, "size": "صغير/وسط/كبير أو null", "action": "add" | "remove" | "increase" | "decrease"}}
    ],
    "reference_position": null أو رقم (1, 2, 3) إذا أشار لنتيجة سابقة,
    "upsell_suggestions": ["بطاطا", "بيبسي", "صوص"],
    "message": "رد ودود وجذاب بالعامية اللبنانية",
    "needs_confirmation": true/false (true إذا كان طلب كامل يحتاج تأكيد)
}}

أمثلة:
"بدي برغر" → {{"intent": "search_product", "product_query": "برغر", "message": "تكرم! عنا كذا مطعم فيهم برغر 🍔"}}
"شو في مناقيش" → {{"intent": "discover_category", "category_query": "Manakish", "message": "عنا أطيب مناقيش! 🫓"}}
"بدي 2 شاورما دجاج كبير من غسان" → {{"intent": "order_item", "items": [{{"name": "شاورما دجاج", "quantity": 2, "size": "كبير"}}], "restaurant_name": "غسان", "upsell_suggestions": ["بطاطا", "بيبسي"], "message": "على راسي! 2 شاورما دجاج كبير من غسان 😋"}}
"من الثاني" → {{"intent": "order_item", "reference_position": 2, "message": "تم! من الخيار الثاني"}}
"نفس طلبي السابق" → {{"intent": "reorder", "message": "تمام! رح نكرر طلبك السابق"}}
"شيل البيبسي" → {{"intent": "modify_cart", "items": [{{"name": "بيبسي", "action": "remove"}}], "message": "تم شيلنا البيبسي"}}
"بدي 2 شاورما من غسان على البترون" → {{"intent": "one_shot_order", "items": [{{"name": "شاورما", "quantity": 2}}], "restaurant_name": "غسان", "delivery_address": "البترون", "needs_confirmation": true, "message": "تمام! 2 شاورما من غسان على البترون 🚗"}}
"طلبلي برغر من ماكدونالدز على المريجة" → {{"intent": "one_shot_order", "items": [{{"name": "برغر", "quantity": 1}}], "restaurant_name": "ماكدونالدز", "delivery_address": "المريجة", "needs_confirmation": true, "message": "حاضر! برغر من ماكدونالدز على المريجة 🍔"}}
"زيد 2 بيبسي" → {{"intent": "modify_cart", "items": [{{"name": "بيبسي", "quantity": 2, "action": "increase"}}], "message": "تم زدنا 2 بيبسي"}}
"نقص شاورما وحدة" → {{"intent": "modify_cart", "items": [{{"name": "شاورما", "quantity": 1, "action": "decrease"}}], "message": "تم نقصنا شاورما"}}

طلب المستخدم: {text}
"""

    async def _get_smart_products_context(self, restaurant_id: Optional[int] = None, query: str = "") -> str:
        """Get smart products context based on current state"""
        try:
            async with AsyncSessionLocal() as db:
                # Strategy 1: If in a specific restaurant, get only that restaurant's products
                if restaurant_id:
                    result = await db.execute(
                        select(MenuItem, Menu, Restaurant)
                        .join(Category, MenuItem.category_id == Category.id)
                        .join(Menu, Category.menu_id == Menu.id)
                        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
                        .where(MenuItem.is_available == True)
                        .where(Restaurant.id == restaurant_id)
                        .limit(100)
                    )
                    items = result.all()

                # Strategy 2: If query contains a product keyword, search for it
                elif query:
                    # Common product keywords
                    keywords = query.lower().split()
                    result = await db.execute(
                        select(MenuItem, Menu, Restaurant)
                        .join(Category, MenuItem.category_id == Category.id)
                        .join(Menu, Category.menu_id == Menu.id)
                        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
                        .where(MenuItem.is_available == True)
                        .where(Restaurant.is_active == True)
                        .limit(300)
                    )
                    all_items = result.all()

                    # Filter items that match the query
                    items = []
                    for item, menu, restaurant in all_items:
                        item_name = (item.name_ar or item.name or "").lower()
                        if any(kw in item_name for kw in keywords):
                            items.append((item, menu, restaurant))

                    # If no matches, return most popular items
                    if not items:
                        items = all_items[:50]

                # Strategy 3: Default - get popular/diverse items
                else:
                    result = await db.execute(
                        select(MenuItem, Menu, Restaurant)
                        .join(Category, MenuItem.category_id == Category.id)
                        .join(Menu, Category.menu_id == Menu.id)
                        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
                        .where(MenuItem.is_available == True)
                        .where(Restaurant.is_active == True)
                        .limit(80)
                    )
                    items = result.all()

                # Format products
                products = []
                for item, menu, restaurant in items[:80]:  # Limit to 80
                    name = item.name_ar or item.name
                    rest_name = restaurant.name_ar or restaurant.name
                    if hasattr(item, 'has_variants') and item.has_variants and hasattr(item, 'price_min') and item.price_min:
                        price_str = f"${item.price_min:.2f}-${item.price_max:.2f}"
                    elif item.price:
                        price_str = f"${item.price:.2f}"
                    else:
                        price_str = "$0.00"
                    products.append(f"- {name} ({price_str}) @ {rest_name} [ID:{item.id}]")

                return "\n".join(products)
        except Exception as e:
            logger.error(f"Error getting smart products: {e}")
            return ""

    async def _get_all_products_context(self) -> str:
        """Get all products with their restaurants (fallback)"""
        return await self._get_smart_products_context()

    async def _get_restaurants_with_categories(self) -> str:
        """Get restaurants with their categories"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Restaurant, RestaurantCategory)
                    .outerjoin(RestaurantCategory, Restaurant.category_id == RestaurantCategory.id)
                    .where(Restaurant.is_active == True)
                )
                rows = result.all()
                
                restaurants = []
                for rest, cat in rows:
                    cat_name = cat.name if cat else "Other"
                    rest_name = rest.name_ar or rest.name
                    restaurants.append(f"- {rest_name} (ID:{rest.id}) [{cat_name}]")
                
                return "\n".join(restaurants)
        except Exception as e:
            logger.error(f"Error getting restaurants: {e}")
            return ""

    async def _get_categories_context(self) -> str:
        """Get restaurant categories"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(RestaurantCategory)
                    .where(RestaurantCategory.is_active == True)
                )
                categories = result.scalars().all()
                return "\n".join([f"- {c.name} / {c.name_ar}" for c in categories])
        except Exception as e:
            return ""

    async def _enrich_result(self, result: dict, current_restaurant_id: Optional[int]) -> dict:
        """Enrich AI result with actual database IDs and data"""
        intent = result.get("intent", "error")
        
        if intent == "search_product":
            # Find restaurants that have this product
            product_query = result.get("product_query", "")
            if product_query:
                restaurants = await self._find_restaurants_with_product(product_query)
                result["matching_restaurants"] = restaurants
                result["success"] = len(restaurants) > 0
                
        elif intent == "discover_category":
            # Find restaurants in this category
            category_query = result.get("category_query", "")
            if category_query:
                restaurants = await self._find_restaurants_by_category(category_query)
                result["matching_restaurants"] = restaurants
                result["success"] = len(restaurants) > 0
                
        elif intent == "order_item":
            # Match items with menu
            restaurant_name = result.get("restaurant_name")
            if restaurant_name:
                rest_id = await self._find_restaurant_id(restaurant_name)
                if rest_id:
                    result["restaurant_id"] = rest_id
                    result = await self._match_menu_items(result, rest_id)
            elif current_restaurant_id:
                result["restaurant_id"] = current_restaurant_id
                result = await self._match_menu_items(result, current_restaurant_id)
            else:
                # No restaurant - need to find one
                product = result.get("items", [{}])[0].get("name", "")
                if product:
                    restaurants = await self._find_restaurants_with_product(product)
                    result["matching_restaurants"] = restaurants
                    result["intent"] = "search_product"  # Convert to search
                    result["product_query"] = product
                    
        elif intent in ["greeting", "ask_question"]:
            result["success"] = True
            
        return result

    async def _find_restaurants_with_product(self, product: str) -> List[dict]:
        """Find restaurants that have products matching the query"""
        try:
            async with AsyncSessionLocal() as db:
                # Search in menu items
                result = await db.execute(
                    select(Restaurant, MenuItem)
                    .join(Menu, Restaurant.id == Menu.restaurant_id)
                    .join(Category, Menu.id == Category.menu_id)
                    .join(MenuItem, Category.id == MenuItem.category_id)
                    .where(Restaurant.is_active == True)
                    .where(MenuItem.is_available == True)
                )
                rows = result.all()
                
                # Normalize search
                product_lower = self._normalize_arabic(product)
                matching = {}
                
                for rest, item in rows:
                    item_name = self._normalize_arabic(item.name_ar or item.name)
                    if product_lower in item_name or item_name in product_lower:
                        if rest.id not in matching:
                            matching[rest.id] = {
                                "id": rest.id,
                                "name": rest.name_ar or rest.name,
                                "name_en": rest.name,
                                "items_count": 0
                            }
                        matching[rest.id]["items_count"] += 1
                
                return list(matching.values())
        except Exception as e:
            logger.error(f"Error finding restaurants: {e}")
            return []

    async def _find_restaurants_by_category(self, category: str) -> List[dict]:
        """Find restaurants by category name"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Restaurant, RestaurantCategory)
                    .join(RestaurantCategory, Restaurant.category_id == RestaurantCategory.id)
                    .where(Restaurant.is_active == True)
                )
                rows = result.all()
                
                category_lower = category.lower()
                matching = []
                
                for rest, cat in rows:
                    if category_lower in cat.name.lower() or category_lower in (cat.name_ar or "").lower():
                        matching.append({
                            "id": rest.id,
                            "name": rest.name_ar or rest.name,
                            "name_en": rest.name
                        })
                
                return matching
        except Exception as e:
            logger.error(f"Error finding restaurants by category: {e}")
            return []

    async def _find_restaurant_id(self, name: str) -> Optional[int]:
        """Find restaurant ID by name"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Restaurant).where(Restaurant.is_active == True)
                )
                restaurants = result.scalars().all()
                name_lower = self._normalize_arabic(name)
                
                for r in restaurants:
                    r_name = self._normalize_arabic(r.name_ar or r.name)
                    r_name_en = r.name.lower()
                    if name_lower in r_name or r_name in name_lower or name_lower in r_name_en:
                        return r.id
                return None
        except Exception:
            return None

    def _normalize_arabic(self, text: str) -> str:
        """Normalize Arabic text"""
        if not text:
            return ""
        text = re.sub(r'[أإآا]', 'ا', text)
        text = re.sub(r'[يى]', 'ي', text)
        text = re.sub(r'ة', 'ه', text)
        text = re.sub(r'[\u064B-\u0652]', '', text)
        arabic_nums = {'٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'}
        for ar, en in arabic_nums.items():
            text = text.replace(ar, en)
        return text.strip().lower()

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response JSON"""
        try:
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            data = json.loads(response_text.strip())
            data["success"] = data.get("understood", False)
            return data
            
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return self._parse_ai_response(json_match.group())
                except Exception:
                    pass
            
            return {
                "success": False,
                "intent": "error",
                "message": "ما فهمت عليك، قلي كمان مرة! 🙏"
            }

    async def _match_menu_items(self, ai_result: dict, restaurant_id: int) -> dict:
        """Match AI items with actual menu"""
        matched_items = []
        unmatched_items = []
        
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(MenuItem)
                    .join(Category)
                    .join(Menu)
                    .where(Menu.restaurant_id == restaurant_id)
                    .where(MenuItem.is_available == True)
                )
                menu_items = result.scalars().all()
                
                menu_lookup = {}
                for item in menu_items:
                    name = self._normalize_arabic(item.name_ar or item.name)
                    menu_lookup[name] = item
                    if item.name_ar:
                        menu_lookup[self._normalize_arabic(item.name)] = item
                
                for requested in ai_result.get("items", []):
                    req_name = self._normalize_arabic(requested.get("name", ""))
                    quantity = requested.get("quantity", 1)
                    matched = None
                    
                    # Exact match
                    if req_name in menu_lookup:
                        matched = menu_lookup[req_name]
                    else:
                        # Partial match
                        for menu_name, item in menu_lookup.items():
                            if req_name in menu_name or menu_name in req_name:
                                matched = item
                                break
                    
                    if matched:
                        matched_items.append({
                            "menu_item_id": matched.id,
                            "name": matched.name_ar or matched.name,
                            "price": matched.price,
                            "quantity": quantity,
                            "restaurant_id": restaurant_id  # Required for order creation
                        })
                    else:
                        unmatched_items.append(requested.get("name", ""))
        except Exception as e:
            logger.error(f"Error matching items: {e}")
        
        ai_result["items"] = matched_items
        ai_result["unmatched"] = unmatched_items
        ai_result["success"] = len(matched_items) > 0
        
        return ai_result

    async def get_upsell_suggestions(self, restaurant_id: int, current_items: List[int]) -> List[dict]:
        """Get upsell suggestions based on current cart"""
        suggestions = []
        try:
            async with AsyncSessionLocal() as db:
                # Get categories we should suggest from
                suggest_categories = ["Appetizer", "مقبلات", "Beverages", "مشروبات", "Add On", "إضافات"]
                
                result = await db.execute(
                    select(MenuItem, Category)
                    .join(Category)
                    .join(Menu)
                    .where(Menu.restaurant_id == restaurant_id)
                    .where(MenuItem.is_available == True)
                    .where(MenuItem.id.notin_(current_items))
                )
                items = result.all()
                
                for item, cat in items:
                    cat_name = cat.name_ar or cat.name
                    if any(s in cat_name for s in suggest_categories):
                        suggestions.append({
                            "id": item.id,
                            "name": item.name_ar or item.name,
                            "price": item.price
                        })
                
                return suggestions[:5]  # Max 5 suggestions
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []


# Keep backward compatibility
ai_service = AIService()

# Also export for new usage
async def process_text_order(text: str, language: str = "ar", restaurant_id: Optional[int] = None) -> Dict[str, Any]:
    """Legacy function for backward compatibility"""
    return await ai_service.process_smart_order(text, language, restaurant_id)
