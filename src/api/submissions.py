from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from src.database import get_db
from src.database.models import Button, Submission, SubmissionAnswer, Question
from src.schemas.submissions import (
    SubmissionCreate, SubmissionResponse, SubmissionData,
    SubmissionListItem, SubmissionsListResponse
)

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


# Функция для получения user_id (потом замените на реальную авторизацию)
async def get_current_user_id(x_user_id: int = Header(default=1, alias="X-User-Id")) -> int:
    """Получить ID текущего пользователя из заголовка"""
    return x_user_id


@router.post("", response_model=SubmissionResponse)
async def create_submission(
        submission: SubmissionCreate,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    """Создать новую заявку"""

    # Проверяем, существует ли кнопка
    result = await db.execute(select(Button).filter(Button.id == submission.button_id))
    button = result.scalar_one_or_none()

    if not button:
        raise HTTPException(status_code=404, detail="Кнопка не найдена")

    # Проверяем, что все вопросы существуют
    for answer in submission.answers:
        result = await db.execute(select(Question).filter(Question.id == answer.question_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"Вопрос с id {answer.question_id} не найден")

    # Создаём заявку
    new_submission = Submission(
        button_id=submission.button_id,
        user_id=user_id,
        status="new"
    )
    db.add(new_submission)
    await db.flush()  # Чтобы получить id заявки

    # Сохраняем ответы
    for answer in submission.answers:
        submission_answer = SubmissionAnswer(
            submission_id=new_submission.id,
            question_id=answer.question_id,
            answer_value=answer.value
        )
        db.add(submission_answer)

    await db.commit()
    await db.refresh(new_submission)

    return SubmissionResponse(
        success=True,
        data=SubmissionData(
            submission_id=new_submission.id,
            status=new_submission.status,
            created_at=new_submission.created_at.isoformat()
        ),
        message="Заявка успешно отправлена!"
    )