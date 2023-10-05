from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_MEMBER_NOT_FOUND, ERROR_ACCESS, ERROR_MEMBER_ADMIN, ERROR_MEMBER_OWNER_ADMIN, \
    ERROR_MEMBER_NOT_ADMIN
from app.utils.repository import AbstractRepository


class CompanyMembersService:
    def __init__(self, comp_memb_repo: AbstractRepository):
        self.comp_memb_repo: AbstractRepository = comp_memb_repo()

    async def add_member(self,
                         user_id: int,
                         company_id: int
                         ):
        data = {
            "user_id": user_id,
            "company_id": company_id
        }
        return await self.comp_memb_repo.add_one(data)

    async def exit_from_company(self,
                                user_id: int,
                                company_id: int,
                                current_user: int
                                ):
        filter_by = {
            "user_id": user_id,
            "company_id": company_id
        }
        if current_user != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        member = await self.get_member(user_id, company_id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)
        return await self.comp_memb_repo.delete_by_filter(filter_by)

    async def delete_from_company(self,
                                  user_id: int,
                                  company: dict,
                                  current_user: int,
                                  ):
        filter_by = {
            "user_id": user_id,
            "company_id": company.id
        }
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        member = await self.get_member(user_id, company.id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)
        return await self.comp_memb_repo.delete_by_filter(filter_by)

    async def get_member(self, user_id: int, company_id: int):
        filter_by = {
            "user_id": user_id,
            "company_id": company_id
        }
        return await self.comp_memb_repo.find_by_filter(filter_by)

    async def get_company_members(self, company: dict, limit: int, offset: int):
        members = await self.comp_memb_repo.find_all(limit, offset)
        return [mem for mem in members if
                company.id == mem.company_id]

    async def add_admin(self,
                        user_id: int,
                        company: dict,
                        current_user: int
                        ):
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        if user_id == current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_OWNER_ADMIN)
        member = await self.get_member(user_id, company.id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)
        if member.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_ADMIN)
        filter_by = {
            "user_id": user_id,
            "company_id": company.id
        }
        data = {"is_admin": True}
        return await self.comp_memb_repo.update_by_filter(filter_by, data)

    async def remove_admin(self,
                           user_id: int,
                           company: dict,
                           current_user: int
                           ):
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        if user_id == current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_OWNER_ADMIN)
        member = await self.get_member(user_id, company.id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)
        if not member.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_NOT_ADMIN)
        filter_by = {
            "user_id": user_id,
            "company_id": company.id
        }
        data = {"is_admin": False}
        return await self.comp_memb_repo.update_by_filter(filter_by, data)

    async def get_company_admins(self, company: dict, limit: int, offset: int):
        members = await self.comp_memb_repo.find_all(limit, offset)
        return [mem for mem in members if
                company.id == mem.company_id and mem.is_admin]
