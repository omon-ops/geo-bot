import os
import discord
from discord.ext import commands
import requests
import random
import asyncio

# Intents para o bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Função para obter uma localização aleatória e imagem de mapa
def get_random_location():
    # API GeoDB Cities
    geo_url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
    geo_headers = {
        "X-RapidAPI-Key": os.environ["GEODB_KEY"],  # Substitua por sua variável no Railway
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

    # Gerar URL do Stamen Maps (imagem do mapa da cidade)
    stamen_url = f"https://stamen-tiles.a.ssl.fastly.net/toner-lite/{int(latitude)}/{int(longitude)}/12.png"

    return city_name, latitude, longitude, stamen_url  # Usando a URL do Stamen Maps

# Variáveis de estado do jogo
current_city = None
start_time = None

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")

@bot.command()
async def start_game(ctx):
    global current_city, start_time

    current_city, lat, lon, img_url = get_random_location()

    msg = (
        f"🧭 Jogo de Geo-Caching iniciado!\n"
        f"🌍 Latitude: {lat}, Longitude: {lon}\n"
        f"🕐 Tens 60 segundos para adivinhar a cidade!"
    )
    await ctx.send(msg)

    if img_url:
        await ctx.send(img_url)
    else:
        await ctx.send("⚠️ Não foi possível carregar uma imagem de rua para este local.")

    start_time = asyncio.get_event_loop().time()
    await asyncio.sleep(60)
    await ctx.send(f"⏰ Tempo esgotado! A cidade correta era **{current_city}**.")

@bot.command()
async def guess(ctx, *, city_name):
    global current_city, start_time

    if start_time is None:
        await ctx.send("❌ Nenhum jogo em andamento.")
        return

    elapsed_time = asyncio.get_event_loop().time() - start_time
    if elapsed_time > 60:
        await ctx.send("⏳ O tempo para adivinhar já acabou.")
        return

    # Comparar a cidade fornecida com a cidade correta
    if city_name.strip().lower() == current_city.lower():
        await ctx.send(f"🎉 Parabéns {ctx.author.mention}, você adivinhou corretamente! A cidade é **{current_city}**.")
    else:
        await ctx.send(f"❌ Errado {ctx.author.mention}, a cidade correta era **{current_city}**.")

# Rodando o bot
bot.run(os.environ["DISCORD_TOKEN"])
