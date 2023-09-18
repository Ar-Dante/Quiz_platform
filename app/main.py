import uvicorn
from fastapi import FastAPI

from app.conf.config import FastAPIConfig
from app.routes import health

app = FastAPI()

conf = FastAPIConfig()

app.include_router(health.route)

if __name__ == "__main__":
    uvicorn.run("main:app", host=conf.host, port=conf.port, reload=conf.reload)
