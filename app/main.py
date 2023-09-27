import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.conf.config import conf
from app.routes import health, users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.route)
app.include_router(users.route)

if __name__ == "__main__":
    uvicorn.run("main:app", host=conf.host, port=conf.port, reload=conf.reload)
