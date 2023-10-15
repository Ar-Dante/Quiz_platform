import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

'''logging.basicConfig(level=logging.DEBUG,
                    filename="meduzzen_intern.log",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )
'''


class FastAPIConfig(BaseSettings):
    host: str = os.getenv("MAIN_HOST")
    port: int = os.getenv("MAIN_PORT")
    reload: bool = os.getenv("RELOAD")
    sqlalchemy_database_url: str = os.getenv("SQLALCHEMY_DATABASE_URL")
    sqlalchemy_database_url_prod: str = os.getenv("SQLALCHEMY_DATABASE_URL_PROD")
    redis_port: int = os.getenv("REDIS_PORT")
    redis_host: str = os.getenv("REDIS_HOST")
    redis_url: str = os.getenv("REDIS_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    hash_algorithm: str = os.getenv("ALGORITHM")
    secret_auth_key: str = os.getenv("SECRET_AUTH_KEY")
    auth_hash_algorithm: str = os.getenv("AUTH_ALGORITHM")
    auth_audience: str = os.getenv("AUTH_AUDIENCE")


conf = FastAPIConfig()
