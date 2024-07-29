import asyncio

from fastapi import APIRouter, Header, Cookie
from fastapi.responses import RedirectResponse

from .. import logout

router = APIRouter()


@router.get("/logout", response_class=RedirectResponse)
async def logoutEndpoint(token: str = Cookie(...)):
    await logout(token)
    response = RedirectResponse("/")
    response.set_cookie("token", "", max_age=0, expires=0)
    return response
