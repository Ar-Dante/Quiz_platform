import json

from fastapi import APIRouter, Response

route = APIRouter(tags=["health_check"])


@route.get("/")
async def health_check():
    """
    The health_check function is a simple endpoint that returns a 200
    status code and the string &quot;ok&quot; in the body.
    This function can be used to verify that your API is up and running.

    :return: A response object with the status code 200 and a json body

    """
    response_content = {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    json_content = json.dumps(response_content)
    return Response(
        status_code=200,
        content=json_content,
        media_type="application/json"
    )
