from sqlalchemy import Column, Integer, String, event, ForeignKey, Boolean, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from . import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # "user", "admin", etc.

    def __str__(self):
        return self.name


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), index=True, nullable=False)
    second_name = Column(String(100), index=True, nullable=False)
    login = Column(String(100), index=True, nullable=False)
    max_id = Column(String(100), unique=True, index=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    password = Column(String(100), nullable=False)

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined"
    )

    role_rel = relationship("Role", lazy="joined")

    # Связь с заявками (добавлено)
    submissions = relationship("Submission", back_populates="user", lazy="dynamic")

    def __str__(self):
        return f"{self.first_name} {self.second_name}"


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("User", back_populates="profile", lazy="joined")

    @property
    def user_display(self) -> str:
        """Возвращает ФИО пользователя"""
        if self.user:
            return f"{self.user.first_name} {self.user.second_name}".strip()
        return "Не указан"

    def __str__(self):
        return self.user_display


# =====================================================
# НОВЫЕ МОДЕЛИ ДЛЯ ФОРМ И ЗАЯВОК
# =====================================================

class Button(Base):
    """Кнопки, которые видит пользователь"""
    __tablename__ = "buttons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # название кнопки
    icon = Column(String(50), default="📄")  # иконка/emoji
    is_active = Column(Boolean, default=True)  # активна ли кнопка
    sort_order = Column(Integer, default=0)  # порядок отображения
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    form = relationship("Form", back_populates="button", uselist=False, cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="button")

    def __str__(self):
        return self.title


class Form(Base):
    """Формы (связь 1:1 с кнопкой)"""
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    button_id = Column(Integer, ForeignKey("buttons.id"), unique=True, nullable=False)
    title = Column(String(255), nullable=False)  # заголовок формы
    description = Column(Text)  # описание формы
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    button = relationship("Button", back_populates="form")
    form_questions = relationship("FormQuestion", back_populates="form", cascade="all, delete-orphan")

    def __str__(self):
        return self.title


class Question(Base):
    """Справочник вопросов (можно переиспользовать в разных формах)"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)  # текст вопроса
    field_type = Column(String(50), nullable=False)  # text, phone, email, select, textarea, date, number
    placeholder = Column(String(255))  # подсказка внутри поля
    options = Column(JSON)  # варианты для select/radio
    validation_regex = Column(String(255))  # регулярное выражение для валидации
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    form_questions = relationship("FormQuestion", back_populates="question")
    submission_answers = relationship("SubmissionAnswer", back_populates="question")

    def __str__(self):
        return self.question_text


class FormQuestion(Base):
    """Связующая таблица: формы ←→ вопросы (многие ко многим)"""
    __tablename__ = "form_questions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    sort_order = Column(Integer, default=0)  # порядок вопроса в форме
    is_required = Column(Boolean, default=False)  # обязательное поле
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    form = relationship("Form", back_populates="form_questions")
    question = relationship("Question", back_populates="form_questions")

    # Уникальность: один вопрос не может быть дважды в одной форме
    __table_args__ = (UniqueConstraint('form_id', 'question_id', name='uq_form_question'),)

    def __str__(self):
        return f"{self.form.title} - {self.question.question_text}"


class Submission(Base):
    """Заявки пользователей"""
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    button_id = Column(Integer, ForeignKey("buttons.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="new")  # new, processing, ready, issued, rejected, canceled
    admin_comment = Column(Text)  # комментарий администратора
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    button = relationship("Button", back_populates="submissions")
    user = relationship("User", back_populates="submissions")
    answers = relationship("SubmissionAnswer", back_populates="submission", cascade="all, delete-orphan")

    def __str__(self):
        return f"Заявка #{self.id} - {self.status}"


class SubmissionAnswer(Base):
    """Ответы пользователя на вопросы"""
    __tablename__ = "submission_answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    submission = relationship("Submission", back_populates="answers")
    question = relationship("Question", back_populates="submission_answers")

    def __str__(self):
        return f"{self.question.question_text}: {self.answer_value}"


# =====================================================
# ТРИГГЕРЫ
# =====================================================

@event.listens_for(User, 'after_insert')
def create_profile(mapper, connection, target):
    """Автоматически создает профиль при создании пользователя"""
    connection.execute(
        Profile.__table__.insert().values(user_id=target.id)
    )