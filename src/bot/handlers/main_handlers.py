import aiomax
from src.bot.handlers.callback_router import router as callback_router
from src.bot.handlers.registration import router as registration_router
from src.bot.keyboards import get_main_menu

# Создаем основной роутер
main_router = aiomax.Router()

# Добавляем роутер регистрации (обрабатывает /start и регистрацию)
main_router.add_router(registration_router)

# Добавляем callback роутер (навигация по контенту)
main_router.add_router(callback_router)











