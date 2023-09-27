import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.conf.messages import ERROR_ACCOUNT_EXISTS, ERROR_INVALID_CRED
from app.schemas.user_schemas import SignUpRequestModel
from app.services.auth import auth_service
from app.services.users import UsersService
from app.repository.dependencies import users_service

route = APIRouter(prefix="/auth", tags=["Auth"])


@route.get('/me')
async def read_current_user(current_user: dict = Depends(auth_service.get_current_user)):
    return current_user


@route.post("/SingUp", status_code=status.HTTP_201_CREATED)
async def SingUp(body: SignUpRequestModel, users_service: UsersService = Depends(users_service)):
    user_email = await users_service.find_user_by_email(body.user_email)
    if user_email is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ERROR_ACCOUNT_EXISTS)
    body.hashed_password = auth_service.get_password_hash(body.hashed_password)
    user = await users_service.add_user(body)
    logging.info(f"User {user} was created")
    return f"User id:{user}"


@route.post("/SingIn")
async def SingIn(body: OAuth2PasswordRequestForm = Depends(), users_service: UsersService = Depends(users_service)):
    user = await users_service.find_user_by_email(body.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_CRED)
    if not auth_service.verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_CRED)
    access_token = await auth_service.create_access_token(data={"sub": user.user_email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.user_email})
    await users_service.update_user_token(user.user_email, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
