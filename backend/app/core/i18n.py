from typing import Dict

TRANSLATIONS = {
    "en": {
        # Welcome & Main Menu
        "welcome": "🦁 Welcome to Lion Delivery!\nWhat would you like to do?",
        "select_language": "Please select your language:",
        
        # Buttons
        "btn_menu": "🍔 Browse Menu",
        "btn_cart": "🛒 My Cart",
        "btn_support": "📞 Support",
        
        # Restaurant & Menu
        "restaurants": "Restaurants",
        "select_restaurant": "Select a restaurant to order from:",
        "view_restaurants": "View Restaurants",
        "no_restaurants": "No restaurants available at the moment.",
        "restaurant_not_found": "Restaurant not found.",
        "select_category": "Select a category:",
        "view_menu": "View Menu",
        "no_menu": "No menu available for this restaurant.",
        "select_item": "Select an item:",
        "view_items": "View Items",
        "no_items": "No items in this category.",
        "no_items_available": "No items available at the moment.",
        "item_not_found": "Item not found.",
        "price": "Price",
        
        # Add to Cart
        "add_one": "Add 1 ➕",
        "add_two": "Add 2 ➕➕",
        "enter_quantity": "Please enter the quantity (1-99):",
        "invalid_quantity": "Please enter a valid number between 1 and 99.",
        "item_added": "Added {quantity}x {name} to cart! (Total items: {cart_count})",
        "continue_shopping": "🛍️ Continue",
        "view_cart": "🛒 View Cart",
        
        # Cart
        "your_cart": "Your Cart",
        "cart_empty": "Your cart is empty! Start by browsing the menu.",
        "total": "Total",
        "checkout": "✅ Checkout",
        "clear_cart": "🗑️ Clear Cart",
        "add_more": "➕ Add More",
        "cart_cleared": "Your cart has been cleared.",
        "select_to_edit": "Select item to edit:",
        "edit_cart": "Edit your cart items:",
        
        # Checkout & Order
        "share_location": "📍 Please share your location for delivery.\n\nYou can send a location pin 📍 or just write your address below 📝",
        "share_location_hybrid": "📍 Please share your location for delivery.\n\nYou can send a location pin 📍 or just write your address below 📝",
        "ask_name": "👤 One last thing, what's your name?",
        "confirm_name_address": "📝 Please confirm your delivery info:\n\n👤 Name: {name}\n📍 Address: {address}",
        "btn_use_previous": "✅ Previous Info",
        "btn_enter_new": "🔄 New Info",
        "location_not_expected": "We weren't expecting a location. Please start a new order.",
        "order_confirmed": "Order #{order_id} confirmed!\n\n📦 *Your Order:*\n{items}\n\n💰 Subtotal: ${subtotal:.2f}\n🚗 Delivery: ${delivery_fee:.2f}\n💵 *Total: ${total:.2f}*\n\nWe'll notify you when your order is accepted!",
        "order_cancelled": "Your order has been cancelled.",
        
        # Order Status
        "order_received": "We have received your order.",
        "order_processing": "Your order is being prepared.",
        "order_ready": "Your order is ready for delivery!",
        "order_on_way": "Your order is on its way! 🚗",
        "order_delivered": "Your order has been delivered! Enjoy! 🎉",
        
        # Support
        "support_message": "📞 How can we help you?\n\nType your message and we'll get back to you shortly.",
        "support_received": "Thank you! We've received your message and will respond soon.",
        "end_support": "End Chat",
        "support_ended": "Support chat ended. Thank you for contacting us!",
        
        # Navigation
        "back": "⬅️ Back",
        "back_to_menu": "🏠 Main Menu",

        # AI & Processing
        "processing_order": "🤖 Processing your order...",
        "ai_error": "Sorry, I couldn't understand that. Please use the menu buttons.",
        "use_menu": "Please use the menu to browse and order.",

        # Reorder
        "btn_reorder": "🔄 Previous Orders",
        "no_previous_orders": "You don't have any previous orders yet.",
        "select_order_to_reorder": "📋 Your recent orders:",
        "reorder_added": "✅ Added to cart!\n\n{items}\n\n💰 Total: ${total:.2f}",
        "view_orders": "View Orders",

        # Loyalty
        "btn_loyalty": "🎁 My Points",
        "loyalty_status": "🏆 Your Loyalty Status:\n\n{tier_icon} Level: {tier}\n💰 Points: {points}\n📦 Orders: {orders}\n💵 Total Spent: ${spent:.2f}",
        "loyalty_progress": "\n\n📈 {points_needed} points to reach {next_tier}!",
        "points_earned": "🎉 You earned {points} points!\n📊 Balance: {total} points",

        # Favorites
        "btn_favorites": "❤️ Favorites",
        "no_favorites": "You don't have any favorite restaurants yet.",
        "your_favorites": "❤️ Your Favorite Restaurants:",
        "added_to_favorites": "❤️ Added to favorites!",
        "removed_from_favorites": "💔 Removed from favorites.",
        "add_to_favorites": "❤️ Add to Favorites",
        "suggest_favorite": "💡 You've ordered from {restaurant} {count} times! Add to favorites?",

        # Reviews
        "rate_order": "⭐ How was your order from {restaurant}?\nRate from 1 (bad) to 5 (excellent)",
        "thanks_for_review": "Thanks for your feedback! 💚",
        "sorry_bad_experience": "We're sorry! What was the problem?",
        "review_bonus": "🎁 +{points} bonus points for your review!",

        # One-Shot Ordering
        "order_preview": "✅ Order Ready!\n\n📦 Items:\n{items}\n\n🏪 From: {restaurant}\n📍 To: {address}\n💰 Total: ${total:.2f}",
        "confirm_order_btn": "✅ Confirm",
        "modify_order_btn": "✏️ Modify",
        "cancel_order_btn": "❌ Cancel",
        "which_restaurant": "🤔 Which restaurant?\n{options}",
        "which_size": "📏 Which size?\n{options}",
        "item_not_found_suggestions": "🔍 Didn't find \"{query}\" exactly, but found:\n{suggestions}\n\nType the number to order.",

        # Conversation
        "thinking": "🤔 Let me check...",
    },
    "ar": {
        # Welcome & Main Menu
        "welcome": "🦁 مرحباً بك في ليون ديليفري!\nماذا تريد أن تفعل؟",
        "select_language": "الرجاء اختيار اللغة:",
        
        # Buttons
        "btn_menu": "🍔 تصفح القائمة",
        "btn_cart": "🛒 سلتي",
        "btn_support": "📞 الدعم",
        
        # Restaurant & Menu
        "restaurants": "المطاعم",
        "select_restaurant": "اختر مطعماً للطلب منه:",
        "view_restaurants": "عرض المطاعم",
        "no_restaurants": "لا توجد مطاعم متاحة حالياً.",
        "restaurant_not_found": "المطعم غير موجود.",
        "select_category": "اختر قسماً:",
        "view_menu": "عرض القائمة",
        "no_menu": "لا توجد قائمة متاحة لهذا المطعم.",
        "select_item": "اختر صنفاً:",
        "view_items": "عرض الأصناف",
        "no_items": "لا توجد أصناف في هذا القسم.",
        "no_items_available": "لا توجد أصناف متاحة حالياً.",
        "item_not_found": "الصنف غير موجود.",
        "price": "السعر",
        
        # Add to Cart
        "add_one": "إضافة 1 ➕",
        "add_two": "إضافة 2 ➕➕",
        "enter_quantity": "الرجاء إدخال الكمية (1-99):",
        "invalid_quantity": "الرجاء إدخال رقم صحيح بين 1 و 99.",
        "item_added": "تمت إضافة {quantity}x {name} إلى السلة! (إجمالي الأصناف: {cart_count})",
        "continue_shopping": "🛍️ متابعة",
        "view_cart": "🛒 عرض السلة",
        
        # Cart
        "your_cart": "سلتك",
        "cart_empty": "سلتك فارغة! ابدأ بتصفح القائمة.",
        "total": "المجموع",
        "checkout": "✅ إتمام الطلب",
        "clear_cart": "🗑️ إفراغ السلة",
        "add_more": "➕ إضافة المزيد",
        "cart_cleared": "تم إفراغ سلتك.",
        "select_to_edit": "اختر صنفاً للتعديل:",
        "edit_cart": "عدّل أصناف سلتك:",
        
        # Checkout & Order
        "share_location": "📍 وين حابب نوصلك الطلب؟\n\nفيك تبعت لوكيشن (Drip Pin) 📍 أو تكتب عنوانك بالتفصيل هون 📝",
        "share_location_hybrid": "📍 وين حابب نوصلك الطلب؟\n\nفيك تبعت لوكيشن (Drip Pin) 📍 أو تكتب عنوانك بالتفصيل هون 📝",
        "ask_name": "👤 آخر خطوة، شو الاسم الكريم؟",
        "confirm_name_address": "📝 مراجعة بيانات التوصيل:\n\n👤 الاسم: {name}\n📍 العنوان: {address}",
        "btn_use_previous": "✅ البيانات السابقة",
        "btn_enter_new": "🔄 بيانات جديدة",
        "location_not_expected": "لم نكن نتوقع موقعاً. الرجاء بدء طلب جديد.",
        "order_confirmed": "تم تأكيد الطلب #{order_id}!\n\n📦 *طلبك:*\n{items}\n\n💰 المجموع الفرعي: ${subtotal:.2f}\n🚗 التوصيل: ${delivery_fee:.2f}\n💵 *الإجمالي: ${total:.2f}*\n\nسنعلمك عند قبول طلبك!",
        "order_cancelled": "تم إلغاء طلبك.",
        
        # Order Status
        "order_received": "لقد استلمنا طلبك.",
        "order_processing": "جاري تحضير طلبك.",
        "order_ready": "طلبك جاهز للتوصيل!",
        "order_on_way": "طلبك في الطريق! 🚗",
        "order_delivered": "تم توصيل طلبك! بالعافية! 🎉",
        
        # Support
        "support_message": "📞 كيف يمكننا مساعدتك؟\n\nاكتب رسالتك وسنرد عليك قريباً.",
        "support_received": "شكراً لك! استلمنا رسالتك وسنرد عليك قريباً.",
        "end_support": "إنهاء المحادثة",
        "support_ended": "انتهت محادثة الدعم. شكراً لتواصلك معنا!",
        
        # Navigation
        "back": "⬅️ رجوع",
        "back_to_menu": "🏠 القائمة الرئيسية",

        # AI & Processing
        "processing_order": "🤖 جاري معالجة طلبك...",
        "ai_error": "عذراً، لم أستطع فهم ذلك. الرجاء استخدام أزرار القائمة.",
        "use_menu": "الرجاء استخدام القائمة للتصفح والطلب.",

        # Reorder
        "btn_reorder": "🔄 طلباتي السابقة",
        "no_previous_orders": "ما عندك طلبات سابقة بعد.",
        "select_order_to_reorder": "📋 آخر طلباتك:",
        "reorder_added": "✅ تم الإضافة للسلة!\n\n{items}\n\n💰 المجموع: ${total:.2f}",
        "view_orders": "عرض الطلبات",

        # Loyalty
        "btn_loyalty": "🎁 نقاطي",
        "loyalty_status": "🏆 حسابك:\n\n{tier_icon} المستوى: {tier}\n💰 النقاط: {points}\n📦 الطلبات: {orders}\n💵 إجمالي المصروف: ${spent:.2f}",
        "loyalty_progress": "\n\n📈 باقي {points_needed} نقطة للوصول لـ {next_tier}!",
        "points_earned": "🎉 ربحت {points} نقطة!\n📊 رصيدك: {total} نقطة",

        # Favorites
        "btn_favorites": "❤️ المفضلة",
        "no_favorites": "ما عندك مطاعم مفضلة بعد.",
        "your_favorites": "❤️ مطاعمك المفضلة:",
        "added_to_favorites": "❤️ تمت الإضافة للمفضلة!",
        "removed_from_favorites": "💔 تمت الإزالة من المفضلة.",
        "add_to_favorites": "❤️ أضف للمفضلة",
        "suggest_favorite": "💡 طلبت من {restaurant} {count} مرات! بدك تضيفه للمفضلة؟",

        # Reviews
        "rate_order": "⭐ كيف كان طلبك من {restaurant}؟\nقيّم من 1 (سيء) إلى 5 (ممتاز)",
        "thanks_for_review": "شكراً على رأيك! 💚",
        "sorry_bad_experience": "نأسف! شو كانت المشكلة؟",
        "review_bonus": "🎁 +{points} نقطة إضافية للتقييم!",

        # One-Shot Ordering
        "order_preview": "✅ طلبك جاهز!\n\n📦 الأصناف:\n{items}\n\n🏪 من: {restaurant}\n📍 إلى: {address}\n💰 المجموع: ${total:.2f}",
        "confirm_order_btn": "✅ تأكيد",
        "modify_order_btn": "✏️ تعديل",
        "cancel_order_btn": "❌ إلغاء",
        "which_restaurant": "🤔 من أي مطعم؟\n{options}",
        "which_size": "📏 أي حجم؟\n{options}",
        "item_not_found_suggestions": "🔍 ما لقيت \"{query}\" بالضبط، بس لقيت:\n{suggestions}\n\nاكتب الرقم للطلب.",

        # Conversation
        "thinking": "🤔 خليني شوف...",
    }
}

