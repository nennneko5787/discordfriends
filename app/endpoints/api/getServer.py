from fastapi import APIRouter

from ... import Env

router = APIRouter()


@router.get("/api/server/{serverId:int}")
async def getUserServer(serverId: int):
    conn = await Env.dbConnect()
    try:
        row = await conn.fetchrow("SELECT * FROM servers WHERE id = $1", int(serverId))
    finally:
        await conn.close()
    if row:
        row = dict(row)
        row["id_str"] = str(row["id"])
        return row
