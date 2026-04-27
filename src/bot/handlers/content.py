import aiomax
import logging
from src.services.parser import parse_files_from_page
from src.keyboards.files_menu import get_files_menu
from src.config.settings import settings

logger = logging.getLogger(__name__)


async def show_category_files(cb: aiomax.Callback, section_key: str, category_name: str, page: int = 0):
    """Показывает файлы выбранной категории"""

    logger.info(f"show_category_files вызван: section={section_key}, category={category_name}, page={page}")

    # Получаем URL категории
    section_data = settings.SECTIONS.get(section_key)
    if not section_data:
        logger.error(f"Раздел не найден: {section_key}")
        await cb.answer(text="❌ Раздел не найден")
        return

    logger.info(f"Данные раздела: {section_data.get('name')}")

    url = section_data["categories"].get(category_name)
    if not url:
        logger.error(f"Категория не найдена: {category_name} в разделе {section_key}")
        logger.info(f"Доступные категории: {list(section_data['categories'].keys())}")
        await cb.answer(text="❌ Категория не найдена")
        return

    logger.info(f"URL категории: {url}")
    await cb.answer(text="⏳ Загружаю документы...")

    # Парсим файлы со страницы
    files = parse_files_from_page(url)
    logger.info(f"Найдено файлов: {len(files)}")

    if not files:
        logger.warning(f"Документы не найдены по URL: {url}")
        await cb.message.edit(
            f"📁 **{category_name}**\n\n❌ Документов не найдено",
            format='markdown'
        )
        return

    # Получаем клавиатуру с файлами
    keyboard, total_pages = get_files_menu(files, section_key, category_name, page)
    logger.info(f"Создана клавиатура, всего страниц: {total_pages}")

    page_info = f" (страница {page + 1} из {total_pages})" if total_pages > 1 else ""

    await cb.message.edit(
        f"📄 **{category_name}** — {len(files)} документов{page_info}\n\nВыберите файл:",
        keyboard=keyboard,
        format='markdown'
    )
    logger.info("Сообщение с файлами отправлено")