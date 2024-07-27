from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="pages")


@router.get("/")
async def index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


@router.get("/dashboard")
async def dashboard(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("dashboard.html", context)


@router.get("/servers/{serverId:int}/edit")
async def serverEdit(request: Request, serverId: int):
    context = {"request": request, "serverId": serverId}
    return templates.TemplateResponse("edit.html", context)
