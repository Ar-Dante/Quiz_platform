from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_ACCESS, ERROR_USER_NOT_INVITED, ERROR_USER_INVITED, ERROR_USER_REQUEST, \
    ERROR_USER_NOT_REQUESTED, ERROR_MEMBER_EXISTS, ERROR_MEMBER_OWNER
from app.repository.validation import validate_access
from app.utils.repository import AbstractRepository


class ActionService:
    def __init__(self, actions_repo: AbstractRepository):
        self.actions_repo: AbstractRepository = actions_repo()

    async def _valid_action_access(self, user_id: int, current_user: int, company_owner: int):
        if current_user != company_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        if user_id == current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_OWNER)

    async def send_invitation(self,
                              user_id: int,
                              company_id: int,
                              current_user: int,
                              company: dict,
                              member: dict) -> int:
        await self._valid_action_access(user_id, current_user.id, company.owner_id)
        if await self.get_actions(user_id, company_id, "invitation_sent"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_USER_INVITED)
        if member:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_EXISTS)

        return await self.actions_repo.add_one({
            "user_id": user_id,
            "company_id": company_id,
            "action": "invitation_sent"
        })

    async def send_request(self,
                           user_id: int,
                           company: dict,
                           current_user: int,
                           member: dict
                           ):
        await self._valid_action_access(user_id, current_user.id, company.owner_id)
        if await self.get_actions(user_id, company.id, "request_sent"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_USER_REQUEST)
        if member:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_EXISTS)
        return await self.actions_repo.add_one({
            "user_id": user_id,
            "company_id": company.id,
            "action": "request_sent"
        })

    async def cancel_request(self,
                             user_id: int,
                             company: dict,
                             current_user: int
                             ):
        await validate_access(current_user, user_id)
        if await self.get_actions(user_id, company.id, "request_sent") is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_REQUESTED)
        return await self.actions_repo.update_by_filter({"user_id": user_id,
                                                         "company_id": company.id,
                                                         "action": "request_sent"},
                                                        {"action": "request_canceled"})

    async def get_company_invitations(self, company_id: int, limit: int, offset: int, current_user: int):
        await validate_access(current_user, company_id)
        return await self.actions_repo.filter_by(limit, offset, {"action": "invitation_sent", "company_id": company_id})

    async def get_company_requests(self, company_id: int, limit: int, offset: int, current_user: int):
        await validate_access(current_user, company_id)
        return await self.actions_repo.filter_by(limit, offset, {"action": "request_sent", "company_id": company_id})

    async def get_user_invitations(self, user_id: int, limit: int, offset: int, current_user: int):
        await validate_access(current_user, user_id)
        return await self.actions_repo.filter_by(limit, offset, {"action": "invitation_sent", "user_id": user_id})

    async def get_user_requests(self, user_id: int, limit: int, offset: int, current_user: int):
        await validate_access(current_user, user_id)
        return await self.actions_repo.filter_by(limit, offset, {"action": "request_sent", "user_id": user_id})

    async def get_actions(self, user_id, company_id, action: str):
        return await self.actions_repo.find_by_filter({"user_id": user_id,
                                                       "company_id": company_id,
                                                       "action": action})

    async def cancel_invitation(self,
                                user_id: int,
                                company: dict,
                                current_user: int
                                ):
        await validate_access(current_user, company.owner_id)
        if await self.get_actions(user_id, company.id, "invitation_sent") is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_INVITED)
        return await self.actions_repo.update_by_filter({"user_id": user_id,
                                                         "company_id": company.id,
                                                         "action": "invitation_sent"},
                                                        {"action": "invitation_canceled"})

    async def accept_invitation(self,
                                user_id: int,
                                company_id: int,
                                current_user: int):
        await validate_access(current_user, user_id)
        if await self.get_actions(user_id, company_id, "invitation_sent") is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_INVITED)
        return await self.actions_repo.update_by_filter({"user_id": user_id,
                                                         "company_id": company_id,
                                                         "action": "invitation_sent"},
                                                        {"action": "invitation_accepted"})

    async def refuse_invitation(self,
                                user_id: int,
                                company_id: int,
                                current_user: int):
        await validate_access(current_user, user_id)
        if await self.get_actions(user_id, company_id, "invitation_sent") is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_INVITED)
        return await self.actions_repo.update_by_filter({"user_id": user_id,
                                                         "company_id": company_id,
                                                         "action": "invitation_sent"},
                                                        {"action": "invitation_refused"})

    async def accept_request(self,
                             user_id: int,
                             company: dict,
                             current_user: int):
        await validate_access(current_user, company.owner_id)
        if await self.get_actions(user_id, company.id, "request_sent") is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_REQUESTED)
        return await self.actions_repo.update_by_filter({"user_id": user_id,
                                                         "company_id": company.id,
                                                         "action": "request_sent"},
                                                        {"action": "request_accepted"})

    async def refuse_request(self,
                             user_id: int,
                             company: dict,
                             current_user: int):
        await validate_access(current_user, company.owner_id)
        if await self.get_actions(user_id, company.id, "request_sent") is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_REQUESTED)
        return await self.actions_repo.update_by_filter({"user_id": user_id,
                                                         "company_id": company.id,
                                                         "action": "request_sent"},
                                                        {"action": "request_refused"})

