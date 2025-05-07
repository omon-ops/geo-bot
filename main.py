import os
import discord
from discord.ext import commands
import requests
import random
import asyncio
import unicodedata

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Normaliza nomes para comparação
def normalize_text(text):
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii').strip().lower()

# Gera cidade aleatória
def get_random_location():
    geo_url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
    geo_headers = {
        "X-RapidAPI-Key": os.environ["GEODB_KEY"],
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }
    geo_params = {
        "limit": "1",
        "offset": str(random.randint(0, 1000)),
        "types": "CITY"
    }

    geo_response = requests.get(geo_url, headers=geo_headers, params=geo_params)
    geo_data = geo_response.json()
    city_info = geo_data["data"][0]
    city_name = city_info["city"]
    latitude = city_info["latitude"]
    longitude = city_info["longitude"]

    return city_name, latitude, longitude

# Estado do jogo
current_city = None
start_time = None
game_active = False
winner_found = False

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")

@bot.command()
async def start_game(ctx):
    global current_city, start_time, game_active, winner_found

    if game_active:
        await ctx.send("⚠️ Já existe um jogo em andamento!")
        return

    current_city, lat, lon = get_random_location()
    game_active = True
    winner_found = False

    await ctx.send(
        f"🧭 Jogo de Geo-Caching iniciado!\n"
        f"🌍 Latitude: {lat}, Longitude: {lon}\n"
        f"🕐 Tens 60 segundos para adivinhar a cidade!"
    )

    start_time = asyncio.get_event_loop().time()
    await asyncio.sleep(60)

    if not winner_found:
        await ctx.send("⏰ Tempo esgotado! Ninguém acertou desta vez.")
    game_active = False

@bot.command()
async def guess(ctx, *, city_name):
    global current_city, start_time, game_active, winner_found

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

    if normalize_text(city_name) == normalize_text(current_city):
        winner_found = True
        game_active = False
        await ctx.send(f"🎉 Parabéns {ctx.author.mention}, você adivinhou corretamente!")
        await ctx.send(f"📍 A cidade correta era **{current_city}**.")
        await ctx.send(f"/xp add user: {ctx.author.mention} amount: 12500")
    else:
        await ctx.send(f"❌ Errado {ctx.author.mention}, tenta novamente!")

# Rodar bot
bot.run(os.environ["DISCORD_TOKEN"])
