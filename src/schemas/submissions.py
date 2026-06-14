from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class SubmissionAnswer(BaseModel):
    question_id: int
    value: str

class SubmissionCreate(BaseModel):
    button_id: int
    answers: List[SubmissionAnswer]

class SubmissionData(BaseModel):
    submission_id: int
    status: str
    created_at: str

class SubmissionResponse(BaseModel):
    success: bool
    data: SubmissionData
    message: str

class SubmissionListItem(BaseModel):
    id: int
    button_title: str
    status: str
    status_text: str
    created_at: datetime
    answers: Dict[str, str]

class SubmissionsListResponse(BaseModel):
    success: bool
    data: List[SubmissionListItem]



    