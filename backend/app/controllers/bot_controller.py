from app.services.whatsapp_service import whatsapp_service
from app.services.redis_service import redis_service
from app.services.ai_service import ai_service
from app.services.fcm_service import fcm_service
from app.core.i18n import get_text
from app.core.constants import (
    lbp_to_usd, usd_to_lbp, format_price_usd,
    DEFAULT_DELIVERY_FEE_LBP, LOYALTY_POINTS_PER_USD,
    LOYALTY_TIER_MULTIPLIERS, LOYALTY_TIER_THRESHOLDS,
    LOYALTY_TIER_INFO, REVIEW_BONUS_POINTS, POINTS_EXPIRY_DAYS,
    get_tier_for_points, get_next_tier,
    AI_RATE_LIMIT_REQUESTS, AI_RATE_LIMIT_WINDOW
)
from app.core.validators import validate_quantity, validate_rating, sanitize_text
from app.db.session import AsyncSessionLocal
from app.models.restaurant import Restaurant, Branch, RestaurantCategory
from app.models.menu import Menu, MenuItem, Category
from app.models.order import Order, OrderItem, OrderStatus
from app.models.user import User
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BotController:
    """
    WhatsApp Bot Controller - Handles all incoming messages and manages conversation flow.
    
    States:
    - INIT: Initial state, waiting for first message
    - AWAITING_LANG: Waiting for language selection
    - MAIN_MENU: Main menu displayed
    - BROWSING_REST_CATEGORIES: User browsing restaurant categories (Shawarma, Pizza, etc.)
    - BROWSING_RESTAURANTS: User browsing restaurants list
    - BROWSING_CATEGORIES: User browsing menu categories
    - BROWSING_ITEMS: User browsing menu items in a category
    - VIEWING_ITEM: User viewing a specific item
    - AWAITING_QUANTITY: Waiting for quantity input
    - VIEWING_CART: User viewing their cart
    - EDITING_CART: User editing cart item
    - AWAITING_LOCATION: Waiting for delivery location
    - ORDER_PLACED: Order successfully placed
    - SUPPORT_CHAT: User in support mode
    """

    async def handle_message(self, phone_number: str, message_body: dict):
        """Main entry point for handling incoming WhatsApp messages"""
        logger.debug(f"Handling message from {phone_number}")

        try:
            state_data = await redis_service.get_user_state(phone_number)
            logger.debug(f"User state data: {state_data}")
        except Exception as e:
            logger.error(f"Failed to get user state: {e}")
            state_data = None

        state = state_data.get("state", "INIT") if state_data else "INIT"
        user_data = state_data.get("data", {}) if state_data else {}
        lang = user_data.get("lang", "ar")
        logger.debug(f"Current State: {state}, Lang: {lang}")

        message_type = message_body.get("type")
        logger.debug(f"Message Type: {message_type}")

        # Route message to appropriate handler
        if message_type == "text":
            await self._handle_text_message(phone_number, message_body, state, lang, user_data)
        elif message_type == "interactive":
            await self._handle_interactive_message(phone_number, message_body, state, lang, user_data)
        elif message_type == "location":
            await self._handle_location_message(phone_number, message_body, state, lang, user_data)

    # ==================== Text Message Handler ====================
    async def _handle_text_message(self, phone_number: str, message_body: dict, state: str, lang: str, user_data: dict):
        """Handle plain text messages"""
        text_data = message_body.get("text", {})
        text = text_data.get("body", "").strip()
        if not text:
            logger.warning(f"Empty text message from {phone_number}")
            return
        logger.debug(f"Text Body: {text}")

        # Handle numbered menu states FIRST (before restart check catches "0")
        if state == "BROWSING_NUMBERED_MENU":
            await self._handle_numbered_menu_input(phone_number, text, lang, user_data)
            return

        if state == "AWAITING_NUMBERED_QUANTITY":
            if text.strip().isdigit():
                await self._handle_numbered_quantity(phone_number, int(text.strip()), lang, user_data)
                return
            # Non-numeric input in quantity state - route back to menu handler
            # This lets AI handle things like "la sheel", "bde men mat3am tene", etc.
            await self._handle_numbered_menu_input(phone_number, text, lang, user_data)
            return

        # Check for restart commands
        if text.lower() in ["start", "restart", "بداية", "ابدأ", "0", "menu", "قائمة"]:
            await self._send_language_selection(phone_number)
            return

        elif state == "AWAITING_LOCATION":
            # Hybrid: handle text address
            await self._process_text_location(phone_number, text, lang, user_data)

        elif state == "AWAITING_NAME":
            # Handle name input
            await self._process_name_input(phone_number, text, lang, user_data)

        elif state == "CONFIRMING_INFO":
            # Treat any text as re-entering name or address if they didn't click buttons
            await self._show_confirmation_options(phone_number, lang, user_data)

        elif state == "AWAITING_REVIEW":
            # Handle review rating
            if await self._process_review(phone_number, text, lang, user_data):
                return
            # If not a valid rating, show main menu
            await self._send_main_menu(phone_number, lang)

        elif state in ["INIT", "MAIN_MENU", "BROWSING_RESTAURANTS", "BROWSING_CATEGORIES", "BROWSING_ITEMS", "BROWSING_REST_CATEGORIES", "BROWSING_ORDERS", "BROWSING_FAVORITES"]:
            # Check if user is selecting from suggestions (typing a number)
            if text.strip().isdigit():
                selection = int(text.strip())
                conv = await redis_service.get_conversation(phone_number)
                context = conv.get("context", {}) if conv else {}
                suggestions = context.get("suggestions", [])

                if suggestions and 1 <= selection <= len(suggestions):
                    # User selected from suggestions - add to cart
                    selected = suggestions[selection - 1]
                    await self._quick_add_suggestion(phone_number, selected, lang)
                    return

            # 🛡️ Cost Optimization: Avoid calling AI for short greetings or small talk
            greetings = ["hi", "hello", "سلام", "مرحبا", "هلا", "هاي", "hey", "test"]
            if len(text) < 3 or text.lower() in greetings:
                await self._send_main_menu(phone_number, lang)
                return

            # AI Processing for natural language orders - works even for new users!
            await self._process_ai_order(phone_number, text, lang, user_data)

        else:
            # Default: show main menu
            await self._send_main_menu(phone_number, lang)

    # ==================== Interactive Message Handler ====================
    async def _handle_interactive_message(self, phone_number: str, message_body: dict, state: str, lang: str, user_data: dict):
        """Handle interactive button/list replies"""
        interaction = message_body.get("interactive", {})
        if not interaction:
            logger.warning(f"Empty interactive message from {phone_number}")
            return

        interaction_type = interaction.get("type", "")

        if interaction_type == "button_reply":
            button_reply = interaction.get("button_reply", {})
            btn_id = button_reply.get("id", "")
            if btn_id:
                await self._handle_button_reply(phone_number, btn_id, state, lang, user_data)

        elif interaction_type == "list_reply":
            list_reply = interaction.get("list_reply", {})
            list_id = list_reply.get("id", "")
            if list_id:
                await self._handle_list_reply(phone_number, list_id, state, lang, user_data)

    async def _handle_button_reply(self, phone_number: str, btn_id: str, state: str, lang: str, user_data: dict):
        """Handle button click responses"""
        logger.debug(f"Button ID: {btn_id}, State: {state}")

        # Language Selection
        if btn_id == "lang_ar":
            lang = "ar"
            await redis_service.set_user_state(phone_number, "MAIN_MENU", {"lang": lang})
            await self._send_main_menu(phone_number, lang)

        elif btn_id == "lang_en":
            lang = "en"
            await redis_service.set_user_state(phone_number, "MAIN_MENU", {"lang": lang})
            await self._send_main_menu(phone_number, lang)

        # Main Menu Options
        elif btn_id == "menu_browse":
            await self._show_restaurant_categories(phone_number, lang)

        elif btn_id == "view_cart":
            await self._show_cart(phone_number, lang)

        elif btn_id == "support":
            await self._start_support(phone_number, lang)

        # Checkout Actions
        elif btn_id == "checkout":
            await self._start_checkout(phone_number, lang)

        elif btn_id == "use_previous_info":
            await self._process_previous_info(phone_number, lang, user_data)

        elif btn_id == "enter_new_info":
            await whatsapp_service.send_text(phone_number, get_text("share_location", lang))
            await redis_service.set_user_state(phone_number, "AWAITING_LOCATION", {"lang": lang})

        elif btn_id == "clear_cart":
            await redis_service.clear_cart(phone_number)
            await whatsapp_service.send_text(phone_number, get_text("cart_cleared", lang))
            await self._send_main_menu(phone_number, lang)

        elif btn_id == "continue_shopping" or btn_id == "add_more":
            restaurant_id = user_data.get("restaurant_id")
            if restaurant_id:
                await self._show_categories(phone_number, restaurant_id, lang)
            else:
                await self._show_restaurants(phone_number, lang)

        elif btn_id == "edit_cart":
            await self._show_cart_edit_options(phone_number, lang)

        # Item Actions
        elif btn_id.startswith("add_"):
            item_id = int(btn_id.replace("add_", ""))
            await self._prompt_quantity(phone_number, item_id, lang, user_data)

        elif btn_id.startswith("qty_"):
            # Quick add with quantity (qty_1_itemid, qty_2_itemid, etc.)
            parts = btn_id.split("_")
            quantity = int(parts[1])
            item_id = int(parts[2])
            await self._add_item_to_cart(phone_number, item_id, quantity, lang, user_data)

        elif btn_id.startswith("var_"):
            # Variant selection (var_variantId_itemId)
            parts = btn_id.split("_")
            variant_id = int(parts[1])
            item_id = int(parts[2])
            await self._add_variant_to_cart(phone_number, item_id, variant_id, 1, lang, user_data)

        # Back Navigation
        elif btn_id == "back_main":
            await self._send_main_menu(phone_number, lang)

        elif btn_id == "back_restaurants":
            await self._show_restaurants(phone_number, lang)

        elif btn_id == "back_categories":
            restaurant_id = user_data.get("restaurant_id")
            if restaurant_id:
                await self._show_categories(phone_number, restaurant_id, lang)
            else:
                await self._show_restaurants(phone_number, lang)

        # Support
        elif btn_id == "end_support":
            await whatsapp_service.send_text(phone_number, get_text("support_ended", lang))
            await self._send_main_menu(phone_number, lang)

        # Skip Upsell - show checkout options
        elif btn_id == "skip_upsell":
            buttons = [
                {"id": "checkout", "title": get_text("checkout", lang)},
                {"id": "view_cart", "title": get_text("view_cart", lang)},
                {"id": "add_more", "title": get_text("continue_shopping", lang)}
            ]
            await whatsapp_service.send_interactive_buttons(
                phone_number,
                "صحتين! شو بدك تعمل هلق؟ 😋" if lang == "ar" else "What would you like to do now?",
                buttons
            )

        # Order Confirmation
        elif btn_id == "confirm_order":
            await self._confirm_order(phone_number, lang, user_data)

        elif btn_id == "cancel_order":
            await redis_service.clear_cart(phone_number)
            await whatsapp_service.send_text(phone_number, get_text("order_cancelled", lang))
            await self._send_main_menu(phone_number, lang)

        # Favorites
        elif btn_id.startswith("add_fav_"):
            restaurant_id = int(btn_id.split("_")[2])
            await self._add_to_favorites(phone_number, restaurant_id, lang)
            await self._send_main_menu(phone_number, lang)

        elif btn_id == "skip_fav":
            await self._send_main_menu(phone_number, lang)

        # Restaurant selection from menu request
        elif btn_id.startswith("rest_"):
            restaurant_id = int(btn_id.split("_")[1])
            await self._show_categories(phone_number, restaurant_id, lang)

        # Show restaurants list
        elif btn_id == "show_restaurants":
            await self._show_restaurants(phone_number, lang)

    async def _handle_list_reply(self, phone_number: str, list_id: str, state: str, lang: str, user_data: dict):
        """Handle list item selection"""
        logger.debug(f"List ID: {list_id}, State: {state}")

        # Pagination handlers FIRST (before regular handlers)
        # Restaurant categories pagination (restcat_page_pageNum)
        if list_id.startswith("restcat_page_"):
            page = int(list_id.split("_")[2])
            await self._show_restaurant_categories(phone_number, lang, page)

        # All restaurants pagination (all_rest_page_pageNum)
        elif list_id.startswith("all_rest_page_"):
            page = int(list_id.split("_")[3])
            await self._show_restaurants(phone_number, lang, page)

        # Menu categories pagination (menucat_page_restId_pageNum)
        elif list_id.startswith("menucat_page_"):
            parts = list_id.split("_")
            restaurant_id = int(parts[2])
            page = int(parts[3])
            await self._show_categories(phone_number, restaurant_id, lang, page)

        # Restaurant Category Selection (Shawarma, Pizza, etc.)
        elif list_id.startswith("restcat_"):
            category_id = int(list_id.split("_")[1])
            await self._show_restaurants_by_category(phone_number, category_id, lang)

        # Restaurant Selection
        elif list_id.startswith("rest_"):
            restaurant_id = int(list_id.split("_")[1])
            await self._show_categories(phone_number, restaurant_id, lang)

        # Category Selection
        elif list_id.startswith("cat_"):
            category_id = int(list_id.split("_")[1])
            await self._show_menu_items(phone_number, category_id, lang, user_data)

        # Item Selection
        elif list_id.startswith("item_"):
            item_id = int(list_id.split("_")[1])
            await self._show_item_details(phone_number, item_id, lang, user_data)

        # Cart Item Selection for editing
        elif list_id.startswith("edit_item_"):
            item_id = int(list_id.split("_")[2])
            await self._show_item_edit_options(phone_number, item_id, lang)

        # Variant Selection (var_variantId_itemId)
        elif list_id.startswith("var_"):
            parts = list_id.split("_")
            variant_id = int(parts[1])
            item_id = int(parts[2])
            await self._add_variant_to_cart(phone_number, item_id, variant_id, 1, lang, user_data)

        # More restaurants pagination (more_rest_categoryId_page)
        elif list_id.startswith("more_rest_"):
            parts = list_id.split("_")
            category_id = int(parts[2])
            page = int(parts[3])
            await self._show_restaurants_by_category(phone_number, category_id, lang, page)

        # Menu items pagination (menu_page_categoryId_page)
        elif list_id.startswith("menu_page_"):
            parts = list_id.split("_")
            category_id = int(parts[2])
            page = int(parts[3])
            await self._show_menu_items(phone_number, category_id, lang, user_data, page)

        # Main Menu Options (from list)
        elif list_id == "menu_browse":
            await self._show_restaurant_categories(phone_number, lang)

        elif list_id == "view_cart":
            await self._show_cart(phone_number, lang)

        elif list_id == "reorder":
            await self._show_previous_orders(phone_number, lang)

        elif list_id == "favorites":
            await self._show_favorites(phone_number, lang)

        elif list_id == "support":
            await self._start_support(phone_number, lang)

        # Reorder selection (reorder_orderId)
        elif list_id.startswith("reorder_"):
            order_id = int(list_id.split("_")[1])
            await self._process_reorder(phone_number, order_id, lang)

        # Favorite restaurant selection (fav_restId)
        elif list_id.startswith("fav_"):
            restaurant_id = int(list_id.split("_")[1])
            await self._show_categories(phone_number, restaurant_id, lang)

        # Quick order from favorites (quickorder_itemId_restId)
        elif list_id.startswith("quickorder_"):
            parts = list_id.split("_")
            item_id = int(parts[1])
            restaurant_id = int(parts[2])
            await self._quick_add_favorite_item(phone_number, item_id, restaurant_id, lang)

    async def _quick_add_favorite_item(self, phone_number: str, item_id: int, restaurant_id: int, lang: str):
        """Quickly add a favorite item to cart"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MenuItem, Restaurant)
                .join(Category, MenuItem.category_id == Category.id)
                .join(Menu, Category.menu_id == Menu.id)
                .join(Restaurant, Menu.restaurant_id == Restaurant.id)
                .where(MenuItem.id == item_id)
            )
            row = result.first()

            if not row:
                await whatsapp_service.send_text(phone_number, "ما لقيت الصنف 🤔")
                await self._send_main_menu(phone_number, lang)
                return

            item, rest = row
            item_name = item.name_ar if lang == "ar" and item.name_ar else item.name
            price = float(item.price) if item.price else 0.0

            # Check if item has variants
            if hasattr(item, 'has_variants') and item.has_variants:
                # Show variants
                await self._show_item_details(phone_number, item_id, lang, {"restaurant_id": restaurant_id, "lang": lang})
                return

            # Add directly to cart
            cart_item = {
                "menu_item_id": item.id,
                "name": item_name,
                "price": price,
                "quantity": 1,
                "restaurant_id": restaurant_id
            }
            await redis_service.add_to_cart(phone_number, cart_item)

            # Get cart total
            cart_total = await redis_service.get_cart_total(phone_number)
            cart_count = await redis_service.get_cart_count(phone_number)

            response = f"⚡ *طلب سريع!*\n\n"
            response += f"✅ تم إضافة {item_name}\n"
            response += f"💰 السعر: ${price:.2f}\n"
            response += f"🛒 المجموع: ${float(cart_total):.2f} ({cart_count} أصناف)"

            await whatsapp_service.send_text(phone_number, response)

            # Show checkout options
            buttons = [
                {"id": "checkout", "title": "إتمام الطلب ✅" if lang == "ar" else "Checkout"},
                {"id": "view_cart", "title": "عرض السلة 🛒" if lang == "ar" else "View Cart"},
                {"id": "favorites", "title": "المزيد ⭐" if lang == "ar" else "More Favorites"}
            ]
            await whatsapp_service.send_interactive_buttons(
                phone_number,
                "شو بدك تعمل؟" if lang == "ar" else "What next?",
                buttons
            )

    # ==================== Location Handler ====================
    async def _handle_location_message(self, phone_number: str, message_body: dict, state: str, lang: str, user_data: dict):
        """Handle location sharing"""
        if state != "AWAITING_LOCATION":
            await whatsapp_service.send_text(phone_number, get_text("location_not_expected", lang))
            return

        location = message_body.get("location", {})
        if not location:
            logger.warning(f"Empty location data from {phone_number}")
            return

        lat = location.get("latitude")
        lng = location.get("longitude")

        if lat is None or lng is None:
            logger.warning(f"Missing coordinates from {phone_number}")
            return

        # Store location temporarily in session data
        user_data["delivery_lat"] = lat
        user_data["delivery_lng"] = lng
        user_data["delivery_address"] = "Shared Location 📍"

        await self._proceed_after_location(phone_number, lang, user_data)

    async def _process_text_location(self, phone_number: str, text: str, lang: str, user_data: dict):
        """Handle address entered as text"""
        user_data["delivery_address"] = text
        # If text address, we don't have lat/lng but that's okay for now
        await self._proceed_after_location(phone_number, lang, user_data)

    async def _proceed_after_location(self, phone_number: str, lang: str, user_data: dict):
        """Next step after obtaining location/address"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()
            
            # Check if we need a name
            if not user or not user.full_name or user.full_name == "WhatsApp Customer":
                await whatsapp_service.send_text(phone_number, get_text("ask_name", lang))
                await redis_service.set_user_state(phone_number, "AWAITING_NAME", user_data)
            else:
                user_data["customer_name"] = user.full_name
                await self._show_confirmation_options(phone_number, lang, user_data)

    async def _process_name_input(self, phone_number: str, text: str, lang: str, user_data: dict):
        """Handle name input"""
        user_data["customer_name"] = text
        await self._show_confirmation_options(phone_number, lang, user_data)

    async def _show_confirmation_options(self, phone_number: str, lang: str, user_data: dict):
        """Confirm all info before creating order"""
        name = user_data.get("customer_name", "N/A")
        address = user_data.get("delivery_address", "N/A")
        
        msg = get_text("confirm_name_address", lang).format(name=name, address=address)
        
        buttons = [
            {"id": "confirm_order", "title": get_text("checkout", lang)},
            {"id": "enter_new_info", "title": get_text("btn_enter_new", lang)}
        ]
        
        await whatsapp_service.send_interactive_buttons(phone_number, msg, buttons)
        await redis_service.set_user_state(phone_number, "CONFIRMING_INFO", user_data)

    # ==================== Flow Methods ====================
    async def _send_language_selection(self, phone_number: str):
        """Send language selection buttons"""
        await whatsapp_service.send_interactive_buttons(
            phone_number,
            "مرحباً! 👋\nPlease select your language / الرجاء اختيار اللغة",
            [
                {"id": "lang_ar", "title": "العربية 🇸🇦"},
                {"id": "lang_en", "title": "English 🇺🇸"}
            ]
        )
        await redis_service.set_user_state(phone_number, "AWAITING_LANG")

    async def _send_main_menu(self, phone_number: str, lang: str):
        """Send main menu options with extended features"""
        cart_count = await redis_service.get_cart_count(phone_number)
        cart_text = f" ({cart_count})" if cart_count > 0 else ""

        # Use Interactive List for more options
        welcome_msg = "🦁 أهلا وسهلا، شو بتحب تاكل؟\nدوام العمل من 9 صباحاً لـ 1 بالليل" if lang == "ar" else "🦁 Welcome! What would you like to eat?\nWorking hours: 9 AM to 1 AM"

        sections = [{
            "title": "القائمة الرئيسية" if lang == "ar" else "Main Menu",
            "rows": [
                {
                    "id": "menu_browse",
                    "title": get_text("btn_menu", lang)[:24],
                    "description": "تصفح المطاعم والأصناف" if lang == "ar" else "Browse restaurants & items"
                },
                {
                    "id": "view_cart",
                    "title": f"{get_text('btn_cart', lang)}{cart_text}"[:24],
                    "description": "عرض سلة المشتريات" if lang == "ar" else "View your cart"
                },
                {
                    "id": "reorder",
                    "title": get_text("btn_reorder", lang)[:24],
                    "description": "أعد طلبك السابق بسرعة" if lang == "ar" else "Quickly reorder previous"
                },
                {
                    "id": "favorites",
                    "title": get_text("btn_favorites", lang)[:24],
                    "description": "مطاعمك المفضلة" if lang == "ar" else "Your favorite restaurants"
                },
                {
                    "id": "support",
                    "title": get_text("btn_support", lang)[:24],
                    "description": "تواصل معنا" if lang == "ar" else "Contact us"
                }
            ]
        }]

        await whatsapp_service.send_interactive_list(
            phone_number,
            welcome_msg,
            "اختر" if lang == "ar" else "Choose",
            sections
        )
        await redis_service.set_user_state(phone_number, "MAIN_MENU", {"lang": lang})

    async def _show_restaurant_categories(self, phone_number: str, lang: str, page: int = 0):
        """Show restaurant categories (Shawarma, Pizza, Snacks, etc.) with pagination"""
        import asyncio
        ITEMS_PER_PAGE = 9  # Leave room for navigation

        categories = None
        for attempt in range(3):
            try:
                async with AsyncSessionLocal() as db:
                    result = await db.execute(
                        select(RestaurantCategory)
                        .where(RestaurantCategory.is_active == True)
                        .order_by(RestaurantCategory.order)
                    )
                    categories = result.scalars().all()
                    break
            except Exception as e:
                logger.error(f"DB attempt {attempt+1}/3 failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(1)
                else:
                    await whatsapp_service.send_text(phone_number, "⚠️ عذراً، في مشكلة. جرب كمان مرة!")
                    await self._send_main_menu(phone_number, lang)
                    return

        if not categories:
            # Fallback to showing all restaurants if no categories exist
            await self._show_restaurants(phone_number, lang)
            return

        # Pagination
        total_categories = len(categories)
        start_idx = page * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        categories_to_show = categories[start_idx:end_idx]
        has_more = total_categories > end_idx
        has_prev = page > 0

        rows = [
            {
                "id": f"restcat_{c.id}",
                "title": f"{c.icon} {c.name_ar if lang == 'ar' else c.name}"[:24],
                "description": ""
            }
            for c in categories_to_show
        ]

        # Add navigation buttons
        if has_prev:
            rows.append({
                "id": f"restcat_page_{page - 1}",
                "title": "⬅️ السابق" if lang == 'ar' else "⬅️ Previous",
                "description": ""
            })

        if has_more:
            remaining = total_categories - end_idx
            rows.append({
                "id": f"restcat_page_{page + 1}",
                "title": "التالي ➡️" if lang == 'ar' else "Next ➡️",
                "description": f"{remaining} {'تصنيف آخر' if lang == 'ar' else 'more categories'}"
            })

        # Build page info
        total_pages = (total_categories + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        page_info = f" ({page + 1}/{total_pages})" if total_pages > 1 else ""

        sections = [{
            "title": f"{get_text('select_category', lang) if lang == 'ar' else 'Select Category'}{page_info}"[:24],
            "rows": rows
        }]

        header = "🍽️ اختر نوع المطعم:" if lang == "ar" else "🍽️ Choose restaurant type:"

        await whatsapp_service.send_interactive_list(
            phone_number,
            header,
            get_text("view_restaurants", lang),
            sections
        )
        await redis_service.set_user_state(phone_number, "BROWSING_REST_CATEGORIES", {"lang": lang, "page": page})

    async def _show_restaurants_by_category(self, phone_number: str, category_id: int, lang: str, page: int = 0):
        """Show restaurants filtered by category with pagination"""
        async with AsyncSessionLocal() as db:
            # Get category info
            cat_result = await db.execute(
                select(RestaurantCategory).where(RestaurantCategory.id == category_id)
            )
            category = cat_result.scalars().first()
            
            if not category:
                await self._show_restaurant_categories(phone_number, lang)
                return

            # Get all restaurants in this category
            result = await db.execute(
                select(Restaurant)
                .where(Restaurant.is_active == True)
                .where(Restaurant.category_id == category_id)
            )
            all_restaurants = result.scalars().all()

            if not all_restaurants:
                no_rest_msg = f"لا توجد مطاعم في قسم {category.name_ar}" if lang == "ar" else f"No restaurants in {category.name} category"
                await whatsapp_service.send_text(phone_number, no_rest_msg)
                await self._show_restaurant_categories(phone_number, lang)
                return

            cat_name = category.name_ar if lang == "ar" else category.name
            
            # Pagination: 9 items per page (leaving room for "More" option)
            items_per_page = 9
            start_idx = page * items_per_page
            end_idx = start_idx + items_per_page
            restaurants_to_show = all_restaurants[start_idx:end_idx]
            has_more = len(all_restaurants) > end_idx
            
            rows = [
                {
                    "id": f"rest_{r.id}",
                    "title": (r.name_ar if lang == 'ar' and r.name_ar else r.name)[:24],
                    "description": ((r.description_ar if lang == 'ar' and r.description_ar else r.description) or "")[:70]
                }
                for r in restaurants_to_show
            ]
            
            # Add "More" option if there are more restaurants
            if has_more:
                more_text = "المزيد ←" if lang == "ar" else "More →"
                rows.append({
                    "id": f"more_rest_{category_id}_{page + 1}",
                    "title": more_text,
                    "description": f"{len(all_restaurants) - end_idx} {'مطعم آخر' if lang == 'ar' else 'more restaurants'}"
                })
            
            sections = [{
                "title": f"{category.icon} {cat_name}"[:24],
                "rows": rows
            }]

            await whatsapp_service.send_interactive_list(
                phone_number,
                get_text("select_restaurant", lang),
                get_text("view_restaurants", lang),
                sections
            )
            await redis_service.set_user_state(phone_number, "BROWSING_RESTAURANTS", {"lang": lang, "rest_category_id": category_id, "page": page})

    async def _show_restaurants(self, phone_number: str, lang: str, page: int = 0):
        """Show available restaurants list with pagination (max 10 items per WhatsApp message)"""
        ITEMS_PER_PAGE = 9  # Leave room for "More" button

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Restaurant)
                .where(Restaurant.is_active == True)
            )
            all_restaurants = result.scalars().all()

            if not all_restaurants:
                await whatsapp_service.send_text(phone_number, get_text("no_restaurants", lang))
                await self._send_main_menu(phone_number, lang)
                return

            # Pagination
            total_restaurants = len(all_restaurants)
            start_idx = page * ITEMS_PER_PAGE
            end_idx = start_idx + ITEMS_PER_PAGE
            restaurants_to_show = all_restaurants[start_idx:end_idx]
            has_more = total_restaurants > end_idx
            has_prev = page > 0

            rows = [
                {
                    "id": f"rest_{r.id}",
                    "title": (r.name_ar if lang == 'ar' and r.name_ar else r.name)[:24],
                    "description": ((r.description_ar if lang == 'ar' and r.description_ar else r.description) or "")[:70]
                }
                for r in restaurants_to_show
            ]

            # Add navigation buttons
            if has_prev:
                rows.append({
                    "id": f"all_rest_page_{page - 1}",
                    "title": "⬅️ السابق" if lang == 'ar' else "⬅️ Previous",
                    "description": f"صفحة {page}" if lang == 'ar' else f"Page {page}"
                })

            if has_more:
                remaining = total_restaurants - end_idx
                rows.append({
                    "id": f"all_rest_page_{page + 1}",
                    "title": "التالي ➡️" if lang == 'ar' else "Next ➡️",
                    "description": f"{remaining} {'مطعم آخر' if lang == 'ar' else 'more restaurants'}"
                })

            # Build page info
            total_pages = (total_restaurants + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            page_info = f" ({page + 1}/{total_pages})" if total_pages > 1 else ""

            sections = [{
                "title": f"{get_text('restaurants', lang)}{page_info}"[:24],
                "rows": rows
            }]

            await whatsapp_service.send_interactive_list(
                phone_number,
                get_text("select_restaurant", lang),
                get_text("view_restaurants", lang),
                sections
            )
            await redis_service.set_user_state(phone_number, "BROWSING_RESTAURANTS", {"lang": lang, "page": page})

    async def _show_categories(self, phone_number: str, restaurant_id: int, lang: str, page: int = 0):
        """Show menu categories for a restaurant with pagination (max 10 items per WhatsApp message)"""
        ITEMS_PER_PAGE = 9  # Leave room for navigation

        async with AsyncSessionLocal() as db:
            # Get restaurant info
            rest_result = await db.execute(
                select(Restaurant).where(Restaurant.id == restaurant_id)
            )
            restaurant = rest_result.scalars().first()

            if not restaurant:
                await whatsapp_service.send_text(phone_number, get_text("restaurant_not_found", lang))
                await self._show_restaurants(phone_number, lang)
                return

            # Get categories
            result = await db.execute(
                select(Category)
                .join(Menu)
                .where(Menu.restaurant_id == restaurant_id)
                .where(Menu.is_active == True)
            )
            categories = result.scalars().all()

            if not categories:
                await whatsapp_service.send_text(phone_number, get_text("no_menu", lang))
                await self._show_restaurants(phone_number, lang)
                return

            # Get display name based on language
            rest_name = (restaurant.name_ar if lang == 'ar' and restaurant.name_ar else restaurant.name)

            # Pagination
            total_categories = len(categories)
            start_idx = page * ITEMS_PER_PAGE
            end_idx = start_idx + ITEMS_PER_PAGE
            categories_to_show = categories[start_idx:end_idx]
            has_more = total_categories > end_idx
            has_prev = page > 0

            rows = [
                {
                    "id": f"cat_{c.id}",
                    "title": (c.name_ar if lang == 'ar' and c.name_ar else c.name)[:24],
                    "description": ""
                }
                for c in categories_to_show
            ]

            # Add navigation buttons
            if has_prev:
                rows.append({
                    "id": f"menucat_page_{restaurant_id}_{page - 1}",
                    "title": "⬅️ السابق" if lang == 'ar' else "⬅️ Previous",
                    "description": ""
                })

            if has_more:
                remaining = total_categories - end_idx
                rows.append({
                    "id": f"menucat_page_{restaurant_id}_{page + 1}",
                    "title": "التالي ➡️" if lang == 'ar' else "Next ➡️",
                    "description": f"{remaining} {'فئة أخرى' if lang == 'ar' else 'more categories'}"
                })

            # Build page info
            total_pages = (total_categories + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            page_info = f" ({page + 1}/{total_pages})" if total_pages > 1 else ""

            sections = [{
                "title": f"{rest_name}{page_info}"[:24],
                "rows": rows
            }]

            await whatsapp_service.send_interactive_list(
                phone_number,
                f"📋 {rest_name}\n{get_text('select_category', lang)}",
                get_text("view_menu", lang),
                sections
            )
            await redis_service.set_user_state(phone_number, "BROWSING_CATEGORIES", {
                "lang": lang,
                "restaurant_id": restaurant_id,
                "restaurant_name": rest_name,
                "page": page
            })

    async def _show_menu_items(self, phone_number: str, category_id: int, lang: str, user_data: dict, page: int = 0):
        """Show menu items in a category with pagination (max 10 items per page)"""
        ITEMS_PER_PAGE = 8  # Leave room for navigation buttons

        async with AsyncSessionLocal() as db:
            # Get category with items
            result = await db.execute(
                select(Category)
                .options(selectinload(Category.items))
                .where(Category.id == category_id)
            )
            category = result.scalars().first()

            if not category or not category.items:
                await whatsapp_service.send_text(phone_number, get_text("no_items", lang))
                return

            # Filter available items
            available_items = [item for item in category.items if item.is_available]

            if not available_items:
                await whatsapp_service.send_text(phone_number, get_text("no_items_available", lang))
                return

            # Calculate pagination
            total_items = len(available_items)
            total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            start_idx = page * ITEMS_PER_PAGE
            end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)

            # Get items for current page
            page_items = available_items[start_idx:end_idx]

            # Get display names based on language
            cat_name = category.name_ar if lang == 'ar' and category.name_ar else category.name

            def get_item_name(item):
                return (item.name_ar if lang == 'ar' and item.name_ar else item.name)[:24]

            def get_item_desc(item):
                desc = item.description_ar if lang == 'ar' and hasattr(item, 'description_ar') and item.description_ar else item.description
                # Handle variant items with price range
                if hasattr(item, 'has_variants') and item.has_variants and hasattr(item, 'price_min') and item.price_min:
                    price_str = f"${item.price_min:.2f}-${item.price_max:.2f}"
                elif item.price:
                    price_str = f"${item.price:.2f}"
                else:
                    price_str = "$0.00"
                return f"💰 {price_str}" + (f" | {desc[:30]}" if desc else "")

            # Build rows for current page items
            rows = [
                {
                    "id": f"item_{item.id}",
                    "title": get_item_name(item),
                    "description": get_item_desc(item)
                }
                for item in page_items
            ]

            # Add navigation rows
            if page > 0:
                rows.append({
                    "id": f"menu_page_{category_id}_{page - 1}",
                    "title": "⬅️ السابق" if lang == 'ar' else "⬅️ Previous",
                    "description": f"صفحة {page}" if lang == 'ar' else f"Page {page}"
                })

            if page < total_pages - 1:
                rows.append({
                    "id": f"menu_page_{category_id}_{page + 1}",
                    "title": "التالي ➡️" if lang == 'ar' else "Next ➡️",
                    "description": f"صفحة {page + 2}" if lang == 'ar' else f"Page {page + 2}"
                })

            # Build section
            page_info = f" ({page + 1}/{total_pages})" if total_pages > 1 else ""
            sections = [{
                "title": f"{cat_name}{page_info}"[:24],
                "rows": rows
            }]

            # Build message with page info
            if total_pages > 1:
                body_text = f"🍽️ {cat_name}\n📄 {page + 1}/{total_pages} | {total_items} {'صنف' if lang == 'ar' else 'items'}\n{get_text('select_item', lang)}"
            else:
                body_text = f"🍽️ {cat_name}\n{get_text('select_item', lang)}"

            await whatsapp_service.send_interactive_list(
                phone_number,
                body_text,
                get_text("view_items", lang),
                sections
            )

            user_data["category_id"] = category_id
            user_data["menu_page"] = page
            await redis_service.set_user_state(phone_number, "BROWSING_ITEMS", user_data)

    async def _show_item_details(self, phone_number: str, item_id: int, lang: str, user_data: dict):
        """Show item details with add to cart option"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MenuItem).where(MenuItem.id == item_id)
            )
            item = result.scalars().first()

            if not item:
                await whatsapp_service.send_text(phone_number, get_text("item_not_found", lang))
                return

            # Get display names based on language
            item_name = item.name_ar if lang == 'ar' and item.name_ar else item.name
            item_desc = item.description_ar if lang == 'ar' and hasattr(item, 'description_ar') and item.description_ar else item.description

            # Format item details
            details = f"🍽️ *{item_name}*\n\n"
            if item_desc:
                details += f"📝 {item_desc}\n\n"
            
            # Check if item has variants (sizes)
            if hasattr(item, 'has_variants') and item.has_variants:
                # Get variants from database
                from app.models.menu import MenuItemVariant
                variants_result = await db.execute(
                    select(MenuItemVariant).where(MenuItemVariant.menu_item_id == item_id).order_by(MenuItemVariant.order)
                )
                variants = variants_result.scalars().all()
                
                if variants:
                    # Use interactive list to show ALL variants (no 3-button limit)
                    variant_rows = []
                    for v in variants:
                        v_name = v.name_ar if lang == 'ar' and v.name_ar else v.name
                        variant_rows.append({
                            "id": f"var_{v.id}_{item.id}",
                            "title": v_name[:24],
                            "description": f"💰 ${v.price:.2f}"
                        })
                    
                    sections = [{
                        "title": get_text('select_size', lang) if lang == 'ar' else 'Select Size',
                        "rows": variant_rows
                    }]
                    
                    await whatsapp_service.send_interactive_list(
                        phone_number,
                        details,
                        get_text('select_size', lang) if lang == 'ar' else 'Choose Size',
                        sections
                    )
                else:
                    # Fallback if no variants found
                    price_str = f"${item.price_min:.2f} - ${item.price_max:.2f}" if item.price_min else "$0.00"
                    details += f"💰 {get_text('price', lang)}: {price_str}"
                    await whatsapp_service.send_interactive_buttons(
                        phone_number,
                        details,
                        [
                            {"id": f"qty_1_{item.id}", "title": get_text("add_one", lang)},
                            {"id": "back_categories", "title": get_text("back", lang)}
                        ]
                    )
            else:
                # Regular item without variants
                price_str = f"${item.price:.2f}" if item.price else "$0.00"
                details += f"💰 {get_text('price', lang)}: {price_str}"
                
                await whatsapp_service.send_interactive_buttons(
                    phone_number,
                    details,
                    [
                        {"id": f"qty_1_{item.id}", "title": get_text("add_one", lang)},
                        {"id": f"qty_2_{item.id}", "title": get_text("add_two", lang)},
                        {"id": "back_categories", "title": get_text("back", lang)}
                    ]
                )
            
            user_data["viewing_item_id"] = item_id
            await redis_service.set_user_state(phone_number, "VIEWING_ITEM", user_data)

    async def _add_item_to_cart(self, phone_number: str, item_id: int, quantity: int, lang: str, user_data: dict):
        """Add item to cart - uses eager loading to avoid N+1 queries"""
        async with AsyncSessionLocal() as db:
            # Load MenuItem with category and menu in a single query (N+1 fix)
            result = await db.execute(
                select(MenuItem)
                .options(selectinload(MenuItem.category).selectinload(Category.menu))
                .where(MenuItem.id == item_id)
            )
            item = result.scalars().first()

            if not item:
                await whatsapp_service.send_text(phone_number, get_text("item_not_found", lang))
                return

            # Access eagerly loaded relationships
            menu = item.category.menu if item.category else None

            cart_item = {
                "menu_item_id": item.id,
                "name": item.name,
                "price": item.price,
                "quantity": quantity,
                "restaurant_id": menu.restaurant_id if menu else user_data.get("restaurant_id")
            }

            await redis_service.add_to_cart(phone_number, cart_item)

            # Confirmation message
            cart_count = await redis_service.get_cart_count(phone_number)
            confirm_msg = get_text("item_added", lang).format(
                quantity=quantity,
                name=item.name,
                cart_count=cart_count
            )

            await whatsapp_service.send_interactive_buttons(
                phone_number,
                f"✅ {confirm_msg}",
                [
                    {"id": "continue_shopping", "title": get_text("continue_shopping", lang)},
                    {"id": "view_cart", "title": get_text("view_cart", lang)},
                    {"id": "checkout", "title": get_text("checkout", lang)}
                ]
            )

    async def _add_variant_to_cart(self, phone_number: str, item_id: int, variant_id: int, quantity: int, lang: str, user_data: dict):
        """Add item with specific variant/size to cart"""
        async with AsyncSessionLocal() as db:
            from app.models.menu import MenuItemVariant
            
            # Get the variant
            variant_result = await db.execute(
                select(MenuItemVariant).where(MenuItemVariant.id == variant_id)
            )
            variant = variant_result.scalars().first()
            
            if not variant:
                await whatsapp_service.send_text(phone_number, get_text("item_not_found", lang))
                return
            
            # Get the menu item
            result = await db.execute(
                select(MenuItem)
                .options(selectinload(MenuItem.category))
                .where(MenuItem.id == item_id)
            )
            item = result.scalars().first()
            
            if not item:
                await whatsapp_service.send_text(phone_number, get_text("item_not_found", lang))
                return
            
            # Get restaurant_id
            menu_result = await db.execute(
                select(Menu).where(Menu.id == item.category.menu_id)
            )
            menu = menu_result.scalars().first()
            
            # Get variant display name
            variant_name = variant.name_ar if lang == 'ar' and variant.name_ar else variant.name
            item_name = item.name_ar if lang == 'ar' and item.name_ar else item.name
            
            cart_item = {
                "menu_item_id": item.id,
                "variant_id": variant.id,
                "name": f"{item_name} ({variant_name})",
                "price": variant.price,
                "quantity": quantity,
                "restaurant_id": menu.restaurant_id if menu else user_data.get("restaurant_id")
            }
            
            await redis_service.add_to_cart(phone_number, cart_item)
            
            # Confirmation message
            cart_count = await redis_service.get_cart_count(phone_number)
            confirm_msg = get_text("item_added", lang).format(
                quantity=quantity,
                name=f"{item_name} ({variant_name})",
                cart_count=cart_count
            )
            
            await whatsapp_service.send_interactive_buttons(
                phone_number,
                f"✅ {confirm_msg}",
                [
                    {"id": "continue_shopping", "title": get_text("continue_shopping", lang)},
                    {"id": "view_cart", "title": get_text("view_cart", lang)},
                    {"id": "checkout", "title": get_text("checkout", lang)}
                ]
            )

    async def _prompt_quantity(self, phone_number: str, item_id: int, lang: str, user_data: dict):
        """Prompt user for quantity"""
        await whatsapp_service.send_text(phone_number, get_text("enter_quantity", lang))
        user_data["pending_item_id"] = item_id
        await redis_service.set_user_state(phone_number, "AWAITING_QUANTITY", user_data)

    async def _process_quantity_input(self, phone_number: str, text: str, lang: str, user_data: dict):
        """Process quantity input"""
        valid, quantity = validate_quantity(text)
        if not valid:
            await whatsapp_service.send_text(phone_number, get_text("invalid_quantity", lang))
            return

        item_id = user_data.get("pending_item_id")
        if item_id:
            await self._add_item_to_cart(phone_number, item_id, quantity, lang, user_data)

    async def _show_cart(self, phone_number: str, lang: str):
        """Show cart contents"""
        cart = await redis_service.get_cart(phone_number)

        if not cart:
            await whatsapp_service.send_text(phone_number, get_text("cart_empty", lang))
            await self._send_main_menu(phone_number, lang)
            return

        cart_text = f"🛒 *{get_text('your_cart', lang)}*\n\n"
        total = 0

        for item in cart:
            price = item.get("price", 0) or 0  # Handle None
            quantity = item.get("quantity", 1)
            name = item.get("name", "Unknown")
            item_total = price * quantity  # Price is already in USD
            cart_text += f"• {name} x{quantity} = ${item_total:.2f}\n"
            total += item_total

        cart_text += f"\n💰 *{get_text('total', lang)}: ${total:.2f}*"

        await whatsapp_service.send_interactive_buttons(
            phone_number,
            cart_text,
            [
                {"id": "checkout", "title": get_text("checkout", lang)},
                {"id": "clear_cart", "title": get_text("clear_cart", lang)},
                {"id": "continue_shopping", "title": get_text("add_more", lang)}
            ]
        )
        await redis_service.set_user_state(phone_number, "VIEWING_CART", {"lang": lang})

    async def _show_cart_edit_options(self, phone_number: str, lang: str):
        """Show cart items for editing"""
        cart = await redis_service.get_cart(phone_number)

        if not cart:
            await whatsapp_service.send_text(phone_number, get_text("cart_empty", lang))
            return

        sections = [{
            "title": get_text("select_to_edit", lang),
            "rows": [
                {
                    "id": f"edit_item_{item.get('menu_item_id', 0)}",
                    "title": f"{item.get('name', 'Item')[:20]} x{item.get('quantity', 1)}",
                    "description": f"${float(item.get('price', 0) * item.get('quantity', 1)):.2f}"
                }
                for item in cart
            ]
        }]

        await whatsapp_service.send_interactive_list(
            phone_number,
            get_text("edit_cart", lang),
            get_text("select_item", lang),
            sections
        )

    async def _start_checkout(self, phone_number: str, lang: str):
        """Start checkout process"""
        logger.debug(f"Starting checkout for {phone_number}")
        cart = await redis_service.get_cart(phone_number)
        if not cart:
            logger.debug(f"Cart empty for {phone_number}")
            await whatsapp_service.send_text(phone_number, get_text("cart_empty", lang))
            await self._send_main_menu(phone_number, lang)
            return

        async with AsyncSessionLocal() as db:
            logger.debug(f"Checking user persistence for {phone_number}")
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()

            if user and user.default_address and user.full_name and user.full_name != "WhatsApp Customer":
                logger.debug(f"Found persistent user info for {phone_number}")
                # Offer to use previous info
                msg = get_text("confirm_name_address", lang).format(
                    name=user.full_name,
                    address=user.default_address
                )
                buttons = [
                    {"id": "use_previous_info", "title": get_text("btn_use_previous", lang)},
                    {"id": "enter_new_info", "title": get_text("btn_enter_new", lang)}
                ]
                await whatsapp_service.send_interactive_buttons(phone_number, msg, buttons)
                await redis_service.set_user_state(phone_number, "CONFIRMING_INFO", {"lang": lang})
            else:
                logger.debug(f"No persistent info for {phone_number}, asking for location")
                # Ask for location first
                await whatsapp_service.send_text(phone_number, get_text("share_location", lang))
                await redis_service.set_user_state(phone_number, "AWAITING_LOCATION", {"lang": lang})

    async def _process_previous_info(self, phone_number: str, lang: str, user_data: dict):
        """Use stored user info for checkout"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()
            if not user:
                await self._start_checkout(phone_number, lang)
                return
            
            # Map user to session data
            user_data.update({
                "customer_name": user.full_name,
                "delivery_address": user.default_address,
                "delivery_lat": user.last_latitude,
                "delivery_lng": user.last_longitude
            })
            
            await self._create_order(phone_number, lang, user_data)

    async def _create_order(self, phone_number: str, lang: str, user_data: dict):
        """Create order in database and persist user data"""
        cart = await redis_service.get_cart(phone_number)
        if not cart:
            await whatsapp_service.send_text(phone_number, get_text("cart_empty", lang))
            return

        lat = user_data.get("delivery_lat")
        lng = user_data.get("delivery_lng")
        address = user_data.get("delivery_address", "WhatsApp Order")
        name = user_data.get("customer_name", "WhatsApp Customer")

        async with AsyncSessionLocal() as db:
            # Find or create user
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()

            if not user:
                user = User(phone_number=phone_number, full_name=name)
                db.add(user)
            else:
                user.full_name = name
            
            # Persist info
            user.default_address = address
            if lat and lng:
                user.last_latitude = lat
                user.last_longitude = lng
            
            await db.commit()
            await db.refresh(user)

            # Calculate totals
            total_amount = sum(item["price"] * item["quantity"] for item in cart)
            delivery_fee = await self._calculate_delivery_fee(lat, lng, cart[0].get("restaurant_id"))
            restaurant_id = cart[0].get("restaurant_id") or user_data.get("restaurant_id") or 1

            # Create order
            order = Order(
                restaurant_id=restaurant_id,
                user_id=user.id,
                status=OrderStatus.NEW,
                total_amount=total_amount,
                delivery_fee=delivery_fee,
                latitude=lat,
                longitude=lng,
                address=address
            )
            db.add(order)
            await db.commit()
            await db.refresh(order)

            # Add order items
            for item in cart:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item.get("menu_item_id", 1),
                    quantity=item["quantity"],
                    unit_price=item["price"],
                    total_price=item["price"] * item["quantity"]
                )
                db.add(order_item)

            await db.commit()

            # Clear cart
            await redis_service.clear_cart(phone_number)

            # Build items list for confirmation message
            # Note: prices in DB are already in USD
            items_text = []
            for item in cart:
                item_name = item.get("name", item.get("name_ar", "Item"))
                item_qty = item.get("quantity", 1)
                item_price = float(item.get("price", 0))  # Already USD
                item_total = item_price * item_qty
                items_text.append(f"• {item_qty}x {item_name} - ${item_total:.2f}")
            items_str = "\n".join(items_text)

            # Send confirmation
            # total_amount is already in USD (from cart prices)
            # delivery_fee is in LBP (from _calculate_delivery_fee)
            subtotal_usd = float(total_amount)  # Already USD
            delivery_usd = lbp_to_usd(delivery_fee)  # Convert LBP to USD
            order_msg = get_text("order_confirmed", lang).format(
                order_id=order.id,
                items=items_str,
                subtotal=subtotal_usd,
                total=subtotal_usd + delivery_usd,
                delivery_fee=delivery_usd
            )
            await whatsapp_service.send_text(phone_number, f"🎉 {order_msg}")

            # Notify restaurant
            await self._notify_restaurant(order, cart, lat, lng)

            # Check if should suggest favorite
            try:
                await self._check_and_suggest_favorite(phone_number, restaurant_id, lang)
            except Exception as e:
                logger.error(f"Failed to check favorite suggestion: {e}")

            # Schedule review request (in production, this would be a delayed task)
            # For now, we'll store it and send after order status changes to delivered
            restaurant_name = ""
            try:
                rest_result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
                restaurant = rest_result.scalars().first()
                if restaurant:
                    restaurant_name = restaurant.name
            except:
                pass

            # Send push notification to admin app
            try:
                await fcm_service.notify_admins_new_order(
                    order_id=order.id,
                    restaurant_name=restaurant_name or "مطعم",
                    total_amount=float(total_amount),
                    restaurant_id=restaurant_id,
                )
            except Exception as e:
                logger.error(f"Failed to send push notification: {e}")

            await redis_service.set_user_state(phone_number, "ORDER_PLACED", {
                "lang": lang,
                "order_id": order.id,
                "restaurant_name": restaurant_name
            })

    async def _notify_restaurant(self, order: Order, cart: list, lat: float, lng: float):
        """Send notification to restaurant about new order via WhatsApp"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Restaurant).where(Restaurant.id == order.restaurant_id)
            )
            restaurant = result.scalars().first()

            if not restaurant:
                logger.warning(f"Restaurant {order.restaurant_id} not found for order {order.id}")
                return

            # Prepare order summary
            items_text = "\n".join([f"• {item['name']} x{item['quantity']}" for item in cart])
            total_usd = float(order.total_amount or 0)  # Already USD
            delivery_usd = lbp_to_usd(order.delivery_fee or 0)  # Convert LBP to USD
            grand_total_usd = total_usd + delivery_usd
            notification = f"""🔔 *طلب جديد #{order.id}*

