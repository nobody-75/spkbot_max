import logging

from aiomax import Router
from aiomax.types import Message
from aiomax.buttons import KeyboardBuilder, CallbackButton
from aiomax.filters import equals, state
from sqlalchemy import select

from src.bot.keyboards import get_main_menu
from src.database import AsyncSessionLocal, User

logger = logging.getLogger(__name__)
router = Router()


def get_confirmation_keyboard():
    """Клавиатура подтверждения регистрации"""
    kb = KeyboardBuilder()
    kb.row(
        CallbackButton(text="✅ Подтвердить", payload="confirm_registration"),
        CallbackButton(text="✏️ Изменить данные", payload="edit_registration"),
    )
    kb.row(CallbackButton(text="❌ Отменить регистрацию", payload="cancel_registration"))
    return kb


# ================= ОСНОВНОЙ ОБРАБОТЧИК /start =================

@router.on_message(equals("/start"))
async def cmd_start(message: Message, cursor):
    """Обработка команды /start"""
    max_id = str(message.sender.user_id)
    logger.info(f"Команда /start от пользователя {max_id}")

    async with AsyncSessionLocal() as db:
        stmt = select(User).filter(User.max_id == max_id)
        user = (await db.execute(stmt)).scalars().first()

        if user:
            await message.send(
                f"👋 С возвращением, {user.first_name} {user.second_name}!",
                keyboard=get_main_menu()
            )
            cursor.clear()
        else:
            await message.send(
                "📝 **Добро пожаловать!**\n\n"
                "Для продолжения давайте зарегистрируемся.\n\n"
                "👤 **Введите ваше имя:**",
                format='markdown'
            )
            cursor.change_state("waiting_for_first_name")


# ================= ОБРАБОТЧИКИ СООБЩЕНИЙ ДЛЯ FSM =================

@router.on_message(state("waiting_for_first_name"))
async def process_first_name(message: Message, cursor):
    """Обработка ввода имени"""
    text = message.body.text.strip()

    if text in ["❌ Отмена", "Отмена"]:
        cursor.clear()
        await message.send("❌ Регистрация отменена.")
        return

    if text == "⬅️ Назад":
        await message.send("📝 **Введите ваше имя:**", format='markdown')
        return

    data = cursor.get_data() or {}
    data["first_name"] = text
    cursor.change_data(data)

    await message.send("📝 **Введите фамилию:**", format='markdown')
    cursor.change_state("waiting_for_second_name")


@router.on_message(state("waiting_for_second_name"))
async def process_second_name(message: Message, cursor):
    """Обработка ввода фамилии"""
    text = message.body.text.strip()

    if text == "⬅️ Назад":
        await message.send("📝 **Введите ваше имя:**", format='markdown')
        cursor.change_state("waiting_for_first_name")
        return

    if text in ["❌ Отмена", "Отмена"]:
        cursor.clear()
        await message.send("❌ Регистрация отменена.")
        return

    data = cursor.get_data() or {}
    data["second_name"] = text
    cursor.change_data(data)

    await message.send("📚 **Введите номер группы:**", format='markdown')
    cursor.change_state("waiting_for_group")


@router.on_message(state("waiting_for_group"))
async def process_group(message: Message, cursor):
    """Обработка ввода группы"""
    text = message.body.text.strip()

    if text == "⬅️ Назад":
        await message.send("📝 **Введите фамилию:**", format='markdown')
        cursor.change_state("waiting_for_second_name")
        return

    if text in ["❌ Отмена", "Отмена"]:
        cursor.clear()
        await message.send("❌ Регистрация отменена.")
        return

    if not text:
        await message.send("❌ Группа не может быть пустой. Введите номер группы:")
        return

    data = cursor.get_data() or {}
    data["group"] = text.upper()
    cursor.change_data(data)

    await message.send(
        "📋 **Проверьте введенные данные:**\n\n"
        f"👤 Имя: `{data.get('first_name')}`\n"
        f"👤 Фамилия: `{data.get('second_name')}`\n"
        f"📚 Группа: `{data.get('group')}`\n\n"
        "Все данные верны?",
        format='markdown',
        keyboard=get_confirmation_keyboard()
    )
    cursor.change_state("confirmation")
