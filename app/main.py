import uvicorn
from fastapi import FastAPI

from app.conf.config import FastAPIConfig

app = FastAPI()

conf = FastAPIConfig()


@app.get("/")
async def health_check() -> dict:
    """
    The health_check function is a simple endpoint that returns a JSON object
    with the status code, detail, and result. This function can be used to check
    if the server is up and running.

    :return: A dictionary, which is converted to json
    """
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


if __name__ == '__main__':
    uvicorn.run("main:app", host=conf.host, port=conf.port, reload=conf.reload)
