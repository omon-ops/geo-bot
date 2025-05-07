import os
import discord
from discord.ext import commands
import requests
import random
import asyncio
from bs4 import BeautifulSoup

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

BASE_URL = "https://valorant.fandom.com"
CATEGORY_URL = f"{BASE_URL}/wiki/Category:Voice_Lines"

current_agent = None
current_quote = None
game_active = False
winner_found = False
start_time = None

def get_all_agents():
    response = requests.get(CATEGORY_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.select(".category-page__member-link")

    agents = []
    for link in links:
        href = link.get("href")
        name = link.text.strip()
        if "/wiki/" in href and "/Quotes" not in href:
            agent_name = name
            agent_url = f"{BASE_URL}/wiki/{agent_name.replace(' ', '_')}/Quotes"
            agents.append((agent_name, agent_url))
    return agents

def get_random_quote_from_agent(agent_url):
    response = requests.get(agent_url)
    soup = BeautifulSoup(response.content, "html.parser")

    quotes = []
    for li in soup.select("ul > li"):
        text = li.get_text(strip=True)
        if 10 < len(text) < 200:
            quotes.append(text)

    return random.choice(quotes) if quotes else None

@bot.command()
async def rq(ctx):
    global current_agent, current_quote, game_active, winner_found, start_time

    if game_active:
        await ctx.send("⚠️ Um jogo já está em andamento!")
        return

    agents = get_all_agents()
    if not agents:
        await ctx.send("❌ Não foi possível obter agentes.")
        return

    current_agent, agent_url = random.choice(agents)
    current_quote = get_random_quote_from_agent(agent_url)

    if not current_quote:
        await ctx.send("❌ Não foi possível obter uma frase do agente.")
        return

    game_active = True
    winner_found = False
    start_time = asyncio.get_event_loop().time()

    await ctx.send(
        f"🧠 Adivinha o agente pela frase:\n\n"
        f"💬 \"{current_quote}\"\n"
        f"⏱️ Tens 60 segundos para responder com `!aq <nome>`!"
    )

    await asyncio.sleep(60)

    if not winner_found:
        await ctx.send(f"⏰ Tempo esgotado! A resposta correta era **{current_agent}**.")
    game_active = False

@bot.command()
async def aq(ctx, *, guess):
    global current_agent, current_quote, game_active, winner_found, start_time

    if not game_active:
        await ctx.send("❌ Nenhum jogo em andamento.")
        return

    if winner_found:
        await ctx.send("✅ Já houve um vencedor.")
        return

    elapsed = asyncio.get_event_loop().time() - start_time
    if elapsed > 60:
        await ctx.send("⏳ O tempo acabou!")
        game_active = False
        return

    if guess.strip().lower() == current_agent.lower():
        winner_found = True
        game_active = False
        await ctx.send(f"🎉 Parabéns {ctx.author.mention}! A resposta correta era **{current_agent}**!")
    else:
        await ctx.send(f"❌ Errado, {ctx.author.mention}! Tenta de novo!")

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")

bot.run(os.environ["DISCORD_TOKEN"])
