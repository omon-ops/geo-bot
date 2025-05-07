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

# Função para obter a imagem de rua e cidade mais próxima usando Mapillary
def get_random_street_image():
    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)

    # Mapillary API para obter imagem de rua
    mapillary_token = os.environ["MAPILLARY_TOKEN"]
    mapillary_url = (
        f"https://graph.mapillary.com/images"
        f"?access_token={mapillary_token}"
        f"&fields=thumb_2048_url"
        f"&closeto={longitude},{latitude}"
        f"&limit=1"
    )

    # Obter a imagem de rua mais próxima
    image_response = requests.get(mapillary_url)
    image_data = image_response.json()

    image_url = (
        image_data["data"][0].get("thumb_2048_url")
        if "data" in image_data and len(image_data["data"]) > 0
        else None
    )

    city_name = "Cidade Aleatória"  # Nome fictício da cidade. Você pode substituir com uma API real.

    return city_name, image_url

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

    # Debug: Verificar se o comando chegou aqui
    print("Comando start_game foi chamado!")

    current_city, img_url = get_random_street_image()
    game_active = True
    winner_found = False

    await ctx.send(
        f"🧭 Jogo de Geo-Caching iniciado!\n"
        f"🕐 Tens 60 segundos para adivinhar a cidade com base na imagem!"
    )

    if img_url:
        await ctx.send(img_url)  # Envia a imagem de rua
    else:
        await ctx.send("⚠️ Não foi possível carregar uma imagem de rua para este local.")

    start_time = asyncio.get_event_loop().time()
    await asyncio.sleep(60)

    if not winner_found:
        await ctx.send(f"⏰ Tempo esgotado! Ninguém acertou desta vez. A cidade correta era **{current_city}**.")
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

    if city_name.strip().lower() == current_city.lower():
        winner_found = True
        game_active = False
        await ctx.send(f"🎉 Parabéns {ctx.author.mention}, você adivinhou corretamente!")
        await ctx.send(f"📍 A cidade correta era **{current_city}**.")
        await ctx.send(f"/xp add user: {ctx.author.mention} amount: 12500")
    else:
        await ctx.send(f"❌ Errado {ctx.author.mention}, tenta novamente!")

# Rodar bot
bot.run(os.environ["DISCORD_TOKEN"])
