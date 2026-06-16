from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.database.models import User
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])


async def get_current_user_id(x_user_id: int = Header(default=1, alias="X-User-Id")) -> int:
    return x_user_id


class UserProfileResponse(BaseModel):
    success: bool
    data: dict = None
    message: str = ""


@router.get("/me", response_model=UserProfileResponse)
async def get_user_profile(
        request: Request,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    """Получить профиль пользователя из БД по max_id"""
    logger.info(f"Запрос профиля для user_id: {user_id}")
    logger.info(f"Заголовки: {dict(request.headers)}")

    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    user = result.scalars().first()

    logger.info(f"Найден пользователь: {user}")

    if not user:
        # Проверим все max_id в БД для отладки
        all_users = await db.execute(select(User))
        users_list = all_users.scalars().all()
        logger.info(f"Все пользователи в БД: {[(u.id, u.first_name, u.group) for u in users_list]}")

        return UserProfileResponse(
            success=False,
            message=f"Пользователь с id={user_id} не найден. Всего пользователей: {len(users_list)}"
        )

    return UserProfileResponse(
        success=True,
        data={
            "first_name": user.first_name,
            "second_name": user.second_name,
            "group": user.group,
            "max_id": user.max_id
        }
    )
    user = result.scalars().first()

    logger.info(f"Найден пользователь: {user}")

    if not user:
        # Проверим все id в БД для отладки
        all_users = await db.execute(select(User))
        users_list = all_users.scalars().all()
        logger.info(f"Все пользователи в БД: {[(u.id, u.first_name, u.group) for u in users_list]}")

        return UserProfileResponse(
            success=False,
            message=f"Пользователь с max_id={user_id} не найден. Всего пользователей: {len(users_list)}"
        )

    return UserProfileResponse(
        success=True,
        data={
            "first_name": user.first_name,
            "second_name": user.second_name,
            "group": user.group,
            "max_id": user.max_id
        }
    )
    user = result.scalars().first()

    if not user:
        return UserProfileResponse(
            success=False,
            message="Пользователь не найден"
        )

    return UserProfileResponse(
        success=True,
        data={
            "first_name": user.first_name,
            "second_name": user.second_name,
            "group": user.group,
            "max_id": user.max_id
        }
    )
