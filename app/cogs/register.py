import asyncpg
import discord
from discord.ext import commands

from .. import Env


class RegisterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.hybrid_command(
        name="register", description="サーバーをでぃすフレに掲載できる状態にします。"
    )
    async def registerCommand(self, ctx: commands.Context):
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
        val = await conn.fetchval(
            "SELECT name FROM servers WHERE id = $1", ctx.guild.id
        )

        if val:
            embed = discord.Embed(
                title="既にでぃすフレに登録できる状態のようです",
                description="[でぃすフレのダッシュボード](https://htnmk.site/dashboard)にアクセスして、サーバーの概要を書いて公開しましょう。",
                colour=discord.Colour.red(),
            ).set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar)
            await ctx.reply(embed=embed)
            return

        try:
            await conn.execute(
                """
                    INSERT INTO servers (id, name, "memberCount", icon, "serverCreatedDate")
                    VALUES ($1, $2, $3, $4, $5)
                """,
                ctx.guild.id,
                ctx.guild.name,
                sum(not member.bot for member in ctx.guild.members),
                ctx.guild.icon.url,
                ctx.guild.created_at,
            )
        finally:
            await conn.close()

        embed = discord.Embed(
            title="でぃすフレに登録する準備が完了しました！",
            description="まず先に`/invite`コマンドを招待したいチャンネルにて実行してください。\nそして、[でぃすフレのダッシュボード](https://htnmk.site/dashboard)にアクセスして、サーバーの概要を書いて公開しましょう。",
            colour=discord.Colour.green(),
        ).set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar)
        await ctx.reply(embed=embed)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(RegisterCog(bot))
