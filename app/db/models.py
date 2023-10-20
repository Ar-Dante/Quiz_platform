from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True, index=True, nullable=False)
    user_firstname = Column(String)
    user_lastname = Column(String)
    user_status = Column(String, default="active", nullable=False)
    user_city = Column(String)
    user_phone = Column(String)
    user_links = Column(String)
    user_avatar = Column(String)
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    companies = relationship("Company", back_populates="owner")
    notifications = relationship("Notification", back_populates="user")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    company_title = Column(String)
    company_description = Column(String)
    company_city = Column(String)
    company_phone = Column(String)
    company_links = Column(String)
    company_avatar = Column(String)
    is_visible = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="companies")


class UsersCompaniesActions(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    action = Column(String)


class CompanyMembers(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    is_admin = Column(Boolean, default=False)


class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_name = Column(String(255), nullable=False)
    quiz_title = Column(String(255))
    quiz_description = Column(String)
    quiz_frequency = Column(Integer, nullable=False)
    quiz_company_id = Column(Integer, ForeignKey("companies.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    questions = relationship("Question", back_populates="quiz")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(String, nullable=False)
    question_answers = Column(ARRAY(String), nullable=False)
    question_correct_answer = Column(String, nullable=False)
    question_quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    question_company_id = Column(Integer, ForeignKey("companies.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    quiz = relationship("Quiz", back_populates="questions")


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    result_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    result_quiz_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    result_right_count = Column(Integer)
    result_total_count = Column(Integer)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_read = Column(Boolean, default=False)

    user = relationship("User", back_populates="notifications")