🏪 *{restaurant.name}*

📦 *الأصناف:*
{items_text}

💰 *المجموع:* ${total_usd:.2f}
🚗 *رسوم التوصيل:* ${delivery_usd:.2f}
💵 *الإجمالي:* ${grand_total_usd:.2f}

📍 *موقع التوصيل:*
https://maps.google.com/?q={lat},{lng}

💳 *طريقة الدفع:* الدفع عند الاستلام

⏰ الرجاء قبول الطلب في أقرب وقت!"""

            # Send WhatsApp notification to restaurant if phone number exists
            if restaurant.phone_number:
                try:
                    await whatsapp_service.send_text(restaurant.phone_number, notification)
                    logger.info(f"WhatsApp notification sent to restaurant {restaurant.name} ({restaurant.phone_number}) for order {order.id}")
                except Exception as e:
                    logger.error(f"Failed to send WhatsApp to restaurant: {e}")
            else:
                logger.warning(f"Restaurant {restaurant.name} has no phone number for notifications")

            # Publish to Redis for real-time updates (for mobile app)
            await redis_service.publish_restaurant_notification(
                order.restaurant_id,
                {
                    "type": "new_order",
                    "order_id": order.id,
                    "total": order.total_amount,
                    "items_count": len(cart),
                    "delivery_location": {"lat": lat, "lng": lng}
                }
            )

            # Send FCM push notification to admin app
            try:
                await fcm_service.send_to_topic(
                    topic="admin_orders",
                    title="🛒 طلب جديد!",
                    body=f"طلب #{order.id} من {restaurant.name} - ${float(order.total_amount or 0):.2f}",
                    data={
                        "type": "new_order",
                        "order_id": str(order.id),
                        "restaurant_id": str(order.restaurant_id),
                        "restaurant_name": restaurant.name or "",
                        "total": str(order.total_amount),
                    }
                )
                logger.info(f"FCM notification sent to admin_orders topic for order {order.id}")
            except Exception as e:
                logger.error(f"Failed to send FCM notification: {e}")

            logger.info(f"Restaurant {order.restaurant_id} notified about order {order.id}")

    async def _calculate_delivery_fee(self, lat: float, lng: float, restaurant_id: int) -> float:
        """Calculate delivery fee based on distance (returns LBP)"""
        # TODO: Implement proper distance calculation using Google Maps API
        # For now, return a flat fee from constants
        return DEFAULT_DELIVERY_FEE_LBP

    async def _start_support(self, phone_number: str, lang: str):
        """Start support chat mode"""
        await whatsapp_service.send_interactive_buttons(
            phone_number,
            get_text("support_message", lang),
            [
                {"id": "end_support", "title": get_text("end_support", lang)},
                {"id": "back_main", "title": get_text("back_to_menu", lang)}
            ]
        )
        await redis_service.set_user_state(phone_number, "SUPPORT_CHAT", {"lang": lang})

    async def _handle_support_message(self, phone_number: str, text: str, lang: str):
        """Handle support message - log it and acknowledge"""
        logger.info(f"Support message from {phone_number}: {text}")
        await whatsapp_service.send_text(
            phone_number,
            get_text("support_received", lang)
        )

    async def _process_ai_order(self, phone_number: str, text: str, lang: str, user_data: dict):
        """Process natural language with smart AI - handles search, order, and discovery intents"""

        # Rate limiting check (30 AI calls per minute per user)
        if not await redis_service.check_rate_limit(phone_number, "ai", limit=30, window=60):
            rate_limit_msg = "⚠️ عم تبعت رسائل كتير بسرعة! انطر شوي وجرب كمان مرة 🙏" if lang == "ar" else "⚠️ Too many requests! Please wait a moment and try again."
            await whatsapp_service.send_text(phone_number, rate_limit_msg)
            return

        # Send processing message with marketing flair
        processing_msg = "🔍 عم دور لك..." if lang == "ar" else "🔍 Searching for you..."
        await whatsapp_service.send_text(phone_number, processing_msg)

        # Save user message to conversation memory
        await self._save_to_conversation(phone_number, "user", text, {
            "restaurant_id": user_data.get("restaurant_id"),
            "state": "AI_PROCESSING"
        })

        # Get conversation history for context
        conversation_history = await self._get_conversation_context(phone_number)

        # Get selected restaurant if any
        restaurant_id = user_data.get("restaurant_id")

        # Get current cart items for context
        cart_items = await redis_service.get_cart(phone_number)

        # Process with smart AI including conversation context and cart
        ai_result = await ai_service.process_smart_order(
            text, lang, restaurant_id, user_data, conversation_history, cart_items
        )

        intent = ai_result.get("intent", "error")
        ai_message = ai_result.get("message", "")

        # Save AI response to conversation memory
        await self._save_to_conversation(phone_number, "assistant", ai_message, {
            "intent": intent,
            "search_results": ai_result.get("matching_restaurants", [])[:3] if ai_result.get("matching_restaurants") else None
        })

        # Track AI usage for analytics
        await redis_service.track_ai_usage(phone_number, intent, ai_result.get("success", False))

        # Handle sentiment
        sentiment = ai_result.get("sentiment", "neutral")
        if sentiment == "negative":
            sorry_msg = "نعتذر عن أي إزعاج! 🙏 إذا بدك تحكي مع الإدارة اتصل على 71234567" if lang == "ar" else "We apologize for any inconvenience! 🙏 Contact management at 71234567"
            await whatsapp_service.send_text(phone_number, sorry_msg)
        elif sentiment == "positive":
            thanks_msg = "شكراً لطيبتك! 😊🦁" if lang == "ar" else "Thank you! 😊🦁"
            await whatsapp_service.send_text(phone_number, thanks_msg)
        
        # Handle different intents
        if intent == "search_product":
            # Show restaurants that have this product
            await self._handle_product_search(phone_number, ai_result, lang)
            
        elif intent == "discover_category":
            # Show restaurants in this category
            await self._handle_category_discovery(phone_number, ai_result, lang)
            
        elif intent == "order_item":
            # Check for reference resolution (e.g., "من الأول")
            reference_position = ai_result.get("reference_position")
            if reference_position:
                # Get search results from conversation context
                conv = await redis_service.get_conversation(phone_number)
                context = conv.get("context", {}) if conv else {}
                search_results = context.get("search_results", [])

                if search_results and reference_position <= len(search_results):
                    # Get referenced restaurant
                    ref_restaurant = search_results[reference_position - 1]
                    restaurant_id = ref_restaurant.get("id")
                    if restaurant_id:
                        # Show categories for this restaurant
                        await self._show_categories(phone_number, restaurant_id, lang)
                        return

            # Add items to cart
            await self._handle_order_intent(phone_number, ai_result, lang, user_data)
            
        elif intent == "greeting":
            # Friendly greeting response
            greeting = ai_message or "أهلا وسهلا! شو بنقدر نساعدك؟ 😊"
            await whatsapp_service.send_text(phone_number, greeting)
            await self._send_main_menu(phone_number, lang)
            
        elif intent == "ask_question":
            # Answer question and show menu
            answer = ai_message or "كيف بقدر ساعدك؟ 🤔"
            await whatsapp_service.send_text(phone_number, answer)
            await self._send_main_menu(phone_number, lang)

        elif intent == "reorder":
            # User wants to repeat previous order
            await self._show_previous_orders(phone_number, lang)

        elif intent == "modify_cart":
            # User wants to modify cart (remove/change items)
            await self._handle_cart_modification(phone_number, ai_result, lang)

        elif intent == "one_shot_order":
            # Complete order in one sentence (items + restaurant + address)
            await self._handle_one_shot_order(phone_number, ai_result, lang, user_data)

        elif intent == "request_menu":
            # User wants to see a restaurant's full menu
            await self._handle_menu_request(phone_number, ai_result, lang)

        elif intent == "search_description":
            # User searching by description (cold, hot, sweet, etc.)
            await self._handle_description_search(phone_number, ai_result, lang)

        else:
            # Error or unknown intent - provide smart recovery
            await self._handle_ai_error_recovery(phone_number, text, ai_result, lang)

    async def _handle_ai_error_recovery(self, phone_number: str, original_text: str, ai_result: dict, lang: str):
        """Smart error recovery with intelligent suggestions"""
        ai_message = ai_result.get("message", "")

        # Try to find similar products using multiple strategies
        suggestions = []
        restaurants_found = []

        try:
            async with AsyncSessionLocal() as db:
                # Strategy 1: Search for similar items by name
                words = [w for w in original_text.lower().split() if len(w) > 2]

                # Get all items for searching
                result = await db.execute(
                    select(MenuItem, Restaurant)
                    .join(Category, MenuItem.category_id == Category.id)
                    .join(Menu, Category.menu_id == Menu.id)
                    .join(Restaurant, Menu.restaurant_id == Restaurant.id)
                    .where(MenuItem.is_available == True)
                    .where(Restaurant.is_active == True)
                )
                all_items = result.all()

                # Score-based matching
                scored_items = []
                for item, rest in all_items:
                    item_name = (item.name_ar or item.name or "").lower()
                    item_desc = (item.description_ar or item.description or "").lower()
                    rest_name = (rest.name_ar or rest.name or "").lower()

                    score = 0
                    for word in words:
                        if word in item_name:
                            score += 10  # High score for name match
                        if word in item_desc:
                            score += 5   # Medium for description
                        if word in rest_name:
                            score += 3   # Low for restaurant name

                    if score > 0:
                        scored_items.append({
                            "id": item.id,
                            "name": item.name_ar or item.name,
                            "restaurant": rest.name_ar or rest.name,
                            "restaurant_id": rest.id,
                            "price": float(item.price) if item.price else 0,
                            "score": score
                        })

                # Sort by score and take top results
                scored_items.sort(key=lambda x: x["score"], reverse=True)
                suggestions = scored_items[:8]

                # Strategy 2: If no suggestions, check if it's a restaurant name
                if not suggestions:
                    rest_result = await db.execute(
                        select(Restaurant)
                        .where(Restaurant.is_active == True)
                    )
                    all_restaurants = rest_result.scalars().all()

                    for rest in all_restaurants:
                        rest_name_ar = (rest.name_ar or "").lower()
                        rest_name_en = (rest.name or "").lower()
                        for word in words:
                            if word in rest_name_ar or word in rest_name_en:
                                restaurants_found.append({
                                    "id": rest.id,
                                    "name": rest.name_ar or rest.name
                                })
                                break

        except Exception as e:
            logger.error(f"Error finding suggestions: {e}")

        # Build response based on what we found
        if suggestions:
            # Group by restaurant
            by_restaurant = {}
            for s in suggestions:
                rest = s["restaurant"]
                if rest not in by_restaurant:
                    by_restaurant[rest] = []
                if len(by_restaurant[rest]) < 3:  # Max 3 per restaurant
                    by_restaurant[rest].append(s)

            # Build interactive list (max 9 rows total for WhatsApp limit)
            sections = []
            total_rows = 0
            MAX_ROWS = 9
            for rest_name, items in list(by_restaurant.items()):
                if total_rows >= MAX_ROWS:
                    break
                rows = []
                for item in items:
                    if total_rows >= MAX_ROWS:
                        break
                    price_str = f"${item['price']:.2f}" if item['price'] else ""
                    rows.append({
                        "id": f"item_{item['id']}",
                        "title": item["name"][:24],
                        "description": f"💰 {price_str}" if price_str else ""
                    })
                    total_rows += 1
                if rows:
                    sections.append({
                        "title": rest_name[:24],
                        "rows": rows
                    })

            header = f"🤔 ما لقيت '{original_text}' بالضبط\n\n"
            header += "💡 بس ممكن تقصد:" if lang == "ar" else "Did you mean:"

            # Store suggestions in context
            await redis_service.update_conversation_context(phone_number, {
                "suggestions": suggestions[:5]
            })

            await whatsapp_service.send_interactive_list(
                phone_number,
                header,
                "اختار 👆" if lang == "ar" else "Select",
                sections
            )

        elif restaurants_found:
            # Found matching restaurants
            header = f"🔍 لقيت مطاعم قريبة من '{original_text}':"

            sections = [{
                "title": "🏪 مطاعم" if lang == "ar" else "Restaurants",
                "rows": [
                    {
                        "id": f"rest_{r['id']}",
                        "title": r["name"][:24],
                        "description": "عرض المانيو" if lang == "ar" else "View menu"
                    }
                    for r in restaurants_found[:5]
                ]
            }]

            await whatsapp_service.send_interactive_list(
                phone_number,
                header,
                "اختار 👆" if lang == "ar" else "Select",
                sections
            )

        else:
            # Nothing found - provide helpful message
            helpful_messages = {
                "ar": [
                    "🤔 ما فهمت عليك...",
                    "",
                    "💡 *جرب تقول:*",
                    "• \"بدي شاورما\" - للبحث عن صنف",
                    "• \"ابعتلي مانيو غسان\" - لعرض قائمة مطعم",
                    "• \"شو في برغر\" - للبحث عن مطاعم",
                    "• \"بدي شي بارد\" - للبحث بالوصف",
                    "",
                    "او اختار من القائمة 👇"
                ],
                "en": [
                    "🤔 I didn't understand...",
                    "",
                    "💡 *Try saying:*",
                    "• \"I want shawarma\" - to search",
                    "• \"Send me Ghasan menu\" - to view menu",
                    "• \"What burgers do you have\" - to browse",
                    "",
                    "Or choose from the menu 👇"
                ]
            }

            await whatsapp_service.send_text(phone_number, "\n".join(helpful_messages.get(lang, helpful_messages["ar"])))
            await self._send_main_menu(phone_number, lang)

    async def _handle_product_search(self, phone_number: str, ai_result: dict, lang: str):
        """Handle search_product intent - show restaurants with this product"""
        restaurants = ai_result.get("matching_restaurants", [])
        product = ai_result.get("product_query", "")
        ai_message = ai_result.get("message", "")
        
        if not restaurants:
            no_result = ai_message or f"ما لقيت {product} بالمطاعم 😕 جرب شي ثاني!"
            await whatsapp_service.send_text(phone_number, no_result)
            await self._show_restaurant_categories(phone_number, lang)
            return
        
        # Build header message
        header = ai_message or f"🔥 لقيتلك {len(restaurants)} مطعم عندهم {product}!"
        
        # Build interactive list (max 9 rows for WhatsApp limit)
        sections = [{
            "title": f"🏪 مطاعم فيها {product}"[:24] if lang == "ar" else f"Restaurants with {product}"[:24],
            "rows": [
                {
                    "id": f"rest_{r['id']}",
                    "title": r['name'][:24],
                    "description": f"{r.get('items_count', '')} أصناف متوفرة" if r.get('items_count') else ""
                }
                for r in restaurants[:9]
            ]
        }]
        
        await whatsapp_service.send_interactive_list(
            phone_number,
            header,
            "🔍 اختار مطعم" if lang == "ar" else "Choose Restaurant",
            sections
        )
        
        await redis_service.set_user_state(phone_number, "BROWSING_RESTAURANTS", {
            "lang": lang,
            "search_query": product
        })

    async def _handle_category_discovery(self, phone_number: str, ai_result: dict, lang: str):
        """Handle discover_category intent - show restaurants in category"""
        restaurants = ai_result.get("matching_restaurants", [])
        category = ai_result.get("category_query", "")
        ai_message = ai_result.get("message", "")
        
        if not restaurants:
            no_result = ai_message or f"ما في مطاعم ب{category} هلق 😕"
            await whatsapp_service.send_text(phone_number, no_result)
            await self._show_restaurant_categories(phone_number, lang)
            return
        
        header = ai_message or f"🍽️ عنا {len(restaurants)} مطعم ب{category}!"
        
        sections = [{
            "title": f"🏪 {category}"[:24],
            "rows": [
                {
                    "id": f"rest_{r['id']}",
                    "title": r['name'][:24],
                    "description": ""
                }
                for r in restaurants[:9]
            ]
        }]
        
        await whatsapp_service.send_interactive_list(
            phone_number,
            header,
            "🔍 اختار مطعم" if lang == "ar" else "Choose Restaurant",
            sections
        )
        
        await redis_service.set_user_state(phone_number, "BROWSING_RESTAURANTS", {"lang": lang})

    async def _handle_order_intent(self, phone_number: str, ai_result: dict, lang: str, user_data: dict):
        """Handle order_item intent - add to cart and suggest upsells"""
        items = ai_result.get("items", [])
        unmatched = ai_result.get("unmatched", [])
        ai_message = ai_result.get("message", "")
        restaurant_id = ai_result.get("restaurant_id")
        upsell_suggestions = ai_result.get("upsell_suggestions", [])

        if not items:
            # No items matched - redirect to search
            if ai_result.get("matching_restaurants"):
                await self._handle_product_search(phone_number, ai_result, lang)
            else:
                error = "ما لقيت الصنف، اختار من القائمة! 🍽️"
                await whatsapp_service.send_text(phone_number, error)
                await self._show_restaurant_categories(phone_number, lang)
            return

        # Validate items - must have menu_item_id and price > 0
        valid_items = []
        invalid_items = []
        for item in items:
            if item.get("menu_item_id") and item.get("price", 0) > 0:
                valid_items.append(item)
            else:
                invalid_items.append(item.get("name", ""))

        # If no valid items, show error and alternatives
        if not valid_items:
            product_query = items[0].get("name", "") if items else ""
            restaurants = await ai_service._find_restaurants_with_product(product_query)

            if restaurants:
                # Show restaurants that have this product
                error_msg = f"⚠️ ما لقيت '{product_query}' بالمطعم المطلوب\n\n🔍 بس لقيتو بهالمطاعم:"
                await whatsapp_service.send_text(phone_number, error_msg)
                ai_result["matching_restaurants"] = restaurants
                ai_result["product_query"] = product_query
                await self._handle_product_search(phone_number, ai_result, lang)
            else:
                await whatsapp_service.send_text(phone_number, f"⚠️ ما لقيت '{product_query}' بأي مطعم 🤔\nجرب شي تاني!")
                await self._show_restaurant_categories(phone_number, lang)
            return

        # Add only valid items to cart
        added_items = []
        for item in valid_items:
            await redis_service.add_to_cart(phone_number, item)
            added_items.append(f"{item['quantity']}x {item['name']}")
        
        # Calculate totals
        cart_total = await redis_service.get_cart_total(phone_number)
        cart_count = await redis_service.get_cart_count(phone_number)
        
        # Build response with Lebanese marketing flair
        confirmations = ["تكرم عينك! ✅", "على راسي! 👍", "حاضر! 🙌", "بالخدمة! ✨"]
        import random
        header = ai_message or random.choice(confirmations)
        
        response = f"{header}\n\n"
        response += "🛒 *الأصناف المضافة:*\n"
        response += "\n".join([f"  • {item}" for item in added_items])
        cart_total_usd = float(cart_total)  # Already USD
        response += f"\n\n💰 *المجموع:* ${cart_total_usd:.2f}"
        response += f"\n📦 *عدد الأصناف:* {cart_count}"
        
        if unmatched:
            response += f"\n\n⚠️ *ما لقيت:* {', '.join(unmatched)}"
        
        await whatsapp_service.send_text(phone_number, response)
        
        # Update state
        await redis_service.set_user_state(phone_number, "MAIN_MENU", {
            "lang": lang,
            "restaurant_id": restaurant_id
        })
        
        # Show upsell suggestions if available
        if upsell_suggestions and restaurant_id:
            await self._show_upsell_suggestions(phone_number, upsell_suggestions, lang, restaurant_id)
        else:
            # Regular action buttons
            buttons = [
                {"id": "checkout", "title": get_text("checkout", lang)},
                {"id": "view_cart", "title": get_text("view_cart", lang)},
                {"id": "add_more", "title": get_text("continue_shopping", lang)}
            ]
            
            await whatsapp_service.send_interactive_buttons(
                phone_number,
                "صحتين وعافية! شو بدك تعمل هلق؟ 😋" if lang == "ar" else "What would you like to do now?",
                buttons
            )

    async def _show_upsell_suggestions(self, phone_number: str, suggestions: list, lang: str, restaurant_id: int):
        """Show upsell suggestions after adding items"""
        # Get actual menu items for upsell
        upsell_items = await ai_service.get_upsell_suggestions(restaurant_id, [])
        
        if upsell_items:
            header = "🔥 شو رأيك تضيف كمان؟" if lang == "ar" else "Would you like to add?"
            
            # Show as buttons (max 3)
            buttons = [
                {"id": f"qty_1_{item['id']}", "title": f"{item['name'][:15]} ${float(item['price']):.1f}"}
                for item in upsell_items[:2]
            ]
            buttons.append({"id": "skip_upsell", "title": "✅ لا شكراً" if lang == "ar" else "No thanks"})
            
            await whatsapp_service.send_interactive_buttons(phone_number, header, buttons)
        else:
            # Regular checkout prompt
            buttons = [
                {"id": "checkout", "title": get_text("checkout", lang)},
                {"id": "view_cart", "title": get_text("view_cart", lang)},
                {"id": "add_more", "title": get_text("continue_shopping", lang)}
            ]
            await whatsapp_service.send_interactive_buttons(
                phone_number,
                "صحتين! شو بدك تعمل؟ 😋" if lang == "ar" else "What next?",
                buttons
            )

    async def _confirm_order(self, phone_number: str, lang: str, user_data: dict):
        """Process definitive order confirmation"""
        await self._create_order(phone_number, lang, user_data)

    async def _handle_cart_modification(self, phone_number: str, ai_result: dict, lang: str):
        """Handle AI-detected cart modification intent"""
        items = ai_result.get("items", [])
        ai_message = ai_result.get("message", "")

        if not items:
            await whatsapp_service.send_text(phone_number, ai_message or "ما فهمت شو بدك تعدل 🤔")
            await self._show_cart(phone_number, lang)
            return

        cart = await redis_service.get_cart(phone_number)
        if not cart:
            await whatsapp_service.send_text(phone_number, get_text("cart_empty", lang))
            await self._send_main_menu(phone_number, lang)
            return

        modifications_made = []

        for mod_item in items:
            action = mod_item.get("action", "remove")
            item_name = mod_item.get("name", "").lower()
            new_size = mod_item.get("size", "").lower() if mod_item.get("size") else None

            # Handle clear all cart
            if action == "clear" or item_name == "all":
                await redis_service.clear_cart(phone_number)
                modifications_made.append("🗑️ تم تفضيت السلة")
                continue

            # Handle replace action (size or type change)
            replace_type = mod_item.get("replace_type", "").lower() if mod_item.get("replace_type") else None
            replace_with = mod_item.get("replace_with", "").lower() if mod_item.get("replace_with") else None

            # Handle replace_item (replace with different product)
            if action == "replace_item" and replace_with:
                target_item = None
                # If name is generic (آخر صنف), get last item in cart
                if "آخر" in item_name or not item_name or item_name == "آخر صنف مضاف":
                    target_item = cart[-1] if cart else None
                else:
                    for cart_item in cart:
                        cart_item_name = cart_item.get("name", "").lower()
                        if item_name in cart_item_name or cart_item_name in item_name:
                            target_item = cart_item
                            break

                if target_item:
                    old_name = target_item.get("name", "")
                    old_menu_item_id = target_item.get("menu_item_id")
                    restaurant_id = target_item.get("restaurant_id")
                    quantity = target_item.get("quantity", 1)

                    # Find the new item by name
                    new_item = await self._find_item_by_name(replace_with, restaurant_id)

                    if new_item:
                        await redis_service.remove_from_cart(phone_number, old_menu_item_id)
                        new_item["quantity"] = quantity
                        await redis_service.add_to_cart(phone_number, new_item)
                        modifications_made.append(f"🔄 غيرنا {old_name} ← {new_item['name']}")
                    else:
                        modifications_made.append(f"⚠️ ما لقيت {replace_with} بنفس المطعم")
                        ai_message = None
                continue

            if action == "replace" and (new_size or replace_type):
                target_item = None
                # If name is generic (آخر صنف), get last item in cart
                if "آخر" in item_name or not item_name or item_name == "آخر صنف مضاف":
                    target_item = cart[-1] if cart else None
                else:
                    for cart_item in cart:
                        cart_item_name = cart_item.get("name", "").lower()
                        if item_name in cart_item_name or cart_item_name in item_name:
                            target_item = cart_item
                            break

                if target_item:
                    old_name = target_item.get("name", "")
                    old_menu_item_id = target_item.get("menu_item_id")
                    restaurant_id = target_item.get("restaurant_id")
                    quantity = target_item.get("quantity", 1)

                    new_item = None
                    if new_size:
                        # Find item with new size
                        new_item = await self._find_item_with_size(old_name, new_size, restaurant_id)
                    elif replace_type:
                        # Find item with different type (e.g., chicken → meat)
                        new_item = await self._find_item_with_type(old_name, replace_type, restaurant_id)

                    if new_item:
                        await redis_service.remove_from_cart(phone_number, old_menu_item_id)
                        new_item["quantity"] = quantity
                        await redis_service.add_to_cart(phone_number, new_item)
                        modifications_made.append(f"🔄 غيرنا {old_name} ← {new_item['name']}")
                    else:
                        search_term = new_size if new_size else replace_type
                        modifications_made.append(f"⚠️ ما لقيت {search_term} بدل {old_name}")
                        # Clear AI message on failure so we show the actual error
                        ai_message = None
                continue

            # Handle decrease on "آخر صنف مضاف" (last item)
            if action == "decrease" and ("آخر" in item_name or item_name == "آخر صنف مضاف"):
                if cart:
                    target_item = cart[-1]
                    qty_to_remove = mod_item.get("quantity", 1)
                    new_qty = target_item.get("quantity", 1) - qty_to_remove
                    if new_qty <= 0:
                        await redis_service.remove_from_cart(phone_number, target_item.get("menu_item_id"))
                        modifications_made.append(f"❌ شلنا {target_item.get('name')}")
                    else:
                        await redis_service.update_cart_item_quantity(
                            phone_number, target_item.get("menu_item_id"), new_qty
                        )
                        modifications_made.append(f"➖ نقصنا {target_item.get('name')} ({new_qty})")
                continue

            for cart_item in cart:
                cart_item_name = cart_item.get("name", "").lower()
                if item_name in cart_item_name or cart_item_name in item_name:
                    if action == "remove":
                        await redis_service.remove_from_cart(phone_number, cart_item.get("menu_item_id"))
                        modifications_made.append(f"❌ شلنا {cart_item.get('name')}")
                    elif action == "increase":
                        new_qty = cart_item.get("quantity", 1) + mod_item.get("quantity", 1)
                        await redis_service.update_cart_item_quantity(
                            phone_number, cart_item.get("menu_item_id"), new_qty
                        )
                        modifications_made.append(f"➕ زدنا {cart_item.get('name')} ({new_qty})")
                    elif action == "decrease":
                        new_qty = cart_item.get("quantity", 1) - mod_item.get("quantity", 1)
                        if new_qty <= 0:
                            await redis_service.remove_from_cart(phone_number, cart_item.get("menu_item_id"))
                            modifications_made.append(f"❌ شلنا {cart_item.get('name')}")
                        else:
                            await redis_service.update_cart_item_quantity(
                                phone_number, cart_item.get("menu_item_id"), new_qty
                            )
                            modifications_made.append(f"➖ نقصنا {cart_item.get('name')} ({new_qty})")
                    break

        if modifications_made:
            response = ai_message or "تم! ✅\n" + "\n".join(modifications_made)
            await whatsapp_service.send_text(phone_number, response)
        else:
            await whatsapp_service.send_text(phone_number, "ما لقيت هالصنف بالسلة 🤔")

        await self._show_cart(phone_number, lang)

    async def _find_item_with_size(self, current_name: str, target_size: str, restaurant_id: int) -> Optional[dict]:
        """Find a menu item with different size - supports both name-based and variant-based sizes"""
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

                # Size words to strip for base name comparison
                size_words = ["صغير", "كبير", "وسط", "small", "medium", "large", "صغيرة", "كبيرة", "وسطى"]

                # Size mapping
                size_map = {
                    "small": ["small", "s", "صغير", "صغيرة"],
                    "medium": ["medium", "m", "وسط", "متوسط"],
                    "large": ["large", "l", "كبير", "كبيرة"],
                }

                # Normalize target size
                target_normalized = target_size.lower()
                for key, variants in size_map.items():
                    if target_normalized in variants:
                        target_normalized = key
                        break

                # Clean up current name - remove size words and variant info
                base_name = current_name.lower()
                # Remove (Large), (Small), etc.
                import re
                base_name = re.sub(r'\([^)]*\)', '', base_name).strip()
                for sw in size_words:
                    base_name = base_name.replace(sw, "").strip()

                # First, try to find item with variants
                for item in menu_items:
                    item_name = (item.name_ar or item.name or "").lower()
                    item_base = re.sub(r'\([^)]*\)', '', item_name).strip()
                    for sw in size_words:
                        item_base = item_base.replace(sw, "").strip()

                    if base_name in item_base or item_base in base_name:
                        # Check if this item has variants
                        if hasattr(item, 'has_variants') and item.has_variants:
                            from app.models.menu import MenuItemVariant
                            variants_result = await db.execute(
                                select(MenuItemVariant)
                                .where(MenuItemVariant.menu_item_id == item.id)
                            )
                            variants = variants_result.scalars().all()

                            for variant in variants:
                                v_name = (variant.name or "").lower()
                                v_name_ar = (variant.name_ar or "").lower()

                                # Check if variant matches target size
                                if target_normalized in size_map:
                                    for size_keyword in size_map[target_normalized]:
                                        if size_keyword in v_name or size_keyword in v_name_ar:
                                            return {
                                                "menu_item_id": item.id,
                                                "variant_id": variant.id,
                                                "name": f"{item.name_ar or item.name} ({variant.name_ar or variant.name})",
                                                "price": float(variant.price) if variant.price else 0.0,
                                                "quantity": 1,
                                                "restaurant_id": restaurant_id
                                            }

                        # No variants, check if size is in item name
                        if target_size in item_name:
                            return {
                                "menu_item_id": item.id,
                                "name": item.name_ar or item.name,
                                "price": float(item.price) if item.price else 0.0,
                                "quantity": 1,
                                "restaurant_id": restaurant_id
                            }
        except Exception as e:
            logger.error(f"Error finding item with size: {e}")
        return None

    async def _find_item_with_type(self, current_name: str, target_type: str, restaurant_id: int) -> Optional[dict]:
        """Find a menu item with different type (e.g., chicken → meat)"""
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

                # Type words to strip for base name comparison
                type_words = ["دجاج", "لحمة", "لحم", "خضار", "جبنة", "chicken", "meat", "beef", "vegetarian", "cheese"]
                base_name = current_name.lower()
                for tw in type_words:
                    base_name = base_name.replace(tw, "").strip()

                # Find matching item with target type
                for item in menu_items:
                    item_name = (item.name_ar or item.name or "").lower()
                    item_base = item_name
                    for tw in type_words:
                        item_base = item_base.replace(tw, "").strip()

                    # Check if same base name and has target type
                    if base_name in item_base or item_base in base_name:
                        if target_type in item_name:
                            return {
                                "menu_item_id": item.id,
                                "name": item.name_ar or item.name,
                                "price": float(item.price) if item.price else 0.0,
                                "quantity": 1,
                                "restaurant_id": restaurant_id
                            }
        except Exception as e:
            logger.error(f"Error finding item with type: {e}")
        return None

    async def _find_item_by_name(self, item_name: str, restaurant_id: int) -> Optional[dict]:
        """Find a menu item by name in a specific restaurant"""
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

                search_term = item_name.lower()

                # Find best match
                for item in menu_items:
                    item_name_ar = (item.name_ar or "").lower()
                    item_name_en = (item.name or "").lower()

                    # Check if search term is in item name
                    if search_term in item_name_ar or search_term in item_name_en:
                        return {
                            "menu_item_id": item.id,
                            "name": item.name_ar or item.name,
                            "price": float(item.price) if item.price else 0.0,
                            "quantity": 1,
                            "restaurant_id": restaurant_id
                        }

                # Try partial match
                for item in menu_items:
                    item_name_ar = (item.name_ar or "").lower()
                    item_name_en = (item.name or "").lower()

                    # Check for partial match
                    search_words = search_term.split()
                    for word in search_words:
                        if len(word) > 2 and (word in item_name_ar or word in item_name_en):
                            return {
                                "menu_item_id": item.id,
                                "name": item.name_ar or item.name,
                                "price": float(item.price) if item.price else 0.0,
                                "quantity": 1,
                                "restaurant_id": restaurant_id
                            }
        except Exception as e:
            logger.error(f"Error finding item by name: {e}")
        return None

    # ==================== One-Shot Order Feature ====================
    async def _handle_one_shot_order(self, phone_number: str, ai_result: dict, lang: str, user_data: dict):
        """Handle complete order in one sentence (items + restaurant + address)"""
        items = ai_result.get("items", [])
        restaurant_name = ai_result.get("restaurant_name")
        delivery_address = ai_result.get("delivery_address")
        ai_message = ai_result.get("message", "")

        # If no items matched, redirect to search
        if not items:
            if ai_result.get("matching_restaurants"):
                await self._handle_product_search(phone_number, ai_result, lang)
            else:
                error = "ما لقيت الصنف، اختار من القائمة! 🍽️"
                await whatsapp_service.send_text(phone_number, error)
                await self._show_restaurant_categories(phone_number, lang)
            return

        # Find restaurant
        restaurant = None
        restaurant_id = ai_result.get("restaurant_id")
        if restaurant_name and not restaurant_id:
            restaurant_id = await ai_service._find_restaurant_id(restaurant_name)

        if not restaurant_id:
            # Show restaurants that have this product
            product = items[0].get("name", "") if items else ""
            restaurants = await ai_service._find_restaurants_with_product(product)
            if restaurants:
                ai_result["matching_restaurants"] = restaurants
                ai_result["product_query"] = product
                await self._handle_product_search(phone_number, ai_result, lang)
            else:
                await whatsapp_service.send_text(phone_number, "ما لقيت المطعم 🤔 اختار من القائمة!")
                await self._show_restaurant_categories(phone_number, lang)
            return

        # Match items with menu
        ai_result = await ai_service._match_menu_items(ai_result, restaurant_id)
        matched_items = ai_result.get("items", [])

        if not matched_items:
            await whatsapp_service.send_text(phone_number, "ما لقيت هالأصناف بهالمطعم 🤔")
            await self._show_categories(phone_number, restaurant_id, lang)
            return

        # Clear cart and add items
        await redis_service.clear_cart(phone_number)
        items_text = []
        total = 0

        for item in matched_items:
            await redis_service.add_to_cart(phone_number, item)
            item_total = item["price"] * item["quantity"]
            total += item_total
            items_text.append(f"• {item['quantity']}x {item['name']}")

        # Get restaurant name
        async with AsyncSessionLocal() as db:
            rest_result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
            restaurant = rest_result.scalars().first()
            rest_name = restaurant.name if restaurant else "Unknown"

        # Build preview
        total_usd = float(total)  # Already USD
        items_list = "\n".join(items_text)

        # If address provided, show order preview
        if delivery_address:
            preview = get_text("order_preview", lang).format(
                items=items_list,
                restaurant=rest_name,
                address=delivery_address,
                total=total_usd
            )

            # Store address in session
            user_data["delivery_address"] = delivery_address
            user_data["restaurant_id"] = restaurant_id

            await whatsapp_service.send_interactive_buttons(
                phone_number,
                preview,
                [
                    {"id": "confirm_order", "title": get_text("confirm_order_btn", lang)},
                    {"id": "view_cart", "title": get_text("modify_order_btn", lang)},
                    {"id": "cancel_order", "title": get_text("cancel_order_btn", lang)}
                ]
            )
            await redis_service.set_user_state(phone_number, "CONFIRMING_INFO", user_data)
        else:
            # No address - show items added and ask for address
            response = ai_message or "تكرم عينك! ✅"
            response += f"\n\n🛒 *الأصناف المضافة:*\n{items_list}"
            response += f"\n\n💰 *المجموع:* ${total_usd:.2f}"

            await whatsapp_service.send_text(phone_number, response)
            await whatsapp_service.send_text(phone_number, get_text("share_location", lang))
            await redis_service.set_user_state(phone_number, "AWAITING_LOCATION", {
                "lang": lang,
                "restaurant_id": restaurant_id
            })

    # ==================== Numbered Menu Ordering ====================
    async def _handle_numbered_menu_input(self, phone_number: str, text: str, lang: str, user_data: dict):
        """Handle text input when user is browsing a numbered menu"""
        items_map = user_data.get("items_map", {})
        restaurant_id = user_data.get("restaurant_id")
        restaurant_name = user_data.get("restaurant_name", "")

        # Check for cart/order/done commands
        done_words = ["طلب", "order", "سلة", "cart", "checkout", "done", "bas", "بس", "خلص", "تم", "كفي", "خلصت", "finish", "ok", "اوك", "tam", "tamam", "تمام", "enough", "yalla", "يلا"]
        if text.lower().strip() in done_words:
            await self._show_cart(phone_number, lang)
            return

        # Check for restart commands
        if text.lower() in ["start", "restart", "بداية", "ابدأ", "0", "menu", "قائمة"]:
            await self._send_language_selection(phone_number)
            return

        # Check if input is purely numbers (1 3, 1,3, 1+3, 1 و 3)
        import re
        clean = re.sub(r'[\s,،وw+]+', '', text)
        if clean.isdigit():
            # Pure number input - use direct number matching
            numbers = re.findall(r'\d+', text)

            # Validate all numbers exist in items_map
            valid_selections = []
            invalid_nums = []
            for num in numbers:
                if num in items_map:
                    valid_selections.append(items_map[num])
                else:
                    invalid_nums.append(num)

            if invalid_nums and not valid_selections:
                max_num = max(int(k) for k in items_map.keys()) if items_map else 0
                await whatsapp_service.send_text(
                    phone_number,
                    f"أرقام غير صحيحة 🤔 اختار من 1 لـ {max_num}" if lang == "ar"
                    else f"Invalid numbers 🤔 Choose from 1 to {max_num}"
                )
                return

            if invalid_nums:
                await whatsapp_service.send_text(
                    phone_number,
                    f"⚠️ الأرقام {', '.join(invalid_nums)} غير موجودة، تم تجاهلها" if lang == "ar"
                    else f"⚠️ Numbers {', '.join(invalid_nums)} not found, skipped"
                )
        else:
            # Text input (with or without numbers) - use AI to match against menu
            ai_result = await self._match_menu_with_ai(text, items_map, restaurant_name, lang)

            if ai_result.get("action") == "order" and ai_result.get("items"):
                # AI matched items from the menu
                valid_selections = []
                for ai_item in ai_result["items"]:
                    num_str = str(ai_item.get("number", ""))
                    qty = ai_item.get("quantity", 1)
                    if num_str in items_map:
                        item_data = dict(items_map[num_str])
                        if qty > 1:
                            item_data["_ai_quantity"] = qty
                        valid_selections.append(item_data)

                if not valid_selections:
                    await whatsapp_service.send_text(
                        phone_number,
                        "ما لقيت هالصنف بالمنيو 🤔\nاكتب رقم الصنف أو اسمو" if lang == "ar"
                        else "Couldn't find that item 🤔\nType the item number or name"
                    )
                    return
            elif ai_result.get("action") == "leave":
                # User wants to leave menu - pass to general AI
                await self._process_ai_order(phone_number, text, lang, user_data)
                return
            else:
                await whatsapp_service.send_text(
                    phone_number,
                    "ما لقيت هالصنف بالمنيو 🤔\nاكتب رقم الصنف أو اسمو" if lang == "ar"
                    else "Couldn't find that item 🤔\nType the item number or name"
                )
                return

        # Check if AI provided quantities - add directly without asking
        ai_has_quantities = any(item.get("_ai_quantity") for item in valid_selections)
        if ai_has_quantities:
            # AI provided quantities - add all items directly
            for selected in valid_selections:
                qty = selected.pop("_ai_quantity", 1)
                cart_item = {
                    "menu_item_id": selected["menu_item_id"],
                    "name": selected["name"],
                    "price": selected["price"],
                    "quantity": qty,
                    "restaurant_id": restaurant_id
                }
                if selected.get("variant_id"):
                    cart_item["variant_id"] = selected["variant_id"]
                await redis_service.add_to_cart(phone_number, cart_item)

            cart_count = await redis_service.get_cart_count(phone_number)
            names = ", ".join(f"{s.get('_ai_quantity', 1) if '_ai_quantity' in s else qty}x {s['name']}" for s in valid_selections)
            if lang == "ar":
                msg = f"✅ تمت الإضافة\n🛒 السلة: {cart_count} أصناف\n\n"
                msg += "اكتب أرقام أصناف تانية، أو اكتب *تم* إذا بس بدك هيدول 👆"
            else:
                msg = f"✅ Added to cart\n🛒 Cart: {cart_count} items\n\n"
                msg += "Type more item numbers, or type *done* if that's all you want 👆"

            await whatsapp_service.send_text(phone_number, msg)
            await redis_service.set_user_state(phone_number, "BROWSING_NUMBERED_MENU", {
                "lang": lang,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "items_map": items_map
            })
            return

        # Start asking quantity for each selected item
        if len(valid_selections) == 1:
            # Single item - ask quantity directly
            selected = valid_selections[0]
            selected.pop("_ai_quantity", None)
            msg = f"✅ *{selected['name']}* - ${selected['price']:.2f}\n\n"
            msg += "كم واحد بدك؟ 🔢" if lang == "ar" else "How many? 🔢"
            await whatsapp_service.send_text(phone_number, msg)
            await redis_service.set_user_state(phone_number, "AWAITING_NUMBERED_QUANTITY", {
                "lang": lang,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "items_map": items_map,
                "selected_item": selected,
                "pending_items": [],
            })
        else:
            # Multiple items - ask quantity for the first, queue the rest
            first = valid_selections[0]
            first.pop("_ai_quantity", None)
            remaining = valid_selections[1:]
            for r in remaining:
                r.pop("_ai_quantity", None)
            msg = f"✅ *{first['name']}* - ${first['price']:.2f}\n\n"
            msg += "كم واحد بدك؟ 🔢" if lang == "ar" else "How many? 🔢"
            await whatsapp_service.send_text(phone_number, msg)
            await redis_service.set_user_state(phone_number, "AWAITING_NUMBERED_QUANTITY", {
                "lang": lang,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "items_map": items_map,
                "selected_item": first,
                "pending_items": remaining,
            })

    async def _handle_numbered_quantity(self, phone_number: str, quantity: int, lang: str, user_data: dict):
        """Handle quantity input after item selection from numbered menu"""
        selected_item = user_data.get("selected_item")
        restaurant_id = user_data.get("restaurant_id")
        restaurant_name = user_data.get("restaurant_name", "")
        items_map = user_data.get("items_map", {})
        pending_items = user_data.get("pending_items", [])

        if not selected_item:
            await whatsapp_service.send_text(phone_number, "حصل خطأ، جرب كمان مرة 🤔")
            await self._send_main_menu(phone_number, lang)
            return

        if quantity < 1 or quantity > 99:
            await whatsapp_service.send_text(
                phone_number,
                "اكتب عدد بين 1 و 99 ☝️" if lang == "ar" else "Enter a number between 1 and 99 ☝️"
            )
            return

        item_name = selected_item["name"]
        item_price = selected_item["price"]
        menu_item_id = selected_item["menu_item_id"]
        variant_id = selected_item.get("variant_id")

        # Build cart item
        cart_item = {
            "menu_item_id": menu_item_id,
            "name": item_name,
            "price": item_price,
            "quantity": quantity,
            "restaurant_id": restaurant_id
        }
        if variant_id:
            cart_item["variant_id"] = variant_id

        await redis_service.add_to_cart(phone_number, cart_item)

        # Get cart info
        cart_count = await redis_service.get_cart_count(phone_number)

        if pending_items:
            # More items to process - ask quantity for next one
            next_item = pending_items[0]
            rest_pending = pending_items[1:]

            if lang == "ar":
                msg = f"✅ {quantity}x {item_name}\n\n"
                msg += f"*{next_item['name']}* - ${next_item['price']:.2f}\n"
                msg += "كم واحد بدك؟ 🔢"
            else:
                msg = f"✅ {quantity}x {item_name}\n\n"
                msg += f"*{next_item['name']}* - ${next_item['price']:.2f}\n"
                msg += "How many? 🔢"

            await whatsapp_service.send_text(phone_number, msg)
            await redis_service.set_user_state(phone_number, "AWAITING_NUMBERED_QUANTITY", {
                "lang": lang,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "items_map": items_map,
                "selected_item": next_item,
                "pending_items": rest_pending,
            })
        else:
            # All items added - show confirmation and go back to menu state
            if lang == "ar":
                msg = f"✅ {quantity}x {item_name}\n"
                msg += f"🛒 السلة: {cart_count} أصناف\n\n"
                msg += "اكتب أرقام أصناف تانية، أو اكتب *تم* إذا بس بدك هيدول 👆"
            else:
                msg = f"✅ {quantity}x {item_name}\n"
                msg += f"🛒 Cart: {cart_count} items\n\n"
                msg += "Type more item numbers, or type *done* if that's all you want 👆"

            await whatsapp_service.send_text(phone_number, msg)

            # Smart upsell suggestion
            try:
                cart_items = await redis_service.get_cart(phone_number)
                upsell = await self._get_menu_upsell(item_name, items_map, restaurant_name, cart_items)
                if upsell:
                    await whatsapp_service.send_text(phone_number, upsell)
            except Exception as e:
                logger.error(f"Upsell error: {e}")

            await redis_service.set_user_state(phone_number, "BROWSING_NUMBERED_MENU", {
                "lang": lang,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "items_map": items_map
            })

    async def _match_menu_with_ai(self, text: str, items_map: dict, restaurant_name: str, lang: str) -> dict:
        """Match user text to items in the current numbered menu using AI"""
        try:
            import google.generativeai as genai

            # Build items list from items_map
            items_list = ""
            for num, item in sorted(items_map.items(), key=lambda x: int(x[0])):
                items_list += f"{num}. {item['name']} - ${item['price']:.2f}\n"

            prompt = f"""أنت مساعد توصيل طعام. المستخدم عم يتصفح منيو "{restaurant_name}" وبدو يطلب.

