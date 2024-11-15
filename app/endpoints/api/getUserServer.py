from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import asyncio

from fastapi import APIRouter, Header, HTTPException

from ... import Env, getUser

router = APIRouter()


@router.get("/api/user/servers")
async def getUserServer(authorization: str = Header(...)):
    user = await getUser(authorization)
    if not user:
        raise HTTPException(401)
    conn = await Env.dbConnect()
    servers = []
    try:
        for server in user["guilds"]:
            if server["permissions"] & 0x00000020:
                row = await conn.fetchrow(
                    "SELECT * FROM servers WHERE id = $1", int(server["id"])
                )
                if row:
                    row = dict(row)
                    row["raw"] = server
                    row["id_str"] = str(row["id"])
                    at: datetime = row["createdAt"].replace(
                        tzinfo=ZoneInfo("Etc/GMT")
                    ) + timedelta(days=10)
                    now = datetime.now(ZoneInfo("Etc/GMT"))
                    if at.timestamp() >= now.timestamp():
                        row["new"] = True
                    else:
                        row["new"] = False

                    at: datetime = row["serverCreatedDate"].replace(
                        tzinfo=ZoneInfo("Etc/GMT")
                    ) + timedelta(days=30)
                    now = datetime.now(ZoneInfo("Etc/GMT"))
                    if at.timestamp() >= now.timestamp():
                        row["dekitate"] = True
                    else:
                        row["dekitate"] = False
                    servers.append(row)
            await asyncio.sleep(0)
    finally:
        await conn.close()
    return servers
