from app.services.whatsapp_service import whatsapp_service
from app.services.redis_service import redis_service
from app.services.ai_service import ai_service
from app.core.i18n import get_text
from app.db.session import AsyncSessionLocal
from app.models.restaurant import Restaurant
from app.models.menu import Menu, MenuItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.user import User
from sqlalchemy import select
import logging
import json

logger = logging.getLogger(__name__)

class BotController:
    async def handle_message(self, phone_number: str, message_body: dict):
        print(f"DEBUG: Handling message from {phone_number}", flush=True)
        # Get user state
        try:
            state_data = await redis_service.get_user_state(phone_number)
            print(f"DEBUG: User state data: {state_data}", flush=True)
        except Exception as e:
            print(f"ERROR: Failed to get user state: {e}", flush=True)
            state_data = None

        state = state_data["state"] if state_data else "INIT"
        lang = state_data.get("data", {}).get("lang", "ar") if state_data else "ar"
        print(f"DEBUG: Current State: {state}, Lang: {lang}", flush=True)

        message_type = message_body.get("type")
        print(f"DEBUG: Message Type: {message_type}", flush=True)
        
        # Handle Text Messages
        if message_type == "text":
            text = message_body["text"]["body"]
            print(f"DEBUG: Text Body: {text}", flush=True)
            
            if state == "INIT":
                print("DEBUG: State is INIT, sending language buttons...", flush=True)
                # Start Flow: Ask for Language
                await whatsapp_service.send_interactive_buttons(
                    phone_number,
                    "Please select your language / الرجاء اختيار اللغة",
                    [
                        {"id": "lang_ar", "title": "العربية 🇸🇦"},
                        {"id": "lang_en", "title": "English 🇺🇸"}
                    ]
                )
                print("DEBUG: Language buttons sent.", flush=True)
                await redis_service.set_user_state(phone_number, "AWAITING_LANG")

            elif state == "AWAITING_LANG":
                print("DEBUG: State is AWAITING_LANG, re-sending buttons...", flush=True)
                await whatsapp_service.send_interactive_buttons(
                    phone_number,
                    "Please select your language / الرجاء اختيار اللغة",
                    [
                        {"id": "lang_ar", "title": "العربية 🇸🇦"},
                        {"id": "lang_en", "title": "English 🇺🇸"}
                    ]
                )
                
            elif state == "MAIN_MENU":
                # AI Processing for text orders
                await whatsapp_service.send_text(phone_number, get_text("order_processing", lang))
                ai_response = await ai_service.process_text_order(text, lang)
                # TODO: Handle AI response (add to cart, confirm, etc.)
                await whatsapp_service.send_text(phone_number, f"AI Parsed: {ai_response}")

        # Handle Interactive Replies (Buttons/Lists)
        elif message_type == "interactive":
            interaction = message_body["interactive"]
            interaction_type = interaction["type"]
            
            if interaction_type == "button_reply":
                btn_id = interaction["button_reply"]["id"]
                
                if state == "AWAITING_LANG":
                    if btn_id == "lang_ar":
                        lang = "ar"
                    else:
                        lang = "en"
                    
                    await redis_service.set_user_state(phone_number, "MAIN_MENU", {"lang": lang})
                    
                    # Send Main Menu Options
                    await whatsapp_service.send_interactive_buttons(
                        phone_number,
                        get_text("welcome", lang),
                        [
                            {"id": "menu_browse", "title": "🍔 Menu"},
                            {"id": "view_cart", "title": "🛒 Cart"},
                            {"id": "support", "title": "📞 Support"}
                        ]
                    )
                
                elif btn_id == "menu_browse":
                    # Fetch Restaurants
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(select(Restaurant).where(Restaurant.is_active == True).limit(10))
                        restaurants = result.scalars().all()
                        
                        if not restaurants:
                            await whatsapp_service.send_text(phone_number, "No restaurants available currently.")
                            return

                        sections = [{
                            "title": "Restaurants",
                            "rows": [{"id": f"rest_{r.id}", "title": r.name, "description": r.description[:70] if r.description else ""} for r in restaurants]
                        }]
                        
                        await whatsapp_service.send_interactive_list(
                            phone_number,
                            "Select a restaurant:",
                            "View Restaurants",
                            sections
                        )
                        await redis_service.set_user_state(phone_number, "BROWSING_RESTAURANTS", {"lang": lang})

            elif interaction_type == "list_reply":
                list_id = interaction["list_reply"]["id"]
                
                if state == "BROWSING_RESTAURANTS" and list_id.startswith("rest_"):
                    restaurant_id = int(list_id.split("_")[1])
                    # Fetch Menus for Restaurant
                    # For simplicity, just showing a placeholder success message
                    # In real app, fetch menus -> categories -> items
                    await whatsapp_service.send_text(phone_number, f"You selected restaurant ID: {restaurant_id}. (Menu browsing to be implemented)")
                    # SIMULATION: Add a dummy item to cart for demonstration
                    dummy_item = {"id": 1, "name": "Burger Meal", "price": 15.0, "quantity": 1, "restaurant_id": restaurant_id}
                    await redis_service.add_to_cart(phone_number, dummy_item)
                    await whatsapp_service.send_text(phone_number, "✅ Added 'Burger Meal' to cart! (Simulated)")
                    
                    await redis_service.set_user_state(phone_number, "BROWSING_MENU", {"lang": lang, "restaurant_id": restaurant_id})

                elif btn_id == "view_cart":
                    cart = await redis_service.get_cart(phone_number)
                    if not cart:
                        await whatsapp_service.send_text(phone_number, "Your cart is empty.")
                        return
                    
                    cart_text = "🛒 *Your Cart:*\n\n"
                    total = 0
                    for item in cart:
                        item_total = item["price"] * item["quantity"]
                        cart_text += f"- {item['name']} x{item['quantity']} = ${item_total}\n"
                        total += item_total
                    
                    cart_text += f"\n*Total: ${total}*"
                    
                    await whatsapp_service.send_interactive_buttons(
                        phone_number,
                        cart_text,
                        [
                            {"id": "checkout", "title": "✅ Checkout"},
                            {"id": "clear_cart", "title": "❌ Clear Cart"},
                            {"id": "menu_browse", "title": "🍔 Add More"}
                        ]
                    )
                
                elif btn_id == "checkout":
                    await whatsapp_service.send_text(phone_number, "Please share your location to proceed with delivery. 📍")
                    await redis_service.set_user_state(phone_number, "AWAITING_LOCATION")
                
                elif btn_id == "clear_cart":
                    await redis_service.clear_cart(phone_number)
                    await whatsapp_service.send_text(phone_number, "Cart cleared.")
                    await redis_service.set_user_state(phone_number, "MAIN_MENU")

        # Handle Location
        elif message_type == "location":
            if state == "AWAITING_LOCATION":
                location = message_body["location"]
                lat = location["latitude"]
                lng = location["longitude"]
                
                # Create Order
                cart = await redis_service.get_cart(phone_number)
                if not cart:
                     await whatsapp_service.send_text(phone_number, "Cart is empty. Cannot checkout.")
                     return

                async with AsyncSessionLocal() as db:
                    # Find or create user (simplified)
                    result = await db.execute(select(User).where(User.phone_number == phone_number))
                    user = result.scalars().first()
                    if not user:
                        # Create guest user
                        user = User(phone_number=phone_number, full_name="Guest User")
                        db.add(user)
                        await db.commit()
                        await db.refresh(user)
                    
                    # Calculate total
                    total_amount = sum(item["price"] * item["quantity"] for item in cart)
                    restaurant_id = cart[0]["restaurant_id"] # Assuming single restaurant order
                    
                    order = Order(
                        restaurant_id=restaurant_id,
                        user_id=user.id,
                        status=OrderStatus.NEW,
                        total_amount=total_amount,
                        latitude=lat,
                        longitude=lng,
                        address="Location Shared via WhatsApp"
                    )
                    db.add(order)
                    await db.commit()
                    await db.refresh(order)
                    
                    # Add items
                    for item in cart:
                        order_item = OrderItem(
                            order_id=order.id,
                            menu_item_id=item.get("menu_item_id", 1), # Fallback if simulated
                            quantity=item["quantity"],
                            unit_price=item["price"],
                            total_price=item["price"] * item["quantity"]
                        )
                        db.add(order_item)
                    
                    await db.commit()
                    
                    await whatsapp_service.send_text(phone_number, f"🎉 Order #{order.id} placed successfully! We will notify you when it's accepted.")
                    await redis_service.clear_cart(phone_number)
                    await redis_service.set_user_state(phone_number, "MAIN_MENU")

bot_controller = BotController()
