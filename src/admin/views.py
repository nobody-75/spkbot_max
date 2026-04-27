from typing import Optional

from fastapi import Request
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database import AsyncSessionLocal, User
from src.database.models import Profile, Role


class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> bool:
        """Аутентификация администратора"""
        form_data = await request.form()
        email = form_data.get("username", "").strip()
        password = form_data.get("password", "")

        if not email or not password:
            return False

        user = await self._get_admin_user(email, password)
        if user:
            await self._create_user_session(request, user)
            return True

        return False

    async def logout(self, request: Request) -> bool:
        """Выход пользователя"""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Проверка аутентификации администратора"""
        return (
                request.session.get("user_id") is not None
                and request.session.get("role") == "Админ"
        )

    async def _get_admin_user(self, email: str, password: str) -> Optional[User]:
        """Получение пользователя с ролью администратора (исправлено)"""
        async with AsyncSessionLocal() as db:
            # Используем асинхронный select вместо синхронного query
            from src.database.models import Role
            stmt = (
                select(User)
                .options(joinedload(User.role_rel))
                .join(User.role_rel)
                .where(User.email == email)
                .where(Role.name == "Админ")
            )
            result = await db.execute(stmt)
            user = result.scalars().first()

            if user and user.password == password:
                return user
        return None

    async def _create_user_session(self, request: Request, user: User) -> None:
        """Создание сессии пользователя"""
        request.session.update({
            "user_id": user.id,
            "email": user.email,
            "role": user.role_rel.name
        })


class UserAdmin(ModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'
    column_list = ["id","login", "first_name", "second_name", "role_rel", "max_id"]
    column_searchable_list = ["first_name", "second_name", "email", "max_id"]
    form_excluded_columns = ["profile"]

    column_labels = {
        "id": "ID",
        "login": "Логин",
        "first_name": "Имя",
        "second_name": "Фамилия",
        "max_id": "Max ID",
        "password": "Пароль"
    }


class ProfileAdmin(ModelView, model=Profile):
    name = 'Профиль'
    name_plural = 'Профили'
    column_list = ["id", "user_display"]
    column_labels = {
        "id": "ID",
        "user_display": "Пользователь",
    }
    column_searchable_list = ["user"]

    def format_user(model, _):
        if hasattr(model, 'user') and model.user:
            first_name = getattr(model.user, 'first_name', '')
            second_name = getattr(model.user, 'second_name', '')
            return f"{first_name} {second_name}".strip()

        return "Не указан"

    column_formatters_detail = {
        "user_display": format_user,
    }



class RoleAdmin(ModelView, model=Role):
    name = 'Роль'
    name_plural = 'Роли'
    column_list = ["id", "name"]
    column_labels = {
        "id": "ID",
        "name": "Название роли",
    }
    column_searchable_list = ["name"]
