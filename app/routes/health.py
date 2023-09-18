import json

from fastapi import APIRouter, Response

route = APIRouter(tags=["health_check"])


@route.get("/")
async def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}