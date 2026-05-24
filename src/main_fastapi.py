# src/main.py (ОБНОВЛЁННЫЙ)
import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from src.admin.views import UserAdmin, RoleAdmin, ProfileAdmin, ButtonAdmin, FormAdmin, QuestionAdmin, FormQuestionAdmin, SubmissionAdmin, SubmissionAnswerAdmin
#from src.admin.views import AdminAuth
from src.config.settings import settings
from src.database import engine

# ================= НОВОЕ: ИМПОРТЫ API ДЛЯ МИНИ-ПРИЛОЖЕНИЯ =================
from src.api import buttons_router, forms_router, submissions_router, my_router

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
        "http://localhost:8080",
        "*",  # Для разработки, потом убрать
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

# Вьюшки для кнопок и форм
admin.add_view(ButtonAdmin)
admin.add_view(FormAdmin)
admin.add_view(QuestionAdmin)
admin.add_view(FormQuestionAdmin)

# Вьюшки для заявок
admin.add_view(SubmissionAdmin)
admin.add_view(SubmissionAnswerAdmin)

# ================= НОВОЕ: ПОДКЛЮЧЕНИЕ API ДЛЯ МИНИ-ПРИЛОЖЕНИЯ =================
app.include_router(buttons_router)
app.include_router(forms_router)
app.include_router(submissions_router)
app.include_router(my_router)

# ================= НОВОЕ: КОРНЕВОЙ ЭНДПОИНТ =================
@app.get("/")
async def root():
    return {"message": "MAX Bot API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ================= БЫЛО: ЗАПУСК =================
if __name__ == "__main__":
    uvicorn.run(
        "main_fastapi:app",  # Исправлено: правильный путь к модулю
        host='0.0.0.0',
        port=8000,
        reload=True
    )