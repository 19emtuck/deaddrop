#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Copyright (C) 2024  Stéphane Bard <stephane.bard@gmail.com>

 This file is part of deaddrop

 deaddrop is free software; you can redistribute it and/or modify it under
 the terms of the M.I.T License.
"""

from typing import List, Annotated
import asyncio
import uuid
import os
import json
from datetime import datetime

from fastapi import (
    FastAPI,
    Request,
    Response,
    Header,
    HTTPException,
    WebSocket,
    WebSocketException,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Header as HeaderType
from aredis import StrictRedis

# set redis for scalability
redis_host = os.getenv("REDIS_HOST_NAME", "127.0.0.1")
redis_port = int(os.getenv("REDIS_TCP_PORT", "6379"))
redis_db = int(os.getenv("REDIS_DEFAULT_DEB", "0"))

app = FastAPI(redoc_url=None, docs_url=None)
client: StrictRedis = StrictRedis(host=redis_host, port=redis_port, db=redis_db)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class UnknownToken(HTTPException):
    """
    exception raised if token is unknown
    """


@app.websocket("/tokens/{token_id}/ws")
async def websocket_endpoint(websocket: WebSocket, token_id: str):
    """
        websocket endpoint if token is known
    """
    data = await client.get(token_id)
    if data is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    await websocket.accept()
    data = json.loads(data)
    while not data:
        serialized_data = await client.get(token_id)
        data = json.loads(serialized_data)
        if data:
            await websocket.send_text(f"{data}")
            break
        await asyncio.sleep(0.01)
    else:
        await websocket.send_text(f"{data}")
    await websocket.close()


async def default_route(scope, receive, send):
    """
    a default route for K8s.
    simple heart beat
    """
    response = Response("Ok")
    await response(scope, receive, send)


app.router.default = default_route


async def add_token(token: str) -> None:
    """
    create token on REDIS
    """
    await client.set(token, json.dumps([]), 3600)


async def save_data(
    token: str, method: str, data: str, headers: List, user_agent: str | None = None
):
    """
    Save data on the corresponding token
    """
    now = datetime.now()
    payload = {
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "method": method,
        "content": data,
        "headers": headers,
        "user_agent": user_agent,
    }

    data = await client.get(token)
    if data:
        data = json.loads(data)
        data.append(payload)
        await client.set(token, json.dumps(data), 3600)
    else:
        raise UnknownToken(status_code=404, detail="unknown")


@app.get("/token/{token:str}/requests")
async def get_content(token):
    """
    create a valid UUID
    """
    data = await client.get(token)
    if data:
        data = json.loads(data)
        result = {"data": data}
    else:
        raise UnknownToken(status_code=404, detail="unknown")
    return result


@app.get("/health", status_code=218)
async def healthcheck():
    """
    validate that the app is up and running
    """
    return Response("Ok")


@app.post("/token")
async def create_token():
    """
    create a valid UUID
    """
    token = str(uuid.uuid4())
    await add_token(token)
    return {"token": token}


@app.delete("/{token:str}")
@app.patch("/{token:str}")
@app.put("/{token:str}")
@app.get("/{token:str}")
@app.post("/{token:str}")
async def dead_drop_on_token(
    token: str, request: Request, user_agent: Annotated[str | None, Header()] = None
):
    """
    receives a request (whatever verb) and will extract data from this request
    and attach these data on related token (the one extract from URL path)
    """
    content = await request.body()
    content = content.decode("utf-8")
    headers = [(h.decode("utf-8"), v.decode("utf-8")) for (h, v) in request.headers.raw]
    method = request.method
    method = method.upper()

    if isinstance(user_agent, HeaderType):
        # ensure data will be a string
        user_agent = repr(user_agent)

    await save_data(token, method, content, headers, user_agent=user_agent)
    return "Ok"
