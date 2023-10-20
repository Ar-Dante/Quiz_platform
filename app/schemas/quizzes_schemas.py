from typing import Optional

from pydantic import BaseModel


class QuizCreateModel(BaseModel):
    quiz_name: str
    quiz_description: Optional[str] = None
    quiz_title: Optional[str] = None
    quiz_frequency: int


class QuizDetail(BaseModel):
    quiz_name: str
    quiz_description: Optional[str] = None
    quiz_title: Optional[str] = None
    quiz_frequency: int


class QuizUpdateModel(BaseModel):
    quiz_name: str
    quiz_description: Optional[str] = None
    quiz_title: Optional[str] = None
    quiz_frequency: int
