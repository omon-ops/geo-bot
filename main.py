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

# Função para obter uma localização aleatória e imagem de rua
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

    # API Mapillary para imagem
    mapillary_token = os.environ["MAPILLARY_TOKEN"]
    mapillary_url = (
        f"https://graph.mapillary.com/images"
        f"?access_token={mapillary_token}"
        f"&fields=thumb_2048_url"
        f"&closeto={longitude},{latitude}"
        f"&limit=1"
    )

    image_response = requests.get(mapillary_url)
    image_data = image_response.json()

    # Verificar se a resposta contém imagens
    if "data" in image_data and len(image_data["data"]) > 0:
        image_url = image_data["data"][0].get("thumb_2048_url")
    else:
        image_url = None  # Se não houver imagem, atribuir None

    return city_name, latitude, longitude, image_url

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

    if city_name.strip().lower() == current_city.lower():
        await ctx.send(f"🎉 Parabéns {ctx.author.mention}, você adivinhou corretamente!")
    else:
        await ctx.send(f"❌ Errado {ctx.author.mention}, a cidade correta era **{current_city}**.")

# Rodando o bot
bot.run(os.environ["DISCORD_TOKEN"])
