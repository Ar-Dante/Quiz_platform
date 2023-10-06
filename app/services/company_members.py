from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_MEMBER_NOT_FOUND, ERROR_ACCESS, ERROR_MEMBER_ADMIN, ERROR_MEMBER_OWNER_ADMIN, \
    ERROR_MEMBER_NOT_ADMIN
from app.repository.validation import validate_access
from app.utils.repository import AbstractRepository


class CompanyMembersService:
    def __init__(self, comp_memb_repo: AbstractRepository):
        self.comp_memb_repo: AbstractRepository = comp_memb_repo()

    async def add_member(self,
                         user_id: int,
                         company_id: int
                         ):
        return await self.comp_memb_repo.add_one({
            "user_id": user_id,
            "company_id": company_id
        })

    async def exit_from_company(self,
                                user_id: int,
                                company_id: int,
                                current_user: int
                                ):
        await validate_access(current_user, user_id)
        if await self.get_member(user_id, company_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)
        return await self.comp_memb_repo.delete_by_filter({
            "user_id": user_id,
            "company_id": company_id
        })

    async def delete_from_company(self,
                                  user_id: int,
                                  company: dict,
                                  current_user: int,
                                  ):
        await validate_access(current_user, company.owner_id)
        if await self.get_member(user_id, company.id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)
        return await self.comp_memb_repo.delete_by_filter({
            "user_id": user_id,
            "company_id": company.id
        })

    async def get_member(self, user_id: int, company_id: int):
        return await self.comp_memb_repo.find_by_filter({
            "user_id": user_id,
            "company_id": company_id
        })

    async def get_company_members(self, company: dict, limit: int, offset: int):
        members = await self.comp_memb_repo.find_all(limit, offset)
        return [mem for mem in members if
                company.id == mem.company_id]

    async def add_admin(self,
                        user_id: int,
                        company: dict,
                        current_user: int
                        ):
        await validate_access(current_user, company.owner_id)
        if user_id == current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_OWNER_ADMIN)
        member = await self.get_member(user_id, company.id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)
        if member.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_ADMIN)
        return await self.comp_memb_repo.update_by_filter({
            "user_id": user_id,
            "company_id": company.id
        }, {"is_admin": True})

    async def remove_admin(self,
                           user_id: int,
                           company: dict,
                           current_user: int
                           ):
        await validate_access(current_user, company.owner_id)
        if user_id == current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_OWNER_ADMIN)
        member = await self.get_member(user_id, company.id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)
        if not member.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_NOT_ADMIN)
        return await self.comp_memb_repo.update_by_filter({
            "user_id": user_id,
            "company_id": company.id
        }, {"is_admin": False})

    async def get_company_admins(self, company: dict, limit: int, offset: int):
        members = await self.comp_memb_repo.find_all(limit, offset)
        return [mem for mem in members if
                company.id == mem.company_id and mem.is_admin]
