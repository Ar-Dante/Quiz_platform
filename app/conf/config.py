import logging
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

logging.basicConfig(level=logging.ERROR,
                    filename="meduzzen_intern.log",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )


class FastAPIConfig(BaseSettings):
    host: str = os.getenv("MAIN_HOST")
    port: int = os.getenv("MAIN_PORT")
    reload: bool = os.getenv("RELOAD")
    sqlalchemy_database_url: str = os.getenv("SQLALCHEMY_DATABASE_URL")
    redis_url: str = os.getenv("REDIS_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    hash_algorithm: str = os.getenv("ALGORITHM")


conf = FastAPIConfig()
