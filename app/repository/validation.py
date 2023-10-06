from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_ACCESS


async def validate_access(current_user, access_id):
    if current_user != access_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
