import asyncpg
import discord
from discord.ext import commands

from .. import Env


class ServerInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        conn: asyncpg.Connection = await Env.dbConnect()
        row = await conn.fetchrow("SELECT * FROM servers WHERE id = $1", guild.id)

        if row:
            try:
                await conn.execute(
                    """
                        DELETE FROM server WHERE id = $1;
                    """,
                    guild.id,
                )
            finally:
                await conn.close()
        return

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        conn: asyncpg.Connection = await Env.dbConnect()
        row = await conn.fetchrow("SELECT * FROM servers WHERE id = $1", after.id)

        if row:
            try:
                await conn.execute(
                    """
                        UPDATE servers
                        SET name = $1, icon = $2
                        WHERE id = $3
                    """,
                    after.name,
                    after.icon.url,
                    after.id,
                )
            finally:
                await conn.close()
        return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        conn: asyncpg.Connection = await Env.dbConnect()
        row = await conn.fetchrow(
            "SELECT * FROM servers WHERE id = $1", member.guild.id
        )

        if row:
            try:
                await conn.execute(
                    """
                        UPDATE servers
                        SET "memberCount" = $1
                        WHERE id = $2
                    """,
                    sum(not member.bot for member in member.guild.members),
                    member.guild.id,
                )
            finally:
                await conn.close()
        return

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        conn: asyncpg.Connection = await Env.dbConnect()
        row = await conn.fetchrow(
            "SELECT * FROM servers WHERE id = $1", member.guild.id
        )

        if row:
            try:
                await conn.execute(
                    """
                        UPDATE servers
                        SET "memberCount" = $1
                        WHERE id = $2
                    """,
                    sum(not member.bot for member in member.guild.members),
                    member.guild.id,
                )
            finally:
                await conn.close()
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerInfoCog(bot))
