import json as JSON
import re

import aiofiles
import asyncpg
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from .. import Env

router = APIRouter()
templates = Jinja2Templates(directory="pages")


@router.get("/")
async def index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


@router.get("/privacy")
async def index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("privacy.html", context)


@router.get("/terms")
async def index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("terms.html", context)


@router.get("/dashboard")
async def dashboard(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("dashboard.html", context)


@router.get("/servers/{serverId:int}")
async def serverEdit(request: Request, serverId: int):
    async with aiofiles.open("crawler-user-agents.json", "r") as f:
        raw = await f.read()
    bots = JSON.loads(raw)
    crawler = False
    for bot in bots:
        if re.search(bot["pattern"], request.headers["user-agent"]):
            crawler = True
    if not crawler:
        context = {"request": request, "serverId": serverId}
        return templates.TemplateResponse("server.html", context)
    else:
        conn: asyncpg.Connection = await Env.dbConnect()
        row = await conn.fetchrow("SELECT * FROM servers WHERE id = $1", serverId)
        context = {"request": request, "server": row}
        return templates.TemplateResponse("serverOGP.html", context)


@router.get("/servers/{serverId:int}/edit")
async def serverEdit(request: Request, serverId: int):
    context = {"request": request, "serverId": serverId}
    return templates.TemplateResponse("edit.html", context)
