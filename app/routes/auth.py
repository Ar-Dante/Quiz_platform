import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from starlette import status

from app.conf.config import conf
from app.conf.messages import ERROR_ACCOUNT_EXISTS, ERROR_INVALID_CRED, ERROR_INVALID_TOKEN
from app.repository.dependencies import users_service
from app.schemas.user_schemas import SignUpRequestModel
from app.services.auth import auth_service
from app.services.users import UsersService

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
    return {"access_token": access_token, "token_type": "bearer"}


@route.post("/auth0-login/")
async def auth0_login(token: str, users_service: UsersService = Depends(users_service)):
    try:
        payload = jwt.decode(token, conf.secret_auth_key, algorithms=[conf.auth_hash_algorithm],
                             audience=conf.auth_audience)
        email = payload.get("https://example.com/email")
        print(email)
        if not email:
            raise HTTPException(status_code=400, detail=ERROR_INVALID_TOKEN)
        user = await users_service.find_user_by_email(email)
        if user is None:
            await users_service.create_user_from_auth0(email)
        access_token = await auth_service.create_access_token(data={"sub": email})
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=401, detail="ERROR_INVALID_TOKEN")
