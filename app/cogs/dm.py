import asyncpg
import discord
from discord.ext import commands

from .. import Env


class DMCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="dmsend")
    async def DMSendCommand(self, ctx: commands.Context):
        if ctx.author.id != 1048448686914551879:
            embed = discord.Embed(
                title="権限がありません",
                description="このコマンドを実行するには、**サーバーの管理**権限が必要です。",
                colour=discord.Colour.red(),
            ).set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar)
            await ctx.send(embed=embed, ephemeral=True)
            return

        await ctx.defer()
        conn: asyncpg.Connection = await Env.dbConnect()
        for guild in self.bot.guilds:
            try:
                row = await conn.fetchrow(
                    "SELECT * FROM servers WHERE id = $1", guild.id
                )
            except:
                continue
            if not row:
                if not guild.owner.dm_channel:
                    await guild.owner.create_dm()
                embed = (
                    discord.Embed(
                        title="あなたのサーバーはでぃすこーどフレンズ！に登録されていません。",
                        description=f"登録するには、**{guild.name}**にて以下の操作を行ってください。\n- `/register` コマンドを実行する。\n`/invite` コマンドを実行する。\n[でぃすこーどフレンズ！のダッシュボード](https://htnmk.site/dashboard)にアクセスし、サーバーの概要を書く。\n\n以上の操作を行っても公開できない場合は、[でぃすこーどフレンズ！のサポートサーバー](https://discord.gg/M3bpz4hCjc)まで報告をお願いします。\n※このDMに返信しても、私は対応できません。",
                        color=discord.Colour.blurple(),
                    )
                    .set_author(
                        name=self.bot.user.name, icon_url=self.bot.user.display_avatar
                    )
                    .set_footer(
                        text=guild.name,
                        icon_url=(
                            guild.icon.url
                            if guild.icon.url is not None
                            else f"https://cdn.discordapp.com/embed/avatars/{(guild.id >> 22) % len(discord.enums.DefaultAvatar)}.png"
                        ),
                    )
                )
                await guild.owner.dm_channel.send(embed=embed)
                await ctx.reply(
                    f"{guild.name} ({guild.id}) の主の {guild.owner.name} ({guild.owner.id}) にDMを送りました。"
                )
        await conn.close()
        await ctx.reply("処理完了")
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(DMCog(bot))
