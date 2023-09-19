from pydantic_settings import BaseSettings


class FastAPIConfig(BaseSettings):
    host: str = "localhost"
    port: int = 8000
    reload: bool = True


conf = FastAPIConfig()
