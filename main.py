import os
import discord
from discord.ext import commands
import json
import random
import asyncio

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Estado do jogo
current_agent = None
current_quote = None
game_active = False
winner_found = False
start_time = None
quotes_data = {}

# Carregar frases do arquivo JSON
def load_quotes():
    global quotes_data
    with open("quotes.json", "r", encoding="utf-8") as file:
        quotes_data = json.load(file)

def get_random_quote():
    agent = random.choice(list(quotes_data.keys()))
    quote = random.choice(quotes_data[agent])
    return agent, quote

@bot.event
async def on_ready():
    load_quotes()
    print(f"✅ Bot online como {bot.user}")

@bot.command(name="rq")
async def start_round(ctx):
    global current_agent, current_quote, game_active, winner_found, start_time

    if game_active:
        await ctx.send("⚠️ Um jogo já está em andamento!")
        return

    agent, quote = get_random_quote()

    current_agent = agent
    current_quote = quote
    game_active = True
    winner_found = False
    start_time = asyncio.get_event_loop().time()

    await ctx.send(
        f"🧠 Adivinha a frase do agente!\n"
        f"💬 **{quote}**\n"
        f"⏱️ Tens 60 segundos! Usa `!aq nome-do-agente` para responder!"
    )

    await asyncio.sleep(60)

    if not winner_found:
        await ctx.send(f"⏰ Tempo esgotado! A resposta certa era **{current_agent}**.")
        game_active = False

@bot.command(name="aq")
async def answer_quote(ctx, *, guess):
    global current_agent, game_active, winner_found

    if not game_active:
        await ctx.send("❌ Nenhum jogo em andamento.")
        return

    if winner_found:
        await ctx.send("⚠️ Já houve um vencedor.")
        return

    elapsed = asyncio.get_event_loop().time() - start_time
    if elapsed > 60:
        game_active = False
        await ctx.send(f"⏰ Tempo esgotado! A resposta era **{current_agent}**.")
        return

    if guess.strip().lower() == current_agent.lower():
        winner_found = True
        game_active = False
        await ctx.send(f"🎉 Parabéns {ctx.author.mention}, acertaste! Era **{current_agent}**.")
    else:
        await ctx.send(f"❌ Errado, {ctx.author.mention}. Tenta outra vez!")

# Rodar bot
bot.run(os.environ["DISCORD_TOKEN"])
