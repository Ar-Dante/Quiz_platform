from typing import List

from pydantic import BaseModel


class QuestionDetail(BaseModel):
    question_text: str
    question_answers: List[str]
    question_correct_answer: int
    question_quiz_id: int


class QuestionCreateModel(BaseModel):
    question_text: str
    question_answers: List[str]
    question_correct_answer: int


class QuestionUpdateModel(BaseModel):
    question_text: str
    question_answers: List[str]
    question_correct_answer: int
