from fastapi import APIRouter

route = APIRouter()


@route.get("/")
async def health_check() -> dict:
    """
    The health_check function is a simple endpoint that returns a JSON object
    with the status code, detail, and result. This function can be used to check
    if the server is up and running.

    :return: A dictionary, which is converted to json
    """
    return {"status_code": 200, "detail": "ok", "result": "working"}