الأصناف المتاحة بالمنيو:
{items_list}

كلام المستخدم: "{text}"

مهمتك: طابق كلام المستخدم مع أصناف من القائمة فوق بس (لا تخترع أصناف).

قواعد:
- افهم عربي، إنكليزي، وعربيزي (arabizi): bde=بدي، pepsi=بيبسي، burger=برغر، chicken=دجاج، fries=بطاطا، 7=ح، 3=ع، 5=خ، 8=غ، 2=أ
- "l awwal" أو "الأول" = الصنف رقم 1
- إذا ذكر كمية (مثلاً "2 بيبسي" أو "tnen shawarma") حطها بالـ quantity
- إذا ما ذكر كمية، الافتراضي quantity = 1
- إذا المستخدم بدو يطلع من المنيو أو يروح لمطعم تاني أو يعمل شي ما إلو علاقة بالمنيو → action = "leave"

رد JSON فقط:
{{"items": [{{"number": 1, "quantity": 1}}], "action": "order"}}

إذا بدو يطلع من المنيو:
{{"items": [], "action": "leave"}}

إذا ما فهمت أو ما لقيت تطابق بالمنيو:
{{"items": [], "action": "unknown"}}
"""

            response = ai_service.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )

            import json
            result = json.loads(response.text)
            return result

        except Exception as e:
            logger.error(f"Menu AI matching error: {e}")
            return {"items": [], "action": "error"}

    async def _get_menu_upsell(self, item_name: str, items_map: dict, restaurant_name: str, cart_items: list) -> str:
        """Get AI upsell suggestion based on what was just added"""
        try:
            import google.generativeai as genai

            # Build items list
            items_list = ""
            for num, item in sorted(items_map.items(), key=lambda x: int(x[0])):
                items_list += f"{num}. {item['name']} - ${item['price']:.2f}\n"

            # Build cart context
            cart_text = ""
            for ci in cart_items:
                cart_text += f"- {ci.get('name', '')} x{ci.get('quantity', 1)}\n"

            prompt = f"""أنت بائع ودود بمطعم "{restaurant_name}". المستخدم لسا ضاف "{item_name}" عالسلة.

