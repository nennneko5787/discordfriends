from fastapi import APIRouter

from ... import Env

router = APIRouter()


@router.get("/api/serverlist")
async def serverList(page: int = 0):
    conn = await Env.dbConnect()
    try:
        servers = await conn.fetch(
            'SELECT * FROM servers WHERE short IS NOT NULL AND description IS NOT NULL AND invite IS NOT NULL ORDER BY "uppedAt" DESC LIMIT 20 OFFSET $1',
            page * 20,
        )
    finally:
        await conn.close()
    return servers
