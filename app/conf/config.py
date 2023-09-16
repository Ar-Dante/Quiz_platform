from pydantic_settings import BaseSettings


class FastAPIConfig(BaseSettings):
    host: str = "localhost"
    port: int = 8022
    reload: bool = True
