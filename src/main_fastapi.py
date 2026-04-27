# src/main.py (ОБНОВЛЁННЫЙ)
import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware  # НОВОЕ

from src.admin.views import UserAdmin, RoleAdmin, ProfileAdmin
#from src.admin.views import AdminAuth
from src.config.settings import settings
from src.database import engine

# НОВОЕ: импорты API для мини-приложения

app = FastAPI(
    title="MAX Bot API",
    description="API для админ-панели и мини-приложения"
)

# ================= НОВОЕ: CORS ДЛЯ МИНИ-ПРИЛОЖЕНИЯ =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.max.ru",
        "https://*.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= БЫЛО: АДМИНКА =================
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

#authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

admin = Admin(
    app=app,
    engine=engine,
 #   authentication_backend=authentication_backend,
    title="Админ-панель"
)

admin.add_view(UserAdmin)
admin.add_view(RoleAdmin)
admin.add_view(ProfileAdmin)

# ================= НОВОЕ: ПОДКЛЮЧЕНИЕ API =================

if __name__ == "__main__":
    uvicorn.run(
        "main_fastapi:app",
        host='0.0.0.0',
        port=8000,
        reload=True
    )