from typing import Optional, Any

from fastapi import Request
from markupsafe import Markup
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from wtforms import SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

from src.database import AsyncSessionLocal, User
from src.database.models import Button, Form, Question, FormQuestion, Submission, SubmissionAnswer


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

    async def _get_admin_user(self, login: str, password: str) -> Optional[User]:
        """Получение пользователя с ролью администратора"""
        async with AsyncSessionLocal() as db:
            from src.database.models import Role
            stmt = (
                select(User)
                .options(joinedload(User.role_rel))
                .join(User.role_rel)
                .where(User.login == login)
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
            "login": user.login,
            "role": user.role_rel.name
        })


# =====================================================
# ПОЛЬЗОВАТЕЛИ
# =====================================================

class UserAdmin(ModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'
    icon = 'mdi-account'

    column_list = ["id", "login", "first_name", "second_name", "max_id", "role_rel"]
    column_searchable_list = ["first_name", "second_name", "login", "max_id"]

    column_labels = {
        "id": "ID",
        "login": "Логин",
        "first_name": "Имя",
        "second_name": "Фамилия",
        "max_id": "Max ID",
        "role_rel": "Роль",
    }

    # Убрали password из формы
    form_columns = ["first_name", "second_name", "login", "max_id", "role_id"]

    form_args = {
        "first_name": {"label": "Имя"},
        "second_name": {"label": "Фамилия"},
        "login": {"label": "Логин"},
        "max_id": {"label": "Max ID"},
        "role_id": {"label": "Роль"},
    }


# =====================================================
# КНОПКИ И ФОРМЫ
# =====================================================

class ButtonAdmin(ModelView, model=Button):
    name = 'Кнопка'
    name_plural = 'Кнопки'
    icon = 'mdi-button-cursor'

    column_list = ["id", "title", "icon", "is_active", "sort_order", "created_at"]
    column_searchable_list = ["title"]

    column_labels = {
        "id": "ID",
        "title": "Название",
        "icon": "Иконка",
        "is_active": "Активна",
        "sort_order": "Порядок",
        "created_at": "Создано",
    }

    form_columns = ["title", "icon", "is_active", "sort_order"]

    form_args = {
        "title": {"label": "Название"},
        "icon": {"label": "Иконка"},
        "sort_order": {"label": "Порядок сортировки"},
    }

    form_widget_args = {
        'icon': {
            'placeholder': '📄 (emoji или иконка)'
        }
    }


class FormAdmin(ModelView, model=Form):
    name = 'Форма'
    name_plural = 'Формы'
    icon = 'mdi-form-select'

    column_list = ["id", "button", "title", "description", "created_at"]
    column_searchable_list = ["title", "description"]

    column_labels = {
        "id": "ID",
        "button": "Кнопка",
        "title": "Заголовок",
        "description": "Описание",
        "created_at": "Создано",
    }

    form_columns = ["button", "title", "description"]

    form_args = {
        "button": {"label": "Кнопка"},
        "title": {"label": "Заголовок"},
        "description": {"label": "Описание"},
    }

    form_required_columns = ["button", "title"]

    # Детали формы с вопросами
    column_details_list = ["id", "button", "title", "description", "questions_display", "created_at"]

    column_labels = {
        "id": "ID",
        "button": "Кнопка",
        "title": "Заголовок",
        "description": "Описание",
        "questions_display": "Вопросы",
        "created_at": "Создано",
    }

    form_columns = ["button", "title", "description"]

    form_args = {
        "button": {"label": "Кнопка"},
        "title": {"label": "Заголовок"},
        "description": {"label": "Описание"},
    }

    form_required_columns = ["button", "title"]

    column_formatters_detail = {
        "questions_display": lambda m, a: FormAdmin._format_questions(m),
    }

    async def get_details_query(self) -> Any:
        """Запрос для деталей с загрузкой вопросов"""
        from sqlalchemy.orm import joinedload
        query = select(self.model).options(
            joinedload(Form.form_questions).joinedload(FormQuestion.question)
        )
        return query

    async def scaffold_form(self, rules: list | None = None) -> type:
        """Создание формы с кастомными полями"""
        form_class = await super().scaffold_form(rules)

        # Получаем активные вопросы для выбора
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Question).where(Question.is_active == True).order_by(Question.question_text)
            )
            questions = result.scalars().all()

        choices = [(str(q.id), q.question_text) for q in questions]

        form_class.question_ids = SelectMultipleField(
            label="Вопросы формы",
            choices=choices,
            coerce=str,
            widget=ListWidget(prefix_label=False),
            option_widget=CheckboxInput()
        )

        return form_class

    async def edit_form(self, request: Request) -> Any:
        """Получение формы редактирования"""
        form = await super().edit_form(request)

        # Загружаем текущие вопросы формы
        pk = request.path_params.get("pk")
        if pk:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(FormQuestion.question_id).where(FormQuestion.form_id == int(pk))
                    .order_by(FormQuestion.sort_order)
                )
                question_ids = [str(row[0]) for row in result.fetchall()]
                form.question_ids.data = question_ids

        return form

    async def on_model_change(self, data: dict, model: Form, is_created: bool, request: Request) -> None:
        """Обработка создания/обновления формы"""
        # Получаем список ID вопросов
        question_ids = data.pop('question_ids', [])

        # Сохраняем форму через базовый класс
        await super().on_model_change(data, model, is_created, request)

        # model.id должен быть установлен после super()
        if not model.id:
            return

        # Обрабатываем вопросы
        async with AsyncSessionLocal() as db:
            # Удаляем старые связи
            await db.execute(
                FormQuestion.__table__.delete().where(
                    FormQuestion.form_id == model.id
                )
            )

            # Создаём новые связи
            if question_ids:
                for idx, q_id in enumerate(question_ids):
                    if q_id:
                        await db.execute(
                            FormQuestion.__table__.insert().values(
                                form_id=model.id,
                                question_id=int(q_id),
                                sort_order=idx,
                                is_required=True
                            )
                        )
            await db.commit()

    @staticmethod
    def _format_questions(form: Form) -> Markup:
        """Форматирование вопросов для отображения в деталях"""
        if not form.form_questions:
            return Markup("Нет вопросов")

        lines = []
        for fq in sorted(form.form_questions, key=lambda x: x.sort_order):
            q = fq.question
            required = " <span style='color:red'>*</span>" if fq.is_required else ""
            lines.append(f"<b>{fq.sort_order + 1}.</b> {q.question_text if q else 'Вопрос #' + str(fq.question_id)}{required}")

        return Markup("<br>".join(lines))


