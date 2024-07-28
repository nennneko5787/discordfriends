import json as JSON
import random
import string

import aiohttp

from .env import Env

users = {}


def randomname(n):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


users = {}


async def getUser(kanriID: dict):
    if not kanriID in users:
        conn = await Env.dbConnect()
        try:
            row = dict(
                await conn.fetchrow("SELECT data FROM auth WHERE id = $1", kanriID)
            )
        finally:
            await conn.close()
        row["data"] = JSON.loads(row["data"])
        users[kanriID] = row["data"]
        return row["data"]
    else:
        return users[kanriID]


async def userLoader(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://discord.com/api/users/@me", headers=headers
        ) as response:
            response.raise_for_status()
            json = await response.json()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://discord.com/api/users/@me/guilds", headers=headers
        ) as response:
            response.raise_for_status()
            json["guilds"] = await response.json()

    kanriID = randomname(10)

    conn = await Env.dbConnect()

    try:
        await conn.execute(
            """
                INSERT INTO auth (id, data)
                VALUES ($1, $2)
            """,
            kanriID,
            JSON.dumps(json),
        )
    finally:
        await conn.close()

    return kanriID
