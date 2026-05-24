from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.database.models import Submission, SubmissionAnswer, Question, Button
from src.schemas.submissions import SubmissionsListResponse, SubmissionListItem

router = APIRouter(prefix="/api/submissions", tags=["my"])


async def get_current_user_id(x_user_id: int = Header(default=1, alias="X-User-Id")) -> int:
    return x_user_id


@router.get("/my", response_model=SubmissionsListResponse)
async def get_my_submissions(
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    """Получить все заявки текущего пользователя"""

    # Получаем заявки пользователя
    result = await db.execute(
        select(Submission, Button)
        .join(Button, Submission.button_id == Button.id)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.created_at.desc())
    )
    submissions = result.all()

    result_list = []

    for submission, button in submissions:
        # Получаем ответы для этой заявки
        answers_result = await db.execute(
            select(Question.question_text, SubmissionAnswer.answer_value)
            .join(SubmissionAnswer, Question.id == SubmissionAnswer.question_id)
            .filter(SubmissionAnswer.submission_id == submission.id)
        )
        answers = {text: value for text, value in answers_result.all()}

        # Статус на русском
        status_text_map = {
            "new": "Новая",
            "processing": "В обработке",
            "ready": "Готова",
            "issued": "Выдана",
            "rejected": "Отклонена",
            "canceled": "Отменена"
        }

        result_list.append(SubmissionListItem(
            id=submission.id,
            button_title=button.title,
            status=submission.status,
            status_text=status_text_map.get(submission.status, submission.status),
            created_at=submission.created_at,
            answers=answers
        ))

    return SubmissionsListResponse(
        success=True,
        data=result_list
    )