السلة الحالية:
{cart_text}

الأصناف المتاحة بالمنيو:
{items_list}

اقترح صنف واحد مكمّل من المنيو (مثلاً: مشروب مع أكل، بطاطا مع برغر، حلو بعد الأكل).
لا تقترح شي موجود بالسلة.
الجواب لازم يكون جملة قصيرة بالعامية اللبنانية مع رقم الصنف.

رد JSON فقط:
{{"suggestion": "شو رأيك تضيف بيبسي معون؟ (رقم 45) 🥤", "item_number": 45}}

إذا ما في اقتراح مناسب:
{{"suggestion": "", "item_number": 0}}
"""

            response = ai_service.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )

            import json
            result = json.loads(response.text)
            return result.get("suggestion", "")

        except Exception as e:
            logger.error(f"Upsell AI error: {e}")
            return ""

    # ==================== Menu Request Feature ====================
    async def _handle_menu_request(self, phone_number: str, ai_result: dict, lang: str):
        """Handle request to see a restaurant's full menu"""
        restaurant_name = ai_result.get("restaurant_name", "")
        ai_message = ai_result.get("message", "")

        if not restaurant_name:
            await whatsapp_service.send_text(
                phone_number,
                "أي مطعم بدك تشوف المانيو تبعه؟ 🤔" if lang == "ar" else "Which restaurant's menu would you like to see?"
            )
            await self._show_restaurants(phone_number, lang)
            return

        # Find restaurant by name
        restaurant_id = await ai_service._find_restaurant_id(restaurant_name)

        if not restaurant_id:
            # Try fuzzy match
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Restaurant)
                    .where(Restaurant.is_active == True)
                )
                restaurants = result.scalars().all()

                # Find best match
                search_lower = restaurant_name.lower()
                for rest in restaurants:
                    name_en = (rest.name or "").lower()
                    name_ar = (rest.name_ar or "").lower()
                    if search_lower in name_en or search_lower in name_ar or name_en in search_lower or name_ar in search_lower:
                        restaurant_id = rest.id
                        break

        if not restaurant_id:
            await whatsapp_service.send_text(
                phone_number,
                f"ما لقيت مطعم باسم '{restaurant_name}' 🤔\nاختار من القائمة:" if lang == "ar"
                else f"Couldn't find restaurant '{restaurant_name}'\nChoose from the list:"
            )
            await self._show_restaurants(phone_number, lang)
            return

        # Get full menu
        async with AsyncSessionLocal() as db:
            # Get restaurant
            rest_result = await db.execute(
                select(Restaurant).where(Restaurant.id == restaurant_id)
            )
            restaurant = rest_result.scalars().first()

            if not restaurant:
                await whatsapp_service.send_text(phone_number, "المطعم غير موجود 🤔")
                await self._show_restaurants(phone_number, lang)
                return

            rest_name = restaurant.name_ar if lang == "ar" and restaurant.name_ar else restaurant.name

            # Get all categories with items
            categories_result = await db.execute(
                select(Category)
                .options(selectinload(Category.items))
                .join(Menu)
                .where(Menu.restaurant_id == restaurant_id)
                .where(Menu.is_active == True)
            )
            categories = categories_result.scalars().all()

            if not categories:
                await whatsapp_service.send_text(
                    phone_number,
                    f"لا يوجد قائمة طعام لـ {rest_name} حالياً 😕" if lang == "ar"
                    else f"No menu available for {rest_name} currently 😕"
                )
                return

            # Build numbered menu text and items map
            from app.models.menu import MenuItemVariant
            menu_text = f"📋 *مانيو {rest_name}*\n"
            menu_text += "=" * 25 + "\n\n"
            items_map = {}  # number -> item info for ordering
            item_num = 0

            for category in categories:
                cat_name = category.name_ar if lang == "ar" and category.name_ar else category.name
                available_items = [item for item in category.items if item.is_available]

                if not available_items:
                    continue

                menu_text += f"🔸 *{cat_name}*\n"

                for item in available_items:
                    item_name = item.name_ar if lang == "ar" and item.name_ar else item.name

                    if hasattr(item, 'has_variants') and item.has_variants:
                        variants_result = await db.execute(
                            select(MenuItemVariant)
                            .where(MenuItemVariant.menu_item_id == item.id)
                            .order_by(MenuItemVariant.order)
                        )
                        variants = variants_result.scalars().all()
                        if variants:
                            for v in variants:
                                item_num += 1
                                v_name = v.name_ar if lang == 'ar' and v.name_ar else v.name
                                price = float(v.price)
                                display_name = f"{item_name} ({v_name})"
                                menu_text += f"  {item_num}. {display_name} - ${price:.2f}\n"
                                items_map[str(item_num)] = {
                                    "menu_item_id": item.id,
                                    "variant_id": v.id,
                                    "name": display_name,
                                    "price": price,
                                    "restaurant_id": restaurant_id
                                }
                        else:
                            item_num += 1
                            price = float(item.price) if item.price else 0.0
                            menu_text += f"  {item_num}. {item_name} - ${price:.2f}\n"
                            items_map[str(item_num)] = {
                                "menu_item_id": item.id,
                                "variant_id": None,
                                "name": item_name,
                                "price": price,
                                "restaurant_id": restaurant_id
                            }
                    else:
                        item_num += 1
                        price = float(item.price) if item.price else 0.0
                        price_str = f"${price:.2f}" if price > 0 else "-"
                        menu_text += f"  {item_num}. {item_name} - {price_str}\n"
                        items_map[str(item_num)] = {
                            "menu_item_id": item.id,
                            "variant_id": None,
                            "name": item_name,
                            "price": price,
                            "restaurant_id": restaurant_id
                        }

                menu_text += "\n"

            # Add instruction footer
            if lang == "ar":
                menu_text += "اكتب أرقام الأصناف يلي بدك ياها (مثلاً: 1 3) 👆\n"
                menu_text += "أو اكتب *طلب* لعرض السلة 🛒"
            else:
                menu_text += "Type item numbers you want (e.g.: 1 3) 👆\n"
                menu_text += "Or type *order* to view cart 🛒"

            # Send menu - split into 2 messages if > 4096 chars (WhatsApp limit)
            if len(menu_text) > 4096:
                # Split at a newline near the middle
                mid = len(menu_text) // 2
                split_pos = menu_text.rfind('\n', 0, mid + 500)
                if split_pos == -1:
                    split_pos = mid
                part1 = menu_text[:split_pos]
                part2 = menu_text[split_pos:].lstrip('\n')
                await whatsapp_service.send_text(phone_number, part1)
                await whatsapp_service.send_text(phone_number, part2)
            else:
                await whatsapp_service.send_text(phone_number, menu_text)

            # Store items map in Redis and set state for numbered ordering
            await redis_service.set_user_state(phone_number, "BROWSING_NUMBERED_MENU", {
                "lang": lang,
                "restaurant_id": restaurant_id,
                "restaurant_name": rest_name,
                "items_map": items_map
            })

    # ==================== Description Search Feature ====================
    async def _handle_description_search(self, phone_number: str, ai_result: dict, lang: str):
        """Handle search by description (cold, hot, sweet, spicy, etc.)"""
        description = ai_result.get("description_query", "")
        ai_message = ai_result.get("message", "")

        if not description:
            await whatsapp_service.send_text(phone_number, ai_message or "شو نوع الأكل اللي بدك ياه؟ 🤔")
            return

        # Search keywords mapping
        description_keywords = {
            # Cold/Refreshing
            "بارد": ["عصير", "سموذي", "آيس", "ice", "cold", "ليموناضة", "موهيتو", "كوكتيل"],
            "منعش": ["عصير", "ليموناضة", "موهيتو", "فريش", "fresh"],
            "cold": ["juice", "smoothie", "ice", "lemonade", "mojito"],
            # Hot/Spicy
            "حار": ["حارة", "سبايسي", "spicy", "hot", "بافلو", "buffalo"],
            "حريف": ["حارة", "سبايسي", "spicy", "فاهيتا", "جالبينو"],
            "spicy": ["spicy", "hot", "buffalo", "jalapeño"],
            # Sweet
            "حلو": ["كيك", "حلويات", "شوكولا", "آيس كريم", "وافل", "كريب", "نوتيلا"],
            "sweet": ["cake", "dessert", "chocolate", "ice cream", "waffle"],
            # Healthy
            "صحي": ["سلطة", "salad", "grilled", "مشوي", "خضار"],
            "healthy": ["salad", "grilled", "vegetables", "light"],
            # Fast
            "سريع": ["برغر", "ساندويش", "شاورما", "فرايز", "هوت دوغ"],
            "fast": ["burger", "sandwich", "fries", "hot dog"],
            # Breakfast
            "فطور": ["منقوشة", "فول", "حمص", "لبنة", "بيض", "كرواسان"],
            "breakfast": ["manakish", "foul", "hummus", "eggs", "croissant"],
        }

        # Find matching keywords
        search_terms = []
        desc_lower = description.lower()
        for key, terms in description_keywords.items():
            if key in desc_lower:
                search_terms.extend(terms)

        if not search_terms:
            search_terms = description.split()

        # Search in database
        matching_items = []
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(MenuItem, Restaurant)
                    .join(Category, MenuItem.category_id == Category.id)
                    .join(Menu, Category.menu_id == Menu.id)
                    .join(Restaurant, Menu.restaurant_id == Restaurant.id)
                    .where(MenuItem.is_available == True)
                    .where(Restaurant.is_active == True)
                    .limit(200)
                )
                rows = result.all()

                for item, rest in rows:
                    item_name = (item.name_ar or item.name or "").lower()
                    item_desc = (item.description_ar or item.description or "").lower()

                    for term in search_terms:
                        if term.lower() in item_name or term.lower() in item_desc:
                            matching_items.append({
                                "id": item.id,
                                "name": item.name_ar or item.name,
                                "restaurant": rest.name_ar or rest.name,
                                "restaurant_id": rest.id,
                                "price": float(item.price) if item.price else 0
                            })
                            break

                # Remove duplicates and limit
                seen = set()
                unique_items = []
                for item in matching_items:
                    key = f"{item['name']}_{item['restaurant_id']}"
                    if key not in seen:
                        seen.add(key)
                        unique_items.append(item)
                matching_items = unique_items[:10]

        except Exception as e:
            logger.error(f"Error searching by description: {e}")

        if matching_items:
            # Build response with suggestions
            response = ai_message + "\n\n" if ai_message else f"🔍 لقيت {len(matching_items)} خيارات:\n\n"

            # Group by restaurant
            by_restaurant = {}
            for item in matching_items:
                rest = item["restaurant"]
                if rest not in by_restaurant:
                    by_restaurant[rest] = []
                by_restaurant[rest].append(item)

            # Build interactive list (max 9 rows total for WhatsApp limit)
            sections = []
            total_rows = 0
            MAX_ROWS = 9
            for rest_name, items in list(by_restaurant.items()):
                if total_rows >= MAX_ROWS:
                    break
                rows = []
                for item in items:
                    if total_rows >= MAX_ROWS:
                        break
                    price_str = f"${item['price']:.2f}" if item['price'] else ""
                    rows.append({
                        "id": f"item_{item['id']}",
                        "title": item["name"][:24],
                        "description": f"💰 {price_str}" if price_str else ""
                    })
                    total_rows += 1
                if rows:
                    sections.append({
                        "title": rest_name[:24],
                        "rows": rows
                    })

            if sections:
                await whatsapp_service.send_interactive_list(
                    phone_number,
                    response.strip(),
                    "اختار 👆" if lang == "ar" else "Select",
                    sections
                )
            else:
                await whatsapp_service.send_text(phone_number, response)
        else:
            await whatsapp_service.send_text(
                phone_number,
                f"ما لقيت شي بهالوصف 🤔\nجرب تقلي شو بدك بالضبط!"
            )
            await self._show_restaurant_categories(phone_number, lang)

    # ==================== Reorder Feature ====================
    async def _show_previous_orders(self, phone_number: str, lang: str):
        """Show user's previous orders for quick reorder"""
        async with AsyncSessionLocal() as db:
            # Find user
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()

            if not user:
                await whatsapp_service.send_text(phone_number, get_text("no_previous_orders", lang))
                await self._send_main_menu(phone_number, lang)
                return

            # Get last 5 orders
            orders_result = await db.execute(
                select(Order)
                .options(selectinload(Order.restaurant), selectinload(Order.items))
                .where(Order.user_id == user.id)
                .order_by(Order.created_at.desc())
                .limit(5)
            )
            orders = orders_result.scalars().all()

            if not orders:
                await whatsapp_service.send_text(phone_number, get_text("no_previous_orders", lang))
                await self._send_main_menu(phone_number, lang)
                return

            # Build list
            sections = [{
                "title": get_text("select_order_to_reorder", lang),
                "rows": []
            }]

            for order in orders:
                restaurant_name = order.restaurant.name if order.restaurant else "Unknown"
                items_count = len(order.items) if order.items else 0
                total_usd = float(order.total_amount or 0)  # Already USD
                date_str = order.created_at.strftime("%d/%m") if order.created_at else ""

                sections[0]["rows"].append({
                    "id": f"reorder_{order.id}",
                    "title": f"{restaurant_name[:20]} - ${total_usd:.1f}",
                    "description": f"{items_count} أصناف - {date_str}" if lang == "ar" else f"{items_count} items - {date_str}"
                })

            await whatsapp_service.send_interactive_list(
                phone_number,
                "📋 " + get_text("select_order_to_reorder", lang),
                get_text("view_orders", lang),
                sections
            )
            await redis_service.set_user_state(phone_number, "BROWSING_ORDERS", {"lang": lang})

    async def _process_reorder(self, phone_number: str, order_id: int, lang: str):
        """Add items from previous order to cart"""
        async with AsyncSessionLocal() as db:
            # Get order with items
            result = await db.execute(
                select(Order)
                .options(selectinload(Order.items).selectinload(OrderItem.menu_item), selectinload(Order.restaurant))
                .where(Order.id == order_id)
            )
            order = result.scalars().first()

            if not order or not order.items:
                await whatsapp_service.send_text(phone_number, "⚠️ لم نجد هذا الطلب")
                await self._send_main_menu(phone_number, lang)
                return

            # Clear cart and add items
            await redis_service.clear_cart(phone_number)

            items_text = []
            total = 0

            for order_item in order.items:
                item_data = {
                    "menu_item_id": order_item.menu_item_id,
                    "name": order_item.menu_item.name if order_item.menu_item else "Item",
                    "price": order_item.unit_price,
                    "quantity": order_item.quantity,
                    "restaurant_id": order.restaurant_id
                }
                await redis_service.add_to_cart(phone_number, item_data)
                item_total = order_item.unit_price * order_item.quantity
                total += item_total
                items_text.append(f"• {order_item.quantity}x {item_data['name']}")

            # Show confirmation
            total_usd = float(total)  # Already USD
            msg = get_text("reorder_added", lang).format(
                items="\n".join(items_text),
                total=total_usd
            )
            await whatsapp_service.send_text(phone_number, msg)

            # Show checkout options
            buttons = [
                {"id": "checkout", "title": get_text("checkout", lang)},
                {"id": "view_cart", "title": get_text("view_cart", lang)},
                {"id": "add_more", "title": get_text("continue_shopping", lang)}
            ]
            await whatsapp_service.send_interactive_buttons(
                phone_number,
                "شو بدك تعمل؟" if lang == "ar" else "What next?",
                buttons
            )
            await redis_service.set_user_state(phone_number, "MAIN_MENU", {"lang": lang, "restaurant_id": order.restaurant_id})

    # ==================== Loyalty Feature ====================
    async def _show_loyalty_status(self, phone_number: str, lang: str):
        """Show user's loyalty points and tier"""
        from app.models.loyalty import CustomerLoyalty, LoyaltyTier

        async with AsyncSessionLocal() as db:
            # Find user
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()

            if not user:
                # Create user and loyalty
                user = User(phone_number=phone_number, full_name="WhatsApp Customer")
                db.add(user)
                await db.commit()
                await db.refresh(user)

            # Get or create loyalty
            loyalty_result = await db.execute(
                select(CustomerLoyalty).where(CustomerLoyalty.user_id == user.id)
            )
            loyalty = loyalty_result.scalars().first()

            if not loyalty:
                # Create loyalty record
                import secrets
                import string
                referral_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                loyalty = CustomerLoyalty(
                    user_id=user.id,
                    referral_code=f"LION{referral_code}"
                )
                db.add(loyalty)
                await db.commit()
                await db.refresh(loyalty)

            # Tier icons and names
            tier_info = {
                LoyaltyTier.BRONZE: ("🥉", "Bronze", "برونز", 1000),
                LoyaltyTier.SILVER: ("🥈", "Silver", "فضي", 5000),
                LoyaltyTier.GOLD: ("🥇", "Gold", "ذهبي", 15000),
                LoyaltyTier.PLATINUM: ("💎", "Platinum", "بلاتيني", None)
            }

            current_tier = loyalty.tier or LoyaltyTier.BRONZE
            tier_icon, tier_en, tier_ar, next_threshold = tier_info.get(current_tier, ("🥉", "Bronze", "برونز", 1000))
            tier_name = tier_ar if lang == "ar" else tier_en

            # Build message
            msg = get_text("loyalty_status", lang).format(
                tier_icon=tier_icon,
                tier=tier_name,
                points=loyalty.available_points or 0,
                orders=loyalty.total_orders or 0,
                spent=float(loyalty.total_spent or 0)
            )

            # Add progress to next tier
            if next_threshold:
                points_needed = next_threshold - (loyalty.lifetime_points or 0)
                if points_needed > 0:
                    # Find next tier name
                    next_tier_map = {
                        LoyaltyTier.BRONZE: ("Silver", "فضي"),
                        LoyaltyTier.SILVER: ("Gold", "ذهبي"),
                        LoyaltyTier.GOLD: ("Platinum", "بلاتيني"),
                    }
                    next_tier = next_tier_map.get(current_tier, ("Silver", "فضي"))
                    next_tier_name = next_tier[1] if lang == "ar" else next_tier[0]
                    msg += get_text("loyalty_progress", lang).format(
                        points_needed=points_needed,
                        next_tier=next_tier_name
                    )

            await whatsapp_service.send_text(phone_number, msg)

            # Show main menu button
            await whatsapp_service.send_interactive_buttons(
                phone_number,
                "🎁 اطلب أكتر واربح نقاط!" if lang == "ar" else "🎁 Order more, earn more!",
                [
                    {"id": "menu_browse", "title": get_text("btn_menu", lang)},
                    {"id": "back_main", "title": get_text("back_to_menu", lang)}
                ]
            )
            await redis_service.set_user_state(phone_number, "MAIN_MENU", {"lang": lang})

    async def _award_loyalty_points(self, phone_number: str, order: Order, lang: str):
        """Award loyalty points after order completion"""
        from app.models.loyalty import CustomerLoyalty, LoyaltyTier, PointTransaction, PointTransactionType
        from datetime import timedelta

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()
            if not user:
                return

            loyalty_result = await db.execute(
                select(CustomerLoyalty).where(CustomerLoyalty.user_id == user.id)
            )
            loyalty = loyalty_result.scalars().first()

            if not loyalty:
                return

            # Calculate points (10 points per $1)
            order_usd = float(order.total_amount or 0)  # Already USD
            base_points = int(order_usd * 10)

            # Tier multipliers
            multipliers = {
                LoyaltyTier.BRONZE: 1.0,
                LoyaltyTier.SILVER: 1.25,
                LoyaltyTier.GOLD: 1.5,
                LoyaltyTier.PLATINUM: 2.0
            }
            multiplier = multipliers.get(loyalty.tier or LoyaltyTier.BRONZE, 1.0)
            final_points = int(base_points * multiplier)

            if final_points > 0:
                # Create transaction
                from datetime import datetime
                transaction = PointTransaction(
                    loyalty_id=loyalty.id,
                    type=PointTransactionType.EARNED,
                    points=final_points,
                    balance_after=(loyalty.available_points or 0) + final_points,
                    order_id=order.id,
                    description=f"Order #{order.id}",
                    expires_at=datetime.utcnow() + timedelta(days=365)
                )
                db.add(transaction)

                # Update loyalty
                loyalty.available_points = (loyalty.available_points or 0) + final_points
                loyalty.total_points = (loyalty.total_points or 0) + final_points
                loyalty.lifetime_points = (loyalty.lifetime_points or 0) + final_points
                loyalty.total_orders = (loyalty.total_orders or 0) + 1
                loyalty.total_spent = (loyalty.total_spent or 0) + order_usd

                # Check tier upgrade
                tier_thresholds = [
                    (15000, LoyaltyTier.PLATINUM),
                    (5000, LoyaltyTier.GOLD),
                    (1000, LoyaltyTier.SILVER),
                    (0, LoyaltyTier.BRONZE)
                ]
                for threshold, tier in tier_thresholds:
                    if loyalty.lifetime_points >= threshold:
                        if loyalty.tier != tier:
                            loyalty.tier = tier
                            # Could send tier upgrade notification here
                        break

                await db.commit()

                # Send points notification
                msg = get_text("points_earned", lang).format(
                    points=final_points,
                    total=loyalty.available_points
                )
                await whatsapp_service.send_text(phone_number, msg)

    # ==================== Favorites Feature ====================
    async def _show_favorites(self, phone_number: str, lang: str):
        """Show user's favorite restaurants and most ordered items"""
        from app.api.v1.endpoints.favorites import Favorite
        from sqlalchemy import func

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()

            if not user:
                await whatsapp_service.send_text(phone_number, get_text("no_favorites", lang))
                await self._send_main_menu(phone_number, lang)
                return

            # Get favorite restaurants
            fav_result = await db.execute(
                select(Favorite, Restaurant)
                .join(Restaurant, Favorite.restaurant_id == Restaurant.id)
                .where(Favorite.user_id == user.id)
                .order_by(Favorite.created_at.desc())
                .limit(5)
            )
            favorites = fav_result.all()

            # Get most ordered items (smart favorites)
            from app.models.order import OrderItem
            top_items_result = await db.execute(
                select(
                    MenuItem,
                    Restaurant,
                    func.sum(OrderItem.quantity).label('total_qty')
                )
                .select_from(OrderItem)
                .join(Order, OrderItem.order_id == Order.id)
                .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
                .join(Category, MenuItem.category_id == Category.id)
                .join(Menu, Category.menu_id == Menu.id)
                .join(Restaurant, Menu.restaurant_id == Restaurant.id)
                .where(Order.user_id == user.id)
                .group_by(MenuItem.id, Restaurant.id)
                .order_by(func.sum(OrderItem.quantity).desc())
                .limit(5)
            )
            top_items = top_items_result.all()

            sections = []

            # Add top items section first (most valuable for quick reorder)
            if top_items:
                item_rows = []
                for item, rest, qty in top_items:
                    item_name = (item.name_ar if lang == "ar" and item.name_ar else item.name)[:20]
                    rest_name = (rest.name_ar if lang == "ar" and rest.name_ar else rest.name)[:15]
                    item_rows.append({
                        "id": f"quickorder_{item.id}_{rest.id}",
                        "title": f"⭐ {item_name}",
                        "description": f"من {rest_name} | طلبت {qty}x"
                    })
                sections.append({
                    "title": "🔥 أصنافك المفضلة" if lang == "ar" else "🔥 Your Favorites",
                    "rows": item_rows
                })

            # Add favorite restaurants section
            if favorites:
                rest_rows = []
                for fav, rest in favorites:
                    rest_name = (rest.name_ar if lang == "ar" and rest.name_ar else rest.name)[:24]
                    rest_rows.append({
                        "id": f"rest_{rest.id}",
                        "title": f"🏪 {rest_name}",
                        "description": "عرض المانيو" if lang == "ar" else "View menu"
                    })
                sections.append({
                    "title": "❤️ مطاعمك" if lang == "ar" else "❤️ Your Restaurants",
                    "rows": rest_rows
                })

            if not sections:
                await whatsapp_service.send_text(phone_number, get_text("no_favorites", lang))
                await self._send_main_menu(phone_number, lang)
                return

            await whatsapp_service.send_interactive_list(
                phone_number,
                "⭐ *المفضلة*\nاختار للطلب السريع!" if lang == "ar" else "⭐ *Favorites*\nQuick order!",
                "اختار 👆" if lang == "ar" else "Select",
                sections
            )
            await redis_service.set_user_state(phone_number, "BROWSING_FAVORITES", {"lang": lang})

    async def _check_and_suggest_favorite(self, phone_number: str, restaurant_id: int, lang: str):
        """Check if restaurant should be suggested as favorite"""
        from app.api.v1.endpoints.favorites import Favorite

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()
            if not user:
                return

            # Check if already favorite
            fav_result = await db.execute(
                select(Favorite).where(
                    Favorite.user_id == user.id,
                    Favorite.restaurant_id == restaurant_id
                )
            )
            if fav_result.scalars().first():
                return  # Already favorite

            # Count orders from this restaurant
            from sqlalchemy import func
            order_count_result = await db.execute(
                select(func.count(Order.id)).where(
                    Order.user_id == user.id,
                    Order.restaurant_id == restaurant_id
                )
            )
            order_count = order_count_result.scalar() or 0

            # Suggest if ordered 3+ times
            if order_count >= 3:
                rest_result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
                restaurant = rest_result.scalars().first()
                if restaurant:
                    msg = get_text("suggest_favorite", lang).format(
                        restaurant=restaurant.name,
                        count=order_count
                    )
                    await whatsapp_service.send_interactive_buttons(
                        phone_number,
                        msg,
                        [
                            {"id": f"add_fav_{restaurant_id}", "title": "❤️ أضف" if lang == "ar" else "❤️ Add"},
                            {"id": "skip_fav", "title": "لا شكراً" if lang == "ar" else "No thanks"}
                        ]
                    )

    async def _add_to_favorites(self, phone_number: str, restaurant_id: int, lang: str):
        """Add restaurant to favorites"""
        from app.api.v1.endpoints.favorites import Favorite

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()
            if not user:
                return

            # Check if already favorite
            existing = await db.execute(
                select(Favorite).where(
                    Favorite.user_id == user.id,
                    Favorite.restaurant_id == restaurant_id
                )
            )
            if existing.scalars().first():
                return

            # Add favorite
            favorite = Favorite(user_id=user.id, restaurant_id=restaurant_id)
            db.add(favorite)
            await db.commit()

            await whatsapp_service.send_text(phone_number, get_text("added_to_favorites", lang))

    # ==================== Reviews Feature ====================
    async def _request_review(self, phone_number: str, order_id: int, restaurant_name: str, lang: str):
        """Request a review from customer (called after delivery)"""
        msg = get_text("rate_order", lang).format(restaurant=restaurant_name)
        await whatsapp_service.send_text(phone_number, msg)

        # Store pending review
        await redis_service.set_pending_review(phone_number, order_id, restaurant_name)
        await redis_service.set_user_state(phone_number, "AWAITING_REVIEW", {"lang": lang, "order_id": order_id})

    async def _process_review(self, phone_number: str, rating_text: str, lang: str, user_data: dict):
        """Process a review rating"""
        from app.api.v1.endpoints.reviews import Review

        try:
            rating = int(rating_text.strip())
            if rating < 1 or rating > 5:
                raise ValueError("Invalid rating")
        except ValueError:
            # Not a valid rating, ignore
            return False

        pending = await redis_service.get_pending_review(phone_number)
        if not pending:
            return False

        order_id = pending.get("order_id")

        async with AsyncSessionLocal() as db:
            # Get user
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalars().first()
            if not user:
                return False

            # Get order
            order_result = await db.execute(select(Order).where(Order.id == order_id))
            order = order_result.scalars().first()
            if not order:
                return False

            # Create review
            review = Review(
                order_id=order_id,
                restaurant_id=order.restaurant_id,
                customer_id=user.id,
                rating=float(rating)
            )
            db.add(review)
            await db.commit()

        # Clear pending review
        await redis_service.clear_pending_review(phone_number)

        if rating >= 4:
            await whatsapp_service.send_text(phone_number, get_text("thanks_for_review", lang))
        else:
            await whatsapp_service.send_text(phone_number, get_text("sorry_bad_experience", lang))

        await self._send_main_menu(phone_number, lang)
        return True

    # ==================== Quick Add from Suggestions ====================
    async def _quick_add_suggestion(self, phone_number: str, suggestion: dict, lang: str):
        """Quick add item from AI suggestions"""
        async with AsyncSessionLocal() as db:
            # Get menu item
            result = await db.execute(
                select(MenuItem)
                .options(selectinload(MenuItem.category))
                .where(MenuItem.id == suggestion.get("id"))
            )
            item = result.scalars().first()

            if not item:
                await whatsapp_service.send_text(phone_number, "⚠️ الصنف غير متوفر")
                await self._send_main_menu(phone_number, lang)
                return

            # Get restaurant_id
            menu_result = await db.execute(
                select(Menu).where(Menu.id == item.category.menu_id)
            )
            menu = menu_result.scalars().first()

            cart_item = {
                "menu_item_id": item.id,
                "name": item.name_ar or item.name,
                "price": item.price,
                "quantity": 1,
                "restaurant_id": menu.restaurant_id if menu else None
            }

            await redis_service.add_to_cart(phone_number, cart_item)

            # Clear suggestions from context
            await redis_service.update_conversation_context(phone_number, {"suggestions": []})

            # Confirmation
            cart_count = await redis_service.get_cart_count(phone_number)
            confirm_msg = get_text("item_added", lang).format(
                quantity=1,
                name=cart_item["name"],
                cart_count=cart_count
            )

            await whatsapp_service.send_interactive_buttons(
                phone_number,
                f"✅ {confirm_msg}",
                [
                    {"id": "continue_shopping", "title": get_text("continue_shopping", lang)},
                    {"id": "view_cart", "title": get_text("view_cart", lang)},
                    {"id": "checkout", "title": get_text("checkout", lang)}
                ]
            )

    # ==================== Conversation Memory Integration ====================
    async def _save_to_conversation(self, phone_number: str, role: str, content: str, context: dict = None):
        """Save message to conversation history"""
        await redis_service.save_conversation_message(phone_number, role, content, context)

    async def _get_conversation_context(self, phone_number: str) -> str:
        """Get formatted conversation history for AI"""
        conv = await redis_service.get_conversation(phone_number)
        if not conv or not conv.get("messages"):
            return ""

        messages = conv["messages"][-5:]  # Last 5 messages
        formatted = []
        for msg in messages:
            role = "المستخدم" if msg["role"] == "user" else "البوت"
            formatted.append(f"{role}: {msg['content']}")

        return "\n".join(formatted)


bot_controller = BotController()

