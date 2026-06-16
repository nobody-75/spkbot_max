from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime, UniqueConstraint
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
    login = Column(String(100), unique=True, index=True, nullable=False)
    group = Column(String(10), nullable=True)
    max_id = Column(String(100), unique=True, index=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    password = Column(String(100), nullable=False)

    role_rel = relationship("Role", lazy="joined")

    # Связь с заявками
    submissions = relationship("Submission", back_populates="user", lazy="select")

    def __str__(self):
        return f"{self.first_name} {self.second_name}"

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
    button_id = Column(Integer, ForeignKey("buttons.id"), nullable=False)
    title = Column(String(255), nullable=False)  # заголовок формы
    description = Column(Text)  # описание формы
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    button = relationship("Button", back_populates="form")
    form_questions = relationship("FormQuestion", back_populates="form", cascade="all, delete-orphan", lazy="joined")

    def __str__(self):
        return self.title

    @property
    def questions_display(self) -> str:
        """Возвращает список вопросов для отображения в админке"""
        if not self.form_questions:
            return "Нет вопросов"

        lines = []
        for fq in sorted(self.form_questions, key=lambda x: x.sort_order):
            q = fq.question
            required = " *" if fq.is_required else ""
            lines.append(f"<b>{fq.sort_order + 1}.</b> {q.question_text if q else 'Вопрос #' + str(fq.question_id)}{required}")

        return "<br>".join(lines)


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
    form = relationship("Form", back_populates="form_questions", lazy="joined")
    question = relationship("Question", back_populates="form_questions", lazy="joined")

    # Уникальность: один вопрос не может быть дважды в одной форме
    __table_args__ = (UniqueConstraint('form_id', 'question_id', name='uq_form_question'),)

    def __str__(self):
        return f"FormQuestion #{self.id}"


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
    user = relationship("User", back_populates="submissions", lazy="joined")
    answers = relationship("SubmissionAnswer", back_populates="submission", cascade="all, delete-orphan", lazy="joined")

    def __str__(self):
        return f"Заявка #{self.id} - {self.status}"

    @property
    def answers_display(self) -> str:
        """Возвращает список ответов для отображения в админке"""
        if not self.answers:
            return "Нет ответов"

        lines = []
        for answer in sorted(self.answers, key=lambda a: a.question_id):
            q_text = answer.question.question_text if answer.question else f"Вопрос #{answer.question_id}"
            lines.append(f"<b>{q_text}:</b><br>{answer.answer_value}")

        return "<br><br>".join(lines)


class SubmissionAnswer(Base):
    """Ответы пользователя на вопросы"""
    __tablename__ = "submission_answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    submission = relationship("Submission", back_populates="answers", lazy="joined")
    question = relationship("Question", back_populates="submission_answers", lazy="joined")

    def __str__(self):
        return f"Answer #{self.id}"
