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
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Função para pegar a lista de agentes e frases do site
def get_agents_and_quotes():
    url = "https://kingdomarchives.com/agents"
    response = requests.get(url)
    print(f"Status da requisição: {response.status_code}")  # Debugging
    soup = BeautifulSoup(response.content, 'html.parser')

    agents = []
    agent_elements = soup.find_all("div", class_="agent-card")  # Exemplo de classe, ajuste conforme o site real
    print(f"Encontrado {len(agent_elements)} agentes.")  # Debugging
    
    for agent in agent_elements:
        name = agent.find("h2").get_text(strip=True)
        quotes = [quote.get_text(strip=True) for quote in agent.find_all("p")]  # Vamos pegar todas as frases em <p>
        
        if name and quotes:
            agents.append({"name": name, "quotes": quotes})

    return agents

# Função para escolher um agente e uma frase aleatória
def get_random_agent_and_quote():
    agents = get_agents_and_quotes()
    if not agents:
        return None, None

    random_agent = random.choice(agents)
    agent_name = random_agent["name"]
    random_quote = random.choice(random_agent["quotes"])

    return agent_name, random_quote

# Estado do jogo
current_agent = None
current_quote = None
start_time = None
game_active = False
winner_found = False

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")

@bot.command()
async def start_game(ctx):
    global current_agent, current_quote, start_time, game_active, winner_found

    print("Comando start_game foi chamado.")  # Debugging

    if game_active:
        await ctx.send("⚠️ Já existe um jogo em andamento!")
        return

    # Obter agente e frase aleatória
    current_agent, current_quote = get_random_agent_and_quote()

    if not current_agent:
        await ctx.send("❌ Não foi possível carregar os agentes ou frases. Tente novamente mais tarde.")
        return

    game_active = True
    winner_found = False

    # Embaralha a frase para dificultar a adivinhação
    scrambled_quote = ''.join(random.sample(current_quote, len(current_quote)))

    await ctx.send(
        f"🧭 Jogo de Adivinhação de Frases iniciado!\n"
        f"💬 Frase embaralhada do agente **{current_agent}**: {scrambled_quote}\n"
        f"🕐 Tens 60 segundos para adivinhar a frase!"
    )

    start_time = asyncio.get_event_loop().time()
    await asyncio.sleep(60)

    if not winner_found:
        await ctx.send(f"⏰ Tempo esgotado! Ninguém acertou desta vez. A frase correta era **{current_quote}**.")
    game_active = False

@bot.command()
async def guess(ctx, *, phrase):
    global current_quote, start_time, game_active, winner_found

    if not game_active:
        await ctx.send("❌ Nenhum jogo em andamento.")
        return

    if winner_found:
        await ctx.send("🎉 Já houve um vencedor neste jogo.")
        return

    elapsed_time = asyncio.get_event_loop().time() - start_time
    if elapsed_time > 60:
        await ctx.send("⏳ O tempo para adivinhar já acabou.")
        game_active = False
        return

    if phrase.strip().lower() == current_quote.strip().lower():
        winner_found = True
        game_active = False
        await ctx.send(f"🎉 Parabéns {ctx.author.mention}, você adivinhou corretamente!")
        await ctx.send(f"📍 A frase correta era **{current_quote}**.")
        await ctx.send(f"/xp add user: {ctx.author.mention} amount: 12500")
    else:
        await ctx.send(f"❌ Errado {ctx.author.mention}, tenta novamente!")

# Rodar bot
bot.run(os.environ["DISCORD_TOKEN"])
