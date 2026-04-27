import logging
from aiomax.buttons import KeyboardBuilder, CallbackButton
from src.config.settings import settings

logger = logging.getLogger(__name__)


def get_categories_menu(section_key: str):
    kb = KeyboardBuilder()
    section_data = settings.SECTIONS.get(section_key)

    if not section_data:
        from .menu import get_main_menu
        return get_main_menu()

    for category_name, url in section_data["categories"].items():
        display_name = category_name if len(category_name) <= 40 else category_name[:37] + "..."
        # Используем | как разделитель
        kb.row(CallbackButton(
            text=f"📁 {display_name}",
            payload=f"category|{section_key}|{category_name}"  # <-- здесь |
        ))

    kb.row(CallbackButton(text="🔙 Главное меню", payload="main_menu"))
    return kb