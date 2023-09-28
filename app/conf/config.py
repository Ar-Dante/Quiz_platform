import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class FastAPIConfig(BaseSettings):
    host: str = os.getenv("MAIN_HOST")
    port: int = os.getenv("MAIN_PORT")
    reload: bool = os.getenv("RELOAD")
    sqlalchemy_database_url: str = os.getenv("SQLALCHEMY_DATABASE_URL")
    redis_url: str = os.getenv("REDIS_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    hash_algorithm: str = os.getenv("ALGORITHM")
    secret_auth_key: str = os.getenv("SECRET_AUTH_KEY")
    auth_hash_algorithm: str = os.getenv("AUTH_ALGORITHM")
    auth_audience: str = os.getenv("AUTH_AUDIENCE")


conf = FastAPIConfig()
