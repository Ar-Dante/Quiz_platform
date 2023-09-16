import uvicorn
from fastapi import FastAPI

from app.conf.config import FastAPIConfig
from app.routes import health_check

app = FastAPI()

conf = FastAPIConfig()

app.include_router(health_check.route, tags=["health_check"])


if __name__ == "__main__":
    uvicorn.run("main:app", host=conf.host, port=conf.port, reload=conf.reload)
