from fastapi import HTTPException
from starlette import status

from app.conf.messages import ERROR_MEMBER_NOT_FOUND, ERROR_USER_NOT_FOUND
from app.utils.repository import AbstractRepository


class ResultsService:
    def __init__(self, results_repo: AbstractRepository):
        self.results_repo: AbstractRepository = results_repo()

    async def add_results(self,
                          quiz_id: int,
                          company_id: int,
                          current_user: int,
                          correct_count: int,
                          total_count: int):
        await self.results_repo.add_one({
            "result_user_id": current_user,
            "result_company_id": company_id,
            "result_quiz_id": quiz_id,
            "result_right_count": correct_count,
            "result_total_count": total_count,
        })

    async def get_user_average_rating_in_company(self,
                                                 user_id: int,
                                                 company_id: int,
                                                 member: dict,
                                                 company: dict,
                                                 current_user: int) -> int:
        if member is None and company.owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)

        user_results = await self.results_repo.filter(
            {
                "result_user_id": user_id,
                "result_company_id": company_id,
            }
        )
        if not user_results:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        total_right_count = sum(result.result_right_count for result in user_results)
        total_total_count = sum(result.result_total_count for result in user_results)
        return total_right_count / total_total_count if total_total_count > 0 else 0.0

    async def get_system_average_rating(self,
                                        user_id: int) -> int:
        user_results = await self.results_repo.filter(
            {
                "result_user_id": user_id,
            }
        )
        if not user_results:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        total_right_count = sum(result.result_right_count for result in user_results)
        total_total_count = sum(result.result_total_count for result in user_results)
        return total_right_count / total_total_count if total_total_count > 0 else 0.0
