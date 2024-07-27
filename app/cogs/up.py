from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
import asyncpg

from .. import Env


class UPCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.hybrid_command(name="up", description="サーバーをUPします。")
    async def upCommand(self, ctx: commands.Context):
        await ctx.defer()
        conn: asyncpg.Connection = await Env.dbConnect()
        row = await conn.fetchrow("SELECT * FROM servers WHERE id = $1", ctx.guild.id)

        if not row:
            embed = discord.Embed(
                title="でぃすフレに登録されていません。",
                description="`/register` コマンドを使用して、でぃすフレにサーバーを登録する準備を開始しましょう。",
                colour=discord.Colour.red(),
            ).set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar)
            await ctx.reply(embed=embed)
            return

        if not row["short"] or not row["description"]:
            embed = discord.Embed(
                title="でぃすフレに登録されていますが、概要と説明文が書かれていません。",
                description="[でぃすフレのダッシュボード](https://htnmk.site/dashboard)にアクセスして、サーバーの概要を書いて公開しましょう。",
                colour=discord.Colour.red(),
            ).set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar)
            await ctx.reply(embed=embed)
            return

        now = datetime.now(ZoneInfo("Etc/GMT"))
        uppedAt: datetime = row["uppedAt"].replace(
            tzinfo=ZoneInfo("Etc/GMT")
        ) + timedelta(hours=1)
        print(uppedAt, now)
        if uppedAt.timestamp() > now.timestamp():
            embed = discord.Embed(
                title="うｐするのが早すぎます。",
                description=f"うｐできるのは<t:{int(uppedAt.timestamp())}:R>からです。",
                colour=discord.Colour.red(),
            ).set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar)
            await ctx.reply(embed=embed)
            return

        now = now + timedelta(hours=1)

        try:
            await conn.execute(
                """
                    UPDATE servers
                    SET "uppedAt" = $1, name = $2, icon = $3, "memberCount" = $4
                    WHERE id = $5
                """,
                now,
                ctx.guild.name,
                ctx.guild.icon.url,
                len(ctx.guild.members),
                ctx.guild.id,
            )
        finally:
            await conn.close()

        embed = discord.Embed(
            title="うｐしました。",
            description=f"<t:{int(now.timestamp())}:R> にまたうｐできます。",
            colour=discord.Colour.green(),
        ).set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar)
        await ctx.reply(embed=embed)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(UPCog(bot))
