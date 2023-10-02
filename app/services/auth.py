from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.conf.config import conf
from app.conf.messages import ERROR_CANT_VALIDATE_CRED, ERROR_INVALID_TOKEN, ERROR_INVALID_CRED
from app.repository.dependencies import users_service
from app.services.users import UsersService


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = conf.secret_key
    ALGORITHM = conf.hash_algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/SingIn")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def decode_auth0_token(self, token: str, users_service: UsersService = Depends(users_service)):
        try:
            payload = jwt.decode(
                token, conf.secret_auth_key, algorithms=[conf.auth_hash_algorithm],
                audience=conf.auth_audience
            )
            email = payload.get("https://example.com/email")
            if not email:
                raise HTTPException(status_code=400, detail=ERROR_INVALID_TOKEN)
            user = await users_service.find_user_by_email(email)
            if user is None:
                await users_service.create_user_from_auth0(email)
            return email
        except JWTError as e:
            raise HTTPException(status_code=401, detail=ERROR_INVALID_TOKEN)

    async def get_current_user(self, token: str = Depends(oauth2_scheme),
                               users_service: UsersService = Depends(users_service)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_CANT_VALIDATE_CRED,
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await users_service.find_user_by_email(email)
        if user is None:
            raise credentials_exception
        return user

    async def SingIn(self, body: OAuth2PasswordRequestForm = Depends(),
                     users_service: UsersService = Depends(users_service)):
        user = await users_service.find_user_by_email(body.username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_CRED)
        if not self.verify_password(body.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_CRED)
        access_token = await self.create_access_token(data={"sub": user.user_email})
        return {"access_token": access_token, "token_type": "bearer"}


auth_service = Auth()
