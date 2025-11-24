from typing import Dict

TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to Lion Delivery!",
        "order_received": "We have received your order.",
        "order_processing": "Your order is being processed.",
        "order_ready": "Your order is ready for pickup/delivery.",
        "select_language": "Please select your language:",
    },
    "ar": {
        "welcome": "مرحباً بك في ليون ديليفري!",
        "order_received": "لقد استلمنا طلبك.",
        "order_processing": "جاري تحضير طلبك.",
        "order_ready": "طلبك جاهز للاستلام/التوصيل.",
        "select_language": "الرجاء اختيار اللغة:",
    }
}

def get_text(key: str, lang: str = "ar") -> str:
    """
    Get translated text for a given key and language.
    Defaults to Arabic if language not found.
    """
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["ar"])
    return lang_dict.get(key, key)
