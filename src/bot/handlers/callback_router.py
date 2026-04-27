import aiomax
import logging
from src.keyboards import get_main_menu, get_categories_menu
from src.handlers.content import show_category_files

router = aiomax.Router()


async def send_file(cb: aiomax.Callback, file_url: str):
    """Отправляет файл пользователю"""
    try:
        logger.info(f"Отправка файла: {file_url}")
        await cb.answer(text="⏳ Загружаю файл...")

        import requests
        from urllib.parse import unquote

        response = requests.get(file_url, timeout=30)
        response.raise_for_status()

        file_name = unquote(file_url.split('/')[-1])

        await cb.message.edit(
            f"✅ **Файл:** {file_name}\n\n🔗 **Ссылка для скачивания:**\n{file_url}",
            format='markdown'
        )

    except Exception as e:
        logger.error(f"Ошибка при отправке файла: {e}", exc_info=True)
        await cb.answer(text=f"❌ Ошибка: {str(e)}")


@router.on_button_callback()
async def handle_callbacks(cb: aiomax.Callback):
    payload = cb.payload
    logger.info(f"Получен callback: {payload}")

    # Главное меню
    if payload == "main_menu":
        await cb.answer(text="🏠 Главное меню")
        await cb.message.edit(
            "🏠 **Главное меню**\n\nВыберите раздел:",
            keyboard=get_main_menu(),
            format='markdown'
        )
        return

    # Выбор раздела с разделителем |
    if payload.startswith("section|"):
        section_key = payload.split("|")[1]
        await cb.answer(text="📚 Загрузка...")
        await cb.message.edit(
            f"📚 **Выберите категорию:**",
            keyboard=get_categories_menu(section_key),
            format='markdown'
        )
        return

    # Выбор категории с разделителем |
    if payload.startswith("category|"):
        parts = payload.split("|")
        if len(parts) >= 3:
            section_key = parts[1]
            category_name = parts[2]
            logger.info(f"Выбрана категория: section={section_key}, category={category_name}")
            await show_category_files(cb, section_key, category_name)
        else:
            logger.error(f"Некорректный category payload: {payload}")
            await cb.answer(text="❌ Ошибка формата данных")
        return

    # Пагинация с разделителем |
    if payload.startswith("page|"):
        parts = payload.split("|")
        if len(parts) >= 4:
            section_key = parts[1]
            category_name = parts[2]
            page = int(parts[3])
            logger.info(f"Пагинация: section={section_key}, category={category_name}, page={page}")
            await show_category_files(cb, section_key, category_name, page)
        else:
            logger.error(f"Некорректный page payload: {payload}")
        return

    # Отправка файла с разделителем |
    if payload.startswith("file|"):
        file_url = payload.replace("file|", "")
        logger.info(f"Запрос на отправку файла: {file_url}")
        await send_file(cb, file_url)
        return

    logger.warning(f"Неизвестный payload: {payload}")
    await cb.answer(text="❌ Неизвестная команда")