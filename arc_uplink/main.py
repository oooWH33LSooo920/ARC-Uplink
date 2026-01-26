# main.py
import discord
from discord.ext import commands
from updater import ExpeditionUpdater
import arc_uplink.commands as expedition_commands
import arc_uplink.config as config

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def setup_hook():
    expedition_commands.setup(bot)
    # Start updater after setup
    updater = ExpeditionUpdater(bot)
    updater.start()

bot.run("YOUR_BOT_TOKEN")
