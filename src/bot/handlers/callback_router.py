import logging
import secrets
import string

import aiomax
from aiomax.buttons import KeyboardBuilder, CallbackButton
from src.bot.keyboards import get_main_menu, get_categories_menu
from src.bot.handlers.content import show_category_files
from src.database import AsyncSessionLocal, User, Role
from sqlalchemy import select

router = aiomax.Router()
logger = logging.getLogger(__name__)

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
async def handle_callbacks(cb: aiomax.Callback, cursor):
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
    if payload.startswith("section_"):
        section_key = payload.split("_")[1]
        await cb.answer(text="📚 Загрузка...")
        await cb.message.edit(
            f"📚 **Выберите категорию:**",
            keyboard=get_categories_menu(section_key),
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

    # ================= РЕГИСТРАЦИЯ =================

    if payload == "cancel_registration":
        cursor.clear()
        await cb.send("❌ Регистрация отменена.")
        await cb.answer()
        return

    if payload == "back_registration":
        state = cursor.get_state()
        if state == "waiting_for_first_name":
            await cb.send("📝 **Введите ваше имя:**", format='markdown')
            cursor.change_state("waiting_for_first_name")
        elif state == "waiting_for_second_name":
            await cb.send("📝 **Введите вашу фамилию:**", format='markdown')
            cursor.change_state("waiting_for_first_name")
        elif state == "waiting_for_group":
            await cb.send("📝 **Введите фамилию:**", format='markdown')
            cursor.change_state("waiting_for_second_name")
        elif state == "confirmation":
            await cb.send("📚 **Введите номер группы:**", format='markdown')
            cursor.change_state("waiting_for_group")
        elif state == "editing":
            await show_confirmation_callback(cb, cursor)
        await cb.answer()
        return

    if payload == "confirm_registration":
        state = cursor.get_state()
        if state != "confirmation":
            await cb.answer()
            return

        user_data = cursor.get_data()
        async with AsyncSessionLocal() as db:
            try:
                role_stmt = select(Role).filter(Role.name == "Пользователь")
                role_res = await db.execute(role_stmt)
                role = role_res.scalars().first()

                password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

                new_user = User(
                    first_name=user_data['first_name'],
                    second_name=user_data['second_name'],
                    login=f"user_{user_data['first_name'].lower()}_{user_data['second_name'].lower()}_{cb.user.user_id}",
                    group=user_data['group'],
                    max_id=str(cb.user.user_id),
                    role_id=role.id if role else 2,
                    password=password
                )
                db.add(new_user)
                await db.commit()

                await cb.send(
                    f"🎉 **Регистрация успешно завершена!**\n\n"
                    f"Добро пожаловать, {user_data['first_name']}!\n\n"
                    f"Ваш ID в системе: `{new_user.max_id}`",
                    keyboard=get_main_menu(),
                    format='markdown'
                )
                cursor.clear()
            except Exception as e:
                await db.rollback()
                logger.error(f"Ошибка сохранения пользователя: {e}", exc_info=True)
                await cb.send("❌ Произошла ошибка при сохранении данных. Попробуйте ещё раз.")

        await cb.answer()
        return

    if payload == "edit_registration":
        state = cursor.get_state()
        if state != "confirmation":
            await cb.answer()
            return

        kb = get_edit_keyboard()
        await cb.send("✏️ **Выберите поле для редактирования:**", format='markdown', keyboard=kb)
        await cb.answer()
        return

    if payload.startswith("edit_"):
        state = cursor.get_state()
        if state != "editing":
            await cb.answer()
            return

        if payload == "edit_first_name":
            await cb.send("✏️ **Введите новое имя:**", format='markdown')
            cursor.change_state("waiting_for_first_name")
        elif payload == "edit_second_name":
            await cb.send("✏️ **Введите новую фамилию:**", format='markdown')
            cursor.change_state("waiting_for_second_name")
        elif payload == "edit_group":
            await cb.send("📚 **Введите номер группы:**", format='markdown')
            cursor.change_state("waiting_for_group")
        elif payload in ["finish_edit", "cancel_edit"]:
            await show_confirmation_callback(cb, cursor)

        await cb.answer()
        return

    logger.warning(f"Неизвестный payload: {payload}")
    await cb.answer(text="❌ Неизвестная команда")


async def show_confirmation_callback(cb, cursor):
    """Показать подтверждение данных"""
    data = cursor.get_data()
    text = (
        "📋 **Проверьте введенные данные:**\n\n"
        f"👤 Имя: `{data.get('first_name')}`\n"
        f"👤 Фамилия: `{data.get('second_name')}`\n"
        f"📚 Группа: `{data.get('group')}`\n\n"
        "Все данные верны?"
    )

    kb = get_confirmation_keyboard()
    await cb.send(text, keyboard=kb, format='markdown')
    cursor.change_state("confirmation")


def get_edit_keyboard():
    """Клавиатура редактирования данных"""
    kb = KeyboardBuilder()
    buttons = [
        CallbackButton(text="👤 Имя", payload="edit_first_name"),
        CallbackButton(text="👤 Фамилия", payload="edit_second_name"),
        CallbackButton(text="📚 Группа", payload="edit_group"),
        CallbackButton(text="✅ Завершить редактирование", payload="finish_edit"),
        CallbackButton(text="❌ Отменить редактирование", payload="cancel_edit"),
    ]
    for button in buttons:
        kb.row(button)
    return kb


def get_confirmation_keyboard():
    """Клавиатура подтверждения регистрации"""
    kb = KeyboardBuilder()
    kb.row(
        CallbackButton(text="✅ Подтвердить", payload="confirm_registration"),
        CallbackButton(text="✏️ Изменить данные", payload="edit_registration"),
    )
    kb.row(CallbackButton(text="❌ Отменить регистрацию", payload="cancel_registration"))
    return kb


