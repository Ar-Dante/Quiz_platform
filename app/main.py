import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.conf.config import conf
from app.routes import health, users, auth, companies, quizzes, results, notifications, analitics
from app.services.schedule_event import schedule_notification_sender

app = FastAPI()

scheduler = AsyncIOScheduler()

scheduler.add_job(schedule_notification_sender, 'cron', hour=0, minute=0)

scheduler.start()   
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.route)
app.include_router(auth.route)
app.include_router(users.route)
app.include_router(notifications.route)
app.include_router(companies.route)
app.include_router(quizzes.route)
app.include_router(results.route)
app.include_router(analitics.route)

if __name__ == "__main__":
    uvicorn.run("main:app", host=conf.host, port=conf.port, reload=conf.reload)
