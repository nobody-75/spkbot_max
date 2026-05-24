from typing import Optional, Any

from fastapi import Request
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database import AsyncSessionLocal, User
from src.database.models import Profile, Role, Button, Form, Question, FormQuestion, Submission, SubmissionAnswer


class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> bool:
        """Аутентификация администратора"""
        form_data = await request.form()
        login = form_data.get("username", "").strip()
        password = form_data.get("password", "")

        if not login or not password:
            return False

        user = await self._get_admin_user(login, password)
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


# =====================================================
# ВЬЮШКИ ДЛЯ ОСНОВНЫХ ПОЛЬЗОВАТЕЛЕЙ
# =====================================================

class UserAdmin(ModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'
    icon = 'mdi-account'

    column_list = ["id", "login", "first_name", "second_name", "role_rel", "max_id"]
    column_searchable_list = ["first_name", "second_name", "login", "max_id"]
    column_filters = ["role_rel"]

    column_labels = {
        "id": "ID",
        "login": "Логин",
        "first_name": "Имя",
        "second_name": "Фамилия",
        "max_id": "Max ID",
        "role_rel": "Роль",
        "password": "Пароль"
    }

    form_columns = ["first_name", "second_name", "login", "max_id", "role_id", "password"]


class ProfileAdmin(ModelView, model=Profile):
    name = 'Профиль'
    name_plural = 'Профили'
    icon = 'mdi-account-details'

    column_list = ["id", "user", "user_display"]
    column_labels = {
        "id": "ID",
        "user": "Пользователь",
        "user_display": "ФИО",
    }

    def format_user(model: Any, _: Any) -> str:
        if hasattr(model, 'user') and model.user:
            first_name = getattr(model.user, 'first_name', '')
            second_name = getattr(model.user, 'second_name', '')
            return f"{first_name} {second_name}".strip()
        return "Не указан"

    column_formatters_detail = {"user_display": format_user}


class RoleAdmin(ModelView, model=Role):
    name = 'Роль'
    name_plural = 'Роли'
    icon = 'mdi-shield-account'

    column_list = ["id", "name"]
    column_labels = {
        "id": "ID",
        "name": "Название роли",
    }
    column_searchable_list = ["name"]


# =====================================================
# ВЬЮШКИ ДЛЯ КНОПОК И ФОРМ
# =====================================================

class ButtonAdmin(ModelView, model=Button):
    name = 'Кнопка'
    name_plural = 'Кнопки'
    icon = 'mdi-button-cursor'

    column_list = ["id", "title", "icon", "is_active", "sort_order", "created_at"]
    column_searchable_list = ["title"]
    column_filters = ["is_active", "sort_order"]
    column_labels = {
        "id": "ID",
        "title": "Название",
        "icon": "Иконка",
        "is_active": "Активна",
        "sort_order": "Порядок",
        "created_at": "Создано",
    }

    form_columns = ["title", "icon", "is_active", "sort_order"]
    form_widget_args = {
        'icon': {
            'placeholder': '📄 (emoji или иконка)'
        }
    }


class FormAdmin(ModelView, model=Form):
    name = 'Форма'
    name_plural = 'Формы'
    icon = 'mdi-form-select'

    column_list = ["id", "button", "title", "created_at"]
    column_searchable_list = ["title", "description"]
    column_filters = ["button"]
    column_labels = {
        "id": "ID",
        "button": "Кнопка",
        "title": "Заголовок",
        "description": "Описание",
        "created_at": "Создано",
        "form_questions": "Вопросы"
    }

    form_columns = ["button_id", "title", "description"]


class QuestionAdmin(ModelView, model=Question):
    name = 'Вопрос'
    name_plural = 'Вопросы'
    icon = 'mdi-help-circle'

    column_list = ["id", "question_text", "field_type", "is_active", "created_at"]
    column_searchable_list = ["question_text"]
    column_filters = ["field_type", "is_active"]
    column_labels = {
        "id": "ID",
        "question_text": "Текст вопроса",
        "field_type": "Тип поля",
        "placeholder": "Подсказка",
        "options": "Варианты",
        "validation_regex": "Regex валидации",
        "is_active": "Активен",
        "created_at": "Создано",
    }

    form_columns = ["question_text", "field_type", "placeholder", "options", "validation_regex", "is_active"]
    form_widget_args = {
        'field_type': {
            'choices': [
                ('text', 'Текст (одна строка)'),
                ('textarea', 'Текст (многострочное)'),
                ('email', 'Email'),
                ('phone', 'Телефон'),
                ('number', 'Число'),
                ('select', 'Выпадающий список'),
                ('date', 'Дата'),
            ]
        },
        'options': {
            'type': 'json',
            'placeholder': '{"options": ["Вариант 1", "Вариант 2"]}'
        }
    }


class FormQuestionAdmin(ModelView, model=FormQuestion):
    name = 'Вопрос формы'
    name_plural = 'Вопросы форм'
    icon = 'mdi-form-dropdown'

    column_list = ["id", "form", "question", "sort_order", "is_required"]
    column_filters = ["form", "question", "is_required"]
    column_labels = {
        "id": "ID",
        "form": "Форма",
        "question": "Вопрос",
        "sort_order": "Порядок",
        "is_required": "Обязательный",
        "created_at": "Создано",
    }

    form_columns = ["form_id", "question_id", "sort_order", "is_required"]


# =====================================================
# ВЬЮШКИ ДЛЯ ЗАЯВОК
# =====================================================

class SubmissionAdmin(ModelView, model=Submission):
    name = 'Заявка'
    name_plural = 'Заявки'
    icon = 'mdi-file-document'

    column_list = ["id", "button", "user", "status", "created_at", "updated_at"]
    column_searchable_list = ["status"]
    column_filters = ["status", "button", "user", "created_at"]
    column_labels = {
        "id": "ID",
        "button": "Кнопка",
        "user": "Пользователь",
        "status": "Статус",
        "admin_comment": "Комментарий администратора",
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "answers": "Ответы"
    }

    form_columns = ["button_id", "user_id", "status", "admin_comment"]
    column_formatters_detail = {
        "answers": lambda m, c: f"{len(m.answers)} ответов" if m.answers else "Нет ответов"
    }

    def status_formatter(model: Any, _: Any) -> str:
        status_colors = {
            'new': '🔵 Новый',
            'processing': '🟡 В обработке',
            'ready': '🟢 Готов',
            'issued': '✅ Выдан',
            'rejected': '🔴 Отклонён',
            'canceled': '⚫ Отменён'
        }
        return status_colors.get(model.status, model.status)

    column_formatters = {"status": status_formatter}
    form_select_choices = {
        "status": [
            ('new', '🔵 Новый'),
            ('processing', '🟡 В обработке'),
            ('ready', '🟢 Готов'),
            ('issued', '✅ Выдан'),
            ('rejected', '🔴 Отклонён'),
            ('canceled', '⚫ Отменён')
        ]
    }


class SubmissionAnswerAdmin(ModelView, model=SubmissionAnswer):
    name = 'Ответ'
    name_plural = 'Ответы'
    icon = 'mdi-comment-text'

    column_list = ["id", "submission", "question", "answer_value", "created_at"]
    column_searchable_list = ["answer_value"]
    column_filters = ["submission", "question"]
    column_labels = {
        "id": "ID",
        "submission": "Заявка",
        "question": "Вопрос",
        "answer_value": "Ответ",
        "created_at": "Создано",
    }

    form_columns = ["submission_id", "question_id", "answer_value"]

