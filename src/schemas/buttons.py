from pydantic import BaseModel
from typing import List

class Button(BaseModel):
    id: int
    title: str
    icon: str

    class Config:
        from_attributes = True

class ButtonResponse(BaseModel):
    success: bool
    data: List[Button]