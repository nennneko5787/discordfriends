import asyncio
import os
from contextlib import asynccontextmanager

import discord
from discord.ext import commands
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.endpoints import callback, frontend
from app.endpoints.api import edit, getServer, getUserServer, serverList

if os.path.isfile(".env"):
    from dotenv import load_dotenv

    load_dotenv(verbose=True)

discord.utils.setup_logging()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot: commands.Bot = commands.Bot("disfre#", intents=intents)


@bot.command(name="reload")
async def reloadExtention(ctx: commands.Context, extension: str):
    if ctx.author.id != 1048448686914551879:
        return
    await bot.reload_extension(extension)
    await ctx.reply(f"reloaded {extension}")


@bot.command(name="sync")
async def commandSync(ctx: commands.Context):
    if ctx.author.id != 1048448686914551879:
        return
    await bot.tree.sync()
    await ctx.reply(f"synced commands")


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(bot.start(os.getenv("discord")))
    yield


@bot.event
async def setup_hook():
    await bot.load_extension("app.cogs.register")
    await bot.load_extension("app.cogs.up")
    await bot.load_extension("app.cogs.invite")
    await bot.load_extension("app.cogs.presence")


app = FastAPI(
    title="でぃすこーどフレンズ！",
    summary="Discordサーバーを紹介するサイト",
    version="2024.07.28",
    lifespan=lifespan,
)
app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

app.include_router(callback.router)
app.include_router(frontend.router)
app.include_router(serverList.router)
app.include_router(getUserServer.router)
app.include_router(edit.router)
app.include_router(getServer.router)
