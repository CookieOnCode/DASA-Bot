import os
from dotenv import load_dotenv
from connectRankDB import connectDB

import discord
from discord.ext import commands
from discord import app_commands
import asyncio

from pretty_help import PrettyHelp

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="/",
intents=intents,help_command=PrettyHelp(color = discord.Color.random(),
                                        no_category = "Developer commands."))

@bot.event
async def on_ready():
    print("Bot is online")
    try:
        synched = await bot.tree.sync()
        print(f'Synched {len(synched)} command(s)')
    
    except Exception as e:
        print(e)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(description='Reload a cog.')
@commands.is_owner()
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f'cogs.{extension}')
        await ctx.send(f'`{extension}` `has been reloaded.`')
    except:
        await ctx.send("`Invalid module.`")

@bot.command(description='Turns off the bot.')
@commands.is_owner()
async def shut(ctx):
    await ctx.send('`Bot going offline!`👋')
    await bot.change_presence(status=discord.Status.offline)
    await bot.close()
    exit()

async def load():
    for file in os.listdir("DASABot\cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    await load()
    await bot.start(BOT_TOKEN)

asyncio.run(main())
