from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter

from ... import Env

router = APIRouter()


@router.get("/api/serverlist")
async def serverList(page: int = 0):
    conn = await Env.dbConnect()
    servers = []
    try:
        _servers = await conn.fetch(
            'SELECT * FROM servers WHERE short IS NOT NULL AND description IS NOT NULL AND invite IS NOT NULL ORDER BY "uppedAt" DESC LIMIT 20 OFFSET $1',
            page * 20,
        )
        for server in _servers:
            server = dict(server)
            server["id_str"] = str(server["id"])
            if server["createdAt"].replace(tzinfo=ZoneInfo("Etc/GMT")) + timedelta(
                days=30
            ) <= datetime.now(ZoneInfo("Etc/GMT")):
                server["new"] = True
            else:
                server["new"] = False

            servers.append(server)
    finally:
        await conn.close()
    return servers
