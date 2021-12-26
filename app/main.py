#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of deaddrop
#
# deaddrop is free software; you can redistribute it and/or modify it under
# the terms of the M.I.T License.
#
from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, Request, Response, Header, HTTPException
import uuid
import pickle
from aredis import StrictRedis

from cachetools import TTLCache

app = FastAPI(redoc_url=None, docs_url=None)
store = TTLCache(maxsize=10000, ttl=3600)
client = StrictRedis(host="127.0.0.1", port=6379, db=0)


class UnknownToken(HTTPException):
    ...


async def default_route(scope, receive, send):
    request = Request(scope, receive=receive, send=send)
    response = Response("Ok")
    await response(scope, receive, send)


app.router.default = default_route


async def add_token(token: str) -> None:
    """ """
    await client.set(token, pickle.dumps([]))


async def save_data(token: str, method: str, data: str, headers: List):
    """ """
    now = datetime.now()
    payload = {
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "method": method,
        "content": data.decode("utf-8"),
        "headers": headers,
    }

    data = await client.get(token)
    if data:
        data = pickle.loads(data)
        data.append(payload)
        await client.set(token, pickle.dumps(data))
    else:
        raise UnknownToken(status_code=404, detail="unknown")


@app.get("/token/{token:str}/requests")
async def get_content(token):
    """
    create a valid UUID
    """
    data = await client.get(token)
    if data:
        data = pickle.loads(data)
        result = {"data": data}
    else:
        raise UnknownToken(status_code=404, detail="unknown")
    return result


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
async def read_item(
    token: str, request: Request, user_agent: Optional[str] = Header(None)
):
    content = await request.body()
    headers = request.headers.raw
    method = request.method
    method = method.upper()

    await save_data(token, method, content, headers)
    return "Ok"
