import os
import discord
from discord.ext import commands
import requests
import random
import asyncio
from bs4 import BeautifulSoup
from discord.ui import View, Button

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

AGENTS = [
    "Brimstone", "Phoenix", "Sage", "Sova", "Viper", "Cypher", "Reyna", "Killjoy", "Breach", "Omen",
    "Jett", "Raze", "Skye", "Yoru", "Astra", "KAY/O", "Chamber", "Neon", "Fade", "Harbor",
    "Gekko", "Deadlock", "Iso", "Clove", "Vyse", "Tejo", "Waylay"
]

def get_random_quote():
    agent = random.choice(AGENTS)
    url_agent = "KAYO" if agent == "KAY/O" else agent.replace("/", "%2F")
    url = f"https://valorant.fandom.com/wiki/{url_agent}/Quotes"

    response = requests.get(url)
    if response.status_code != 200:
        return None, None

    soup = BeautifulSoup(response.content, 'html.parser')
    quotes = []

    # Pega todas as frases em <ul><li> e filtra apenas as que são frases
    for li in soup.select("ul > li"):
        # Remove qualquer tag dentro do <li>, como <span>, mantendo somente o texto
        text = li.get_text(strip=True)

        # Filtra as frases que não contêm links (ou outras informações extras)
        if 20 < len(text) < 200 and "http" not in text and "www" not in text:
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

# Botão de XP
class XPButtonView(View):
    def __init__(self, winner):
        super().__init__(timeout=60)
        self.winner = winner

    @discord.ui.button(label="💸 Reivindicar XP", style=discord.ButtonStyle.green)
    async def claim_xp(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.winner:
            await interaction.response.send_message("❌ Apenas o vencedor pode clicar.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ Usa este comando para receber a recompensa (precisa permissão):\n"
            f"`/xp add user: {self.winner.mention} amount: 12500`", ephemeral=True
        )

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
        view = XPButtonView(ctx.author)
        await ctx.send("🔘 Clica no botão abaixo para reivindicar XP:", view=view)
    else:
        await ctx.send(f"❌ Errado, {ctx.author.mention}. Tenta outra vez!")

# Rodar bot
bot.run(os.environ["DISCORD_TOKEN"])
