from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import asyncpg
import discord
from discord.ext import commands

from .. import Env


class InviteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.hybrid_command(
        name="invite",
        description="サーバーの招待先チャンネルを現在のチャンネルまたは特定のチャンネルに変更します。",
    )
    async def inviteCommand(
        self, ctx: commands.Context, channel: discord.TextChannel = None
    ):
        if not channel:
            channel = ctx.channel

        if not ctx.author.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="権限がありません",
                description="このコマンドを実行するには、**サーバーの管理**権限が必要です。",
                colour=discord.Colour.red(),
            ).set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar)
            await ctx.send(embed=embed, ephemeral=True)
            return

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

        invite = await channel.create_invite()
        invite_url = invite.url

        try:
            await conn.execute(
                """
                    UPDATE servers
                    SET invite = $1
                    WHERE id = $2
                """,
                invite_url,
                ctx.guild.id,
            )
        finally:
            await conn.close()

        embed = discord.Embed(
            title="サーバーの招待チャンネルを変更しました。",
            description=f"招待先チャンネル: {channel.jump_url}",
            colour=discord.Colour.green(),
        ).set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar)
        await ctx.reply(embed=embed)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(InviteCog(bot))
