from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import aiohttp

from .. import Env, userLoader

router = APIRouter()


@router.get("/callback", response_class=RedirectResponse, include_in_schema=False)
async def discordCallback(request: Request, code: str):
    data = {
        "client_id": "1266569180199518289",
        "client_secret": Env.get("client_secret"),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": str(request.url.remove_query_params("code")).replace(
            "https", "http"
        ),
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://discord.com/api/oauth2/token", data=data, headers=headers
        ) as response:
            response.raise_for_status()
            json = await response.json()
    kanriID = await userLoader(json["access_token"])
    now = datetime.now(timezone.utc) + timedelta(days=365)
    response = RedirectResponse("/dashboard")
    response.set_cookie("token", kanriID, expires=now)
    return response
