from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

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
    return await auth_service.SingIn(body=body, users_service=users_service)


@route.post("/auth0-login/")
async def auth0_login(token: str):
    email = auth_service.decode_auth0_token(token)
    access_token = await auth_service.create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}
