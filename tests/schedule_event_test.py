from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.db.models import Company, CompanyMembers, Quiz
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.notifications import NotificationsService
from app.services.quizzes import QuizService
from app.services.results import ResultsService
from app.services.schedule_event import schedule_notification_sender


@pytest.mark.asyncio
async def test_schedule_notification_sender():
    with patch.object(CompanyService, 'get_all_companies', return_value=[Company(id=1)]), \
         patch.object(CompanyMembersService, 'get_all_members', return_value=[CompanyMembers(user_id=1)]), \
         patch.object(QuizService, 'get_quizzes', return_value=[Quiz(id=3, quiz_frequency=7)]), \
         patch.object(ResultsService, 'get_last_attempt_time_for_user_quiz', return_value=datetime.utcnow() - timedelta(days=8)), \
         patch.object(NotificationsService, 'add_notifications_about_time_to_quizz', return_value=None):
        await schedule_notification_sender()