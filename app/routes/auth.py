from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.conf.messages import ERROR_INVALID_CRED
from app.repository.dependencies import users_service
from app.schemas.user_schemas import UserBase
from app.services.auth import auth_service
from app.services.users import UsersService

route = APIRouter(prefix="/auth", tags=["Auth"])


@route.get('/me', response_model=UserBase)
async def read_current_user(current_user: dict = Depends(auth_service.get_current_user)):
    return current_user


@route.post("/SingIn")
async def SingIn(body: OAuth2PasswordRequestForm = Depends(), users_service: UsersService = Depends(users_service)):
    user = await users_service.find_user_by_email(body.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_CRED)
    if not auth_service.verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_CRED)
    access_token = await auth_service.create_access_token(data={"sub": user.user_email})
    return {"access_token": access_token, "token_type": "bearer"}


@route.post("/auth0-login/")
async def auth0_login(token: str, users_service: UsersService = Depends(users_service)):
    email = auth_service.decode_auth0_token(token)
    user = await users_service.find_user_by_email(email)
    if user is None:
        await users_service.create_user_from_auth0(email)
    access_token = await auth_service.create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}
