import os
import discord
from discord.ext import commands, tasks
import requests
import random
import asyncio

# Intents para o bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Função para obter uma localização aleatória
def get_random_location():
    # Usando a API GeoDB Cities (você pode substituir por outra)
    url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
    headers = {
       "X-RapidAPI-Key": os.environ["SUA_API_KEY_AQUI"],
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }

    params = {
        "limit": "1",  # Para pegar 1 cidade aleatória
        "offset": str(random.randint(0, 1000)),  # Offset para pegar cidades aleatórias
        "types": "CITY"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    city_info = data["data"][0]
    city_name = city_info["city"]
    latitude = city_info["latitude"]
    longitude = city_info["longitude"]

    return city_name, latitude, longitude

# Variáveis para armazenar o estado atual do jogo
current_location = None
current_city = None
start_time = None

@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")

@bot.command()
async def start_game(ctx):
    global current_location, current_city, start_time

    # Pega uma localização aleatória
    current_city, lat, lon = get_random_location()

    # Envia a localização para o canal (latitude e longitude são opcional)
    await ctx.send(f"Jogo de Geo-Caching iniciado! Adivinha a cidade mais próxima deste local! \nLatitude: {lat}, Longitude: {lon}")

    # Armazena o tempo de início
    start_time = asyncio.get_event_loop().time()

    # Espera por 1 minuto para respostas
    await asyncio.sleep(60)

    # Checa se alguém adivinhou corretamente
    await ctx.send(f"O tempo acabou! A cidade correta era {current_city}.")

@bot.command()
async def guess(ctx, *, city_name):
    global current_city, start_time

    # Verifica o tempo de resposta
    elapsed_time = asyncio.get_event_loop().time() - start_time
    if elapsed_time > 60:
        await ctx.send("O tempo para adivinhar a cidade acabou.")
        return

    # Checa a resposta do usuário
    if city_name.lower() == current_city.lower():
        await ctx.send(f"Parabéns {ctx.author.mention}, você adivinhou a cidade corretamente!")
        # Aqui você pode adicionar um sistema de EXP (pontos de experiência)
        # Exemplo: user_xp[ctx.author.id] += 10
    else:
        await ctx.send(f"Desculpe {ctx.author.mention}, a cidade correta era {current_city}.")

# Rodando o bot
bot.run(os.environ["DISCORD_TOKEN"])  # Substitua com o seu token
