from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from src.database import get_db
from src.database.models import Button, Form, FormQuestion, Question
from src.schemas.forms import FormResponse, FormData, QuestionResponse

router = APIRouter(prefix="/api/buttons", tags=["forms"])


@router.get("/{button_id}/form", response_model=FormResponse)
async def get_form(button_id: int, db: AsyncSession = Depends(get_db)):
    """Получить форму с вопросами для конкретной кнопки"""

    # Проверяем, существует ли кнопка
    result = await db.execute(select(Button).filter(Button.id == button_id))
    button = result.scalar_one_or_none()

    if not button:
        raise HTTPException(status_code=404, detail="Кнопка не найдена")

    # Находим форму, связанную с кнопкой
    result = await db.execute(
        select(Form)
        .options(joinedload(Form.form_questions).joinedload(FormQuestion.question))
        .filter(Form.button_id == button_id)
    )
    form = result.unique().scalar_one_or_none()

    if not form:
        raise HTTPException(status_code=404, detail="Форма не найдена")

    # Получаем вопросы через связь form_questions
    questions = []
    for fq in sorted(form.form_questions, key=lambda x: x.sort_order):
        q = fq.question
        questions.append(QuestionResponse(
            id=q.id,
            question_text=q.question_text,
            field_type=q.field_type,
            placeholder=q.placeholder,
            options=q.options,
            is_required=fq.is_required,
            sort_order=fq.sort_order
        ))

    return FormResponse(
        success=True,
        data=FormData(
            form_id=form.id,
            title=form.title,
            description=form.description,
            questions=questions
        )
    )