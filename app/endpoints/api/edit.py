from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from ... import Env, getUser

router = APIRouter()


class ServerModel(BaseModel):
    short: str
    description: str
    nsfw: bool


@router.post("/api/server/{serverId:int}/edit")
async def editServer(
    serverId: int, serverModel: ServerModel, authorization: str = Header(...)
):
    user = await getUser(authorization)
    if not user:
        raise HTTPException(401)
    conn = await Env.dbConnect()
    ownFlag = False
    for server in user["guilds"]:
        if server["id"] == str(serverId):
            print("一致した")
            if server["permissions"] & 0x00000020:
                ownFlag = True
            else:
                print(server["raw"]["permissions"])
    if not ownFlag:
        raise HTTPException(400)

    if len(serverModel.short) > 50:
        raise HTTPException(400, "概要が長すぎます(50文字まで)")

    try:
        await conn.execute(
            """
            UPDATE servers
            SET short = $1, description = $2, nsfw = $3
            WHERE id = $4
            """,
            serverModel.short.replace("\r\n", "").replace("\r", "").replace("\n", ""),
            serverModel.description,
            serverModel.nsfw,
            serverId,
        )
    finally:
        await conn.close()
    return {"status": True}
