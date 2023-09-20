import logging
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()
sqlalchemy_database_url = os.getenv("SQLALCHEMY_DATABASE_URL")
redis_url = os.getenv("REDIS_URL")

logging.basicConfig(level=logging.DEBUG,
                    filename="meduzzen_intern.log",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )


class FastAPIConfig(BaseSettings):
    host: str = os.getenv("MAIN_HOST")
    port: int = os.getenv("MAIN_PORT")
    reload: bool = os.getenv("RELOAD")


conf = FastAPIConfig()
