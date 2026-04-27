from aiomax.buttons import KeyboardBuilder, CallbackButton
from src.config.settings import settings


def get_main_menu():
    """Главное меню со всеми разделами"""
    kb = KeyboardBuilder()

    # Добавляем все разделы из настроек
    for section_key, section_data in settings.SECTIONS.items():
        kb.row(CallbackButton(
            text=f"{section_data['emoji']} {section_data['name']}",
            payload=f"section_{section_key}"
        ))

    return kb