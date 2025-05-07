import os
import discord
from discord.ext import commands
import requests
import random
import asyncio
from bs4 import BeautifulSoup

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Lista dos agentes válidos (nomes devem estar conforme aparecem na URL)
AGENTS = [
    "Brimstone", "Phoenix", "Sage", "Sova", "Viper", "Cypher", "Reyna", "Killjoy", "Breach", "Omen",
    "Jett", "Raze", "Skye", "Yoru", "Astra", "KAY/O", "Chamber", "Neon", "Fade", "Harbor",
    "Gekko", "Deadlock", "Iso", "Clove", "Vyse", "Tejo", "Waylay"
]

def get_random_quote():
    agent = random.choice(AGENTS)
    # Para o KAY/O, substituir / por %2F para o link funcionar corretamente
    if agent == "KAY/O":
        url_agent = "KAYO"
    else:
        url_agent = agent.replace("/", "%2F")  # Para outros casos com "/"
    
    url = f"https://valorant.fandom.com/wiki/{url_agent}/Quotes"

    response = requests.get(url)
    if response.status_code != 200:
        return None, None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Pega frases que estão em <ul><li> normalmente (ajustável)
    quotes = []
    for li in soup.select("ul > li"):
        text = li.get_text(strip=True)
        if 20 < len(text) < 200:  # Filtra frases muito curtas ou longas
            quotes.append(text)

    if not quotes:
        return None, None

    return agent, random.choice(quotes)

# Estado do jogo
current_agent = None
current_quote = None
game_active = False
winner_found = False
start_time = None

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")

@bot.command(name="rq")
async def start_round(ctx):
    global current_agent, current_quote, game_active, winner_found, start_time

    if game_active:
        await ctx.send("⚠️ Um jogo já está em andamento!")
        return

    agent, quote = get_random_quote()

    if not quote:
        await ctx.send("❌ Não foi possível obter agentes ou frases.")
        return

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
    global current_agent, current_quote, game_active, winner_found

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