class QuestionAdmin(ModelView, model=Question):
    name = 'Вопрос'
    name_plural = 'Вопросы'
    icon = 'mdi-help-circle'

    column_list = ["id", "question_text", "field_type", "is_active", "created_at"]
    column_searchable_list = ["question_text"]

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

    form_args = {
        "question_text": {"label": "Текст вопроса"},
        "field_type": {"label": "Тип поля"},
    }

    form_widget_args = {
        'field_type': {
            'choices': [
                ('text', '📝 Текст (одна строка)'),
                ('textarea', '📄 Текст (многострочное)'),
                ('email', '📧 Email'),
                ('phone', '📞 Телефон'),
                ('number', '🔢 Число'),
                ('select', '📋 Выпадающий список'),
                ('date', '📅 Дата'),
            ]
        },
        'options': {
            'placeholder': '{"options": ["Вариант 1", "Вариант 2"]}',
            'help_text': 'JSON формат: {"options": ["значение1", "значение2"]}'
        },
        'validation_regex': {
            'placeholder': '^[a-zA-Z0-9]+$',
            'help_text': 'Регулярное выражение для проверки ввода'
        }
    }


# =====================================================
# ЗАЯВКИ
# =====================================================

class SubmissionAdmin(ModelView, model=Submission):
    name = 'Заявка'
    name_plural = 'Заявки'
    icon = 'mdi-file-document'

    column_list = ["id", "button", "user", "status", "created_at", "updated_at"]
    column_searchable_list = ["status"]

    column_labels = {
        "id": "ID",
        "button": "Кнопка",
        "user": "Пользователь",
        "status": "Статус",
        "admin_comment": "Комментарий администратора",
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "answers_display": "Ответы",
    }

    # Детали заявки с ответами
    column_details_list = ["id", "button", "user", "status", "answers_display", "admin_comment", "created_at", "updated_at"]

    column_formatters_detail = {
        "answers_display": lambda m, a: SubmissionAdmin._format_answers(m),
    }

    form_columns = ["button_id", "user_id", "status", "admin_comment"]

    form_args = {
        "button_id": {"label": "Кнопка"},
        "user_id": {"label": "Пользователь"},
        "status": {"label": "Статус"},
    }

    # Загрузка ответов в деталях
    async def get_details_query(self) -> Any:
        """Запрос для деталей с загрузкой ответов"""
        query = select(self.model).options(
            joinedload(Submission.answers).joinedload(SubmissionAnswer.question)
        )
        return query

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

    @staticmethod
    def _format_status(model: Any) -> str:
        status_colors = {
            'new': '🔵 Новый',
            'processing': '🟡 В обработке',
            'ready': '🟢 Готов',
            'issued': '✅ Выдан',
            'rejected': '🔴 Отклонён',
            'canceled': '⚫ Отменён'
        }
        return status_colors.get(model.status, model.status)

    @staticmethod
    def _format_answers(submission: Submission) -> Markup:
        """Форматирование ответов для отображения в деталях"""
        if not submission.answers:
            return Markup("Нет ответов")

        lines = []
        for answer in sorted(submission.answers, key=lambda a: a.question_id):
            q_text = answer.question.question_text if answer.question else f"Вопрос #{answer.question_id}"
            lines.append(f"<b>{q_text}:</b><br>{answer.answer_value}")

        return Markup("<br><br>".join(lines))
