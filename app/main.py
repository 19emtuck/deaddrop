from typing import Optional, Any, List
from datetime import date, datetime, timedelta
from fastapi import FastAPI, Request, Response, Header, HTTPException
import uuid
from cachetools import TTLCache

app = FastAPI(redoc_url=None, docs_url=None)
store = TTLCache(maxsize=10000, ttl=3600)


class UnknownToken(HTTPException):
    ...


async def default_route(scope, receive, send):
    request = Request(scope, receive=receive, send=send)
    response = Response("Ok")
    await response(scope, receive, send)


app.router.default = default_route


def add_token(token: str) -> None:
    """ """
    store[token] = []


def save_data(token: str, method: str, data: str, headers: List):
    """ """
    now = datetime.now()
    payload = {
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "method": method,
        "content": data,
        "headers": headers,
    }
    if token in store:
        store[token].append(payload)
    else:
        raise UnknownToken(status_code=404, detail="unknown")


@app.get("/token/{token:str}/requests")
def get_content(token):
    """
    create a valid UUID
    """
    if token in store:
        result = {"data": store[token]}
    else:
        raise UnknownToken(status_code=404, detail="unknown")
    return result


@app.post("/token")
def create_token():
    """
    create a valid UUID
    """
    token = str(uuid.uuid4())
    add_token(token)
    return {"token": token}


@app.delete("/{token:str}")
@app.patch("/{token:str}")
@app.put("/{token:str}")
@app.get("/{token:str}")
@app.post("/{token:str}")
async def read_item(
    token: str, request: Request, user_agent: Optional[str] = Header(None)
):
    content = await request.body()
    headers = request.headers.raw
    method = request.method
    method = method.upper()

    save_data(token, method, content, headers)
    return "Ok"
