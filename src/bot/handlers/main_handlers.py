import aiomax
from src.bot.handlers.callback_router import router
from src.bot.keyboards import get_main_menu

# Создаем основной роутер
main_router = aiomax.Router()

# Команда /start
@main_router.on_command('start')
async def start_command(ctx: aiomax.CommandContext):
    await ctx.reply(
        f"👋 Привет, {ctx.message.sender.name}!\n\nЯ помогу найти документы"
        f" Северского промышленного колледжа.\n\n🏠"
        f"**Главное меню**\n\nВыберите раздел:",
        keyboard=get_main_menu(),
        format='markdown'
    )

# Добавляем callback роутер
main_router.add_router(router)