def get_text(key: str, lang: str = "ar", **kwargs) -> str:
    """
    Get translated text for a given key and language.
    Supports keyword arguments for string formatting.
    Defaults to Arabic if language not found.

    Example:
        get_text("item_added", "en", quantity=2, name="Pizza", cart_count=3)
    """
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["ar"])
    text = lang_dict.get(key, key)

    # If kwargs provided, format the string
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # Return unformatted if placeholders don't match
    return text


def get_available_languages() -> list:
    """Get list of supported language codes."""
    return list(TRANSLATIONS.keys())


def is_rtl(lang: str) -> bool:
    """Check if language is right-to-left."""
    return lang in ("ar", "he", "fa", "ur")


# Error messages for API responses
ERROR_MESSAGES = {
    "en": {
        "not_found": "Resource not found",
        "unauthorized": "Unauthorized access",
        "forbidden": "Access denied",
        "validation_error": "Validation error",
        "server_error": "Internal server error",
        "rate_limit": "Too many requests. Please try again later.",
        "invalid_credentials": "Invalid email or password",
        "inactive_user": "User account is inactive",
        "order_not_found": "Order not found",
        "restaurant_not_found": "Restaurant not found",
        "item_not_found": "Menu item not found",
        "cart_empty": "Cart is empty",
        "invalid_status": "Invalid order status",
        "driver_not_found": "Driver not found",
        "already_assigned": "Order already assigned to a driver",
    },
    "ar": {
        "not_found": "المورد غير موجود",
        "unauthorized": "غير مصرح بالوصول",
        "forbidden": "تم رفض الوصول",
        "validation_error": "خطأ في التحقق",
        "server_error": "خطأ في الخادم",
        "rate_limit": "طلبات كثيرة. الرجاء المحاولة لاحقاً.",
        "invalid_credentials": "البريد أو كلمة المرور غير صحيحة",
        "inactive_user": "حساب المستخدم غير نشط",
        "order_not_found": "الطلب غير موجود",
        "restaurant_not_found": "المطعم غير موجود",
        "item_not_found": "الصنف غير موجود",
        "cart_empty": "السلة فارغة",
        "invalid_status": "حالة الطلب غير صحيحة",
        "driver_not_found": "السائق غير موجود",
        "already_assigned": "الطلب مخصص لسائق بالفعل",
    },
}


def get_error(key: str, lang: str = "ar") -> str:
    """Get translated error message."""
    lang_dict = ERROR_MESSAGES.get(lang, ERROR_MESSAGES["ar"])
    return lang_dict.get(key, key)

