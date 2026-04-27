import logging
from src.config.settings import settings
import aiomax
import asyncio
from src.bot.handlers import main_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

bot = aiomax.Bot(settings.TOKEN_BOT)

# Регистрируем основной роутер
bot.add_router(main_router)

async def main():
    logger.info("Запуск бота...")
    try:
        # Сначала запускаем поллинг
        await bot.start_polling()
        logger.info("Бот успешно запущен")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())