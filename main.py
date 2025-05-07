import os
import discord
from discord.ext import commands
import requests
import random
import asyncio

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Estado do jogo
current_agent = None
current_audio_url = None
game_active = False
winner_found = False
start_time = None

# Função para obter agente aleatório e frase
def get_random_quote_from_valorant_api():
    url = "https://valorant-api.com/v1/agents?isPlayableCharacter=true&language=pt-BR"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None, None

    data = response.json()
    agents = data.get("data", [])
    if not agents:
        return None, None, None

    agent = random.choice(agents)
    name = agent["displayName"]

    voice_lines = agent.get("voiceLine", {}).get("mediaList", [])
    if not voice_lines:
        return None, None, None

    selected_line = random.choice(voice_lines)
    audio_url = selected_line.get("wave", None)

    return name, "Ouça esta frase e adivinhe o agente:", audio_url

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")

@bot.command(name="rq")
async def start_quote_game(ctx):
    global current_agent, current_audio_url, game_active, winner_found, start_time

    if game_active:
        await ctx.send("⚠️ Um jogo já está em andamento!")
        return

    current_agent, message, current_audio_url = get_random_quote_from_valorant_api()

    if not current_agent or not current_audio_url:
        await ctx.send("❌ Não foi possível buscar uma frase. Tente novamente mais tarde.")
        return

    game_active = True
    winner_found = False
    start_time = asyncio.get_event_loop().time()

    await ctx.send("🎮 Jogo iniciado! Ouça a frase abaixo e adivinhe o agente digitando `!aq nome_do_agente`.")
    await ctx.send(current_audio_url)

    await asyncio.sleep(60)

    if not winner_found:
        await ctx.send(f"⏰ Tempo esgotado! A resposta correta era **{current_agent}**.")
    game_active = False

@bot.command(name="aq")
async def guess_agent(ctx, *, guess):
    global current_agent, game_active, winner_found, start_time

    if not game_active:
        await ctx.send("❌ Nenhum jogo em andamento. Use `!rq` para começar.")
        return

    if winner_found:
        await ctx.send("🎉 Já houve um vencedor neste jogo.")
        return

    elapsed_time = asyncio.get_event_loop().time() - start_time
    if elapsed_time > 60:
        game_active = False
        await ctx.send("⏳ O tempo acabou! Use `!rq` para jogar novamente.")
        return

    if guess.strip().lower() == current_agent.strip().lower():
        winner_found = True
        game_active = False
        await ctx.send(f"🎉 Parabéns {ctx.author.mention}, você acertou!")
        await ctx.send(f"✅ A resposta era: **{current_agent}**.")
        await ctx.send(f"/xp add user: {ctx.author.mention} amount: 12500")
    else:
        await ctx.send(f"❌ Errado {ctx.author.mention}, tenta novamente!")

# Iniciar bot
bot.run(os.environ["DISCORD_TOKEN"])
