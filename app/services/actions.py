from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_ACCESS, ERROR_USER_NOT_INVITED, ERROR_USER_INVITED, ERROR_USER_REQUEST, \
    ERROR_USER_NOT_REQUESTED, ERROR_MEMBER_EXISTS, ERROR_MEMBER_OWNER
from app.utils.repository import AbstractRepository


class ActionService:
    def __init__(self, actions_repo: AbstractRepository):
        self.actions_repo: AbstractRepository = actions_repo()

    async def send_invitation(self,
                              user_id: int,
                              company_id: int,
                              current_user: int,
                              company: dict,
                              member: dict) -> int:
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        if user_id == current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_OWNER)
        invitation = await self.get_actions(user_id, company_id, "invitation_sent")
        if invitation:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_USER_INVITED)
        if member:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_EXISTS)
        data = {
            "user_id": user_id,
            "company_id": company_id,
            "action": "invitation_sent"
        }
        return await self.actions_repo.add_one(data)

    async def send_request(self,
                           user_id: int,
                           company: dict,
                           current_user: int,
                           member: dict
                           ):
        if current_user != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        if user_id == company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_OWNER)
        request = await self.get_actions(user_id, company.id, "request_sent")
        if request:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_USER_REQUEST)
        if member:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_EXISTS)
        data = {
            "user_id": user_id,
            "company_id": company.id,
            "action": "request_sent"
        }
        return await self.actions_repo.add_one(data)

    async def cancel_request(self,
                             user_id: int,
                             company: dict,
                             current_user: int
                             ):
        if current_user != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitation = await self.get_actions(user_id, company.id, "request_sent")
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_REQUESTED)
        filter_by = {"user_id": user_id, "company_id": company.id, "action": "request_sent"}
        data = {"action": "request_canceled"}
        return await self.actions_repo.update_by_filter(filter_by, data)

    async def get_company_invitations(self, company: dict, limit: int, offset: int, current_user: int):
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitations = await self.actions_repo.find_all(limit, offset)
        return [invite for invite in invitations if
                invite.action == "invitation_sent" and invite.company_id == company.id]

    async def get_company_requests(self, company: dict, limit: int, offset: int, current_user: int):
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitations = await self.actions_repo.find_all(limit, offset)
        return [invite for invite in invitations if
                invite.action == "request_sent" and invite.company_id == company.id]

    async def get_user_invitations(self, user_id: int, limit: int, offset: int, current_user: int):
        if current_user != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitations = await self.actions_repo.find_all(limit, offset)
        return [invite for invite in invitations if
                invite.action == "invitation_sent" and invite.user_id == user_id]

    async def get_user_requests(self, user_id: int, limit: int, offset: int, current_user: int):
        if current_user != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitations = await self.actions_repo.find_all(limit, offset)
        return [invite for invite in invitations if
                invite.action == "request_sent" and invite.user_id == user_id]

    async def get_actions(self, user_id, company_id, action: str):
        filter_by = {"user_id": user_id, "company_id": company_id, "action": action}
        return await self.actions_repo.find_by_filter(filter_by)

    async def cancel_invitation(self,
                                user_id: int,
                                company: dict,
                                current_user: int
                                ):
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitation = await self.get_actions(user_id, company.id, "invitation_sent")
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_INVITED)
        filter_by = {"user_id": user_id, "company_id": company.id, "action": "invitation_sent"}
        data = {"action": "invitation_canceled"}
        return await self.actions_repo.update_by_filter(filter_by, data)

    async def accept_invitation(self,
                                user_id: int,
                                company_id: int,
                                current_user: int):
        if current_user != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitation = await self.get_actions(user_id, company_id, "invitation_sent")
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_INVITED)
        filter_by = {"user_id": user_id, "company_id": company_id, "action": "invitation_sent"}
        data = {"action": "invitation_accepted"}
        return await self.actions_repo.update_by_filter(filter_by, data)

    async def refuse_invitation(self,
                                user_id: int,
                                company_id: int,
                                current_user: int):
        if current_user != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitation = await self.get_actions(user_id, company_id, "invitation_sent")
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_INVITED)
        filter_by = {"user_id": user_id, "company_id": company_id, "action": "invitation_sent"}
        data = {"action": "invitation_refused"}
        return await self.actions_repo.update_by_filter(filter_by, data)

    async def accept_request(self,
                             user_id: int,
                             company: dict,
                             current_user: int):
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitation = await self.get_actions(user_id, company.id, "request_sent")
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_REQUESTED)
        filter_by = {"user_id": user_id, "company_id": company.id, "action": "request_sent"}
        data = {"action": "request_accepted"}
        return await self.actions_repo.update_by_filter(filter_by, data)

    async def refuse_request(self,
                             user_id: int,
                             company: dict,
                             current_user: int):
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        invitation = await self.get_actions(user_id, company.id, "request_sent")
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_REQUESTED)
        filter_by = {"user_id": user_id, "company_id": company.id, "action": "request_sent"}
        data = {"action": "request_refused"}
        return await self.actions_repo.update_by_filter(filter_by, data)
