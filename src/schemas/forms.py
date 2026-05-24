from pydantic import BaseModel
from typing import Optional, List, Any

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    field_type: str
    placeholder: Optional[str] = None
    options: Optional[Any] = None
    is_required: bool
    sort_order: int

    class Config:
        from_attributes = True

class FormData(BaseModel):
    form_id: int
    title: str
    description: Optional[str] = None
    questions: List[QuestionResponse]

class FormResponse(BaseModel):
    success: bool
    data: FormData