import os
from discord.ext import commands
import discord

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(os.environ["DISCORD_TOKEN"])
