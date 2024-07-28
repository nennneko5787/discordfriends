import asyncpg
import discord
from discord.ext import commands, tasks

from .. import Env


class PresenceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener
    async def on_ready(self):
        self.presence.start()

    @tasks.loop(hours=1)
    async def presence(self):
        conn: asyncpg.Connection = await Env.dbConnect()
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM servers WHERE short IS NOT NULL AND description IS NOT NULL AND invite IS NOT NULL"
        )
        await conn.close()
        await self.bot.change_presence(
            activity=discord.Game(
                f"{count} SERVERS REGISTED / {len(self.bot.guilds) - count} SERVERS NOT REGISTED"
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(PresenceCog(bot))
