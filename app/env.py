import os
from typing import Optional

import asyncpg

if os.path.isfile(".env"):
    from dotenv import load_dotenv

    load_dotenv(verbose=True)


class Env:
    @classmethod
    def get(cls, key: str) -> Optional[str]:
        return os.getenv(key)

    @classmethod
    async def dbConnect(cls) -> asyncpg.Connection:
        return await asyncpg.connect(cls.get("dsn"), statement_cache_size=0)
