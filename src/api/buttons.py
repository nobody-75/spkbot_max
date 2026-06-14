from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.database.models import Button as ButtonModel
from src.schemas.buttons import ButtonResponse, Button

router = APIRouter(prefix="/api/buttons", tags=["buttons"])


@router.get("", response_model=ButtonResponse)
async def get_buttons(db: AsyncSession = Depends(get_db)):
    """Получить список всех активных кнопок"""

    result = await db.execute(
        select(ButtonModel)
        .filter(ButtonModel.is_active == True)
        .order_by(ButtonModel.sort_order)
    )
    buttons = result.scalars().all()

    return ButtonResponse(
        success=True,
        data=[Button(id=b.id, title=b.title, icon=b.icon) for b in buttons]
    )




