
import discord
from discord.ext import commands, tasks
from discord import app_commands
import requests
import os
from dotenv import load_dotenv
from updater import StaticMessageUpdater, WeeklyTrialsUpdater, LiveEventsUpdater, ExpeditionUpdater
from channel_settings import load_channels, save_channels
from channel_settings_db import ChannelSettingsDB
import asyncio
import subprocess
import sys






# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class ARCClient(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.synced = False

bot = ARCClient(command_prefix='!', intents=intents)
bot.remove_command('help')

# --- Slash Command: showcommands ---
@bot.tree.command(name="showcommands", description="Show all available slash commands.")
async def showcommands(interaction: discord.Interaction):
    cmds = bot.tree.get_commands()
    help_text = "Available slash commands:\n" + "\n".join(f"- /{cmd.name}: {cmd.description}" for cmd in cmds)
    await interaction.response.send_message(help_text, ephemeral=True)













    channels = load_channels()
    guild_id = str(interaction.guild.id)
    if guild_id in channels and "static_message" in channels[guild_id]:
        del channels[guild_id]["static_message"]
        save_channels(channels)
        await interaction.response.send_message("ARC Static Message channel unset for this server.", ephemeral=True)
        updater = arc_map_event_updaters.get(interaction.guild.id)
        if updater:
            try:
                updater.task.cancel()
            except Exception:
                pass
            del arc_map_event_updaters[interaction.guild.id]
    else:
        await interaction.response.send_message("No ARC Static Message channel is set for this server.", ephemeral=True)


# Intents must be defined before bot initialization
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class ARCClient(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.synced = False

bot = ARCClient(command_prefix='!', intents=intents)

# Remove the default help command to avoid conflicts
bot.remove_command('help')



# --- Updater Dictionaries ---
channels = load_channels()
arc_map_event_updaters = {}
weekly_trials_updaters = {}
live_events_updaters = {}
expedition_updaters = {}


bot = ARCClient(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user} (slash commands synced)')

    # Auto-start updaters for all configured channels
    channels = load_channels()
    for guild_id, ch in channels.items():
        # Live Events
        if "map_events" in ch:
            if int(guild_id) not in live_events_updaters:
                updater = LiveEventsUpdater(
                    bot=bot,
                    channel_id=ch["map_events"],
                    guild_id=int(guild_id)
                )
                updater.start()
                live_events_updaters[int(guild_id)] = updater
        # Weekly Trials
        if "weekly_trials" in ch:
            if int(guild_id) not in weekly_trials_updaters:
                updater = WeeklyTrialsUpdater(
                    bot=bot,
                    channel_id=ch["weekly_trials"],
                    guild_id=int(guild_id)
                )
                updater.start()
                weekly_trials_updaters[int(guild_id)] = updater
        # Expedition
        if "expedition" in ch:
            if int(guild_id) not in expedition_updaters:
                updater = ExpeditionUpdater(
                    bot=bot,
                    channel_id=ch["expedition"],
                    guild_id=int(guild_id)
                )
                updater.start()
                expedition_updaters[int(guild_id)] = updater
        # Static Message
        if "static_message" in ch:
            if int(guild_id) not in arc_map_event_updaters:
                updater = StaticMessageUpdater(
                    bot=bot,
                    channel_id=ch["static_message"],
                    guild_id=int(guild_id)
                )
                updater.start()
                arc_map_event_updaters[int(guild_id)] = updater

@bot.command()
async def version(ctx):
    """Get ARC Raiders API version info."""
    url = 'https://arctracker.io/api/version'


# --- Slash Command: setliveevents ---
@bot.tree.command(name="setliveevents", description="Set this channel for ARC Live Events updates.")
@app_commands.checks.has_permissions(administrator=True)
async def setliveevents(interaction: discord.Interaction):
    channels = load_channels()
    guild_id = str(interaction.guild.id)
    if guild_id not in channels:
        channels[guild_id] = {}
    channels[guild_id]["map_events"] = interaction.channel_id
    save_channels(channels)
    await interaction.response.send_message("This channel is now set for ARC Live Events updates.", ephemeral=True)
    # Start or update the live events updater for this guild

    updater = LiveEventsUpdater(
        bot=bot,
        channel_id=interaction.channel_id,
        guild_id=interaction.guild.id
    )
    updater.start()
    live_events_updaters[interaction.guild.id] = updater

@bot.tree.command(name="help", description="Show all available bot commands.")
async def help_slash(interaction: discord.Interaction):
    prefix = bot.command_prefix
    user_prefix_cmds = [cmd for cmd in bot.commands if cmd.enabled and cmd.name not in ["unlink", "relink"]]
    prefix_cmds = [f"{prefix}{cmd.name}" for cmd in user_prefix_cmds]
    user_slash_cmds = [cmd for cmd in bot.tree.get_commands() if cmd.name not in ["unlink", "relink"]]
    slash_cmds = [f"/{cmd.name}" for cmd in user_slash_cmds]
    help_text = "Available commands:\n" + \
        ("Prefix commands:\n" + "\n".join(f"- {name}" for name in prefix_cmds) + "\n\n" if prefix_cmds else "") + \
        ("Slash commands:\n" + "\n".join(f"- {name}" for name in slash_cmds) if slash_cmds else "")
    await interaction.response.send_message(help_text, ephemeral=True)

async def load_cogs():
    import importlib.util
    import pathlib
    bot.db = ChannelSettingsDB()
    cogs_loaded = 0
    base_path = pathlib.Path(__file__).parent / "modules"
    # Only load files ending with _cog.py as cogs
    for py_file in base_path.rglob("*_cog.py"):
        if "__pycache__" in py_file.parts:
            continue
        rel_path = py_file.relative_to(pathlib.Path(__file__).parent)
        module = str(rel_path.with_suffix("")).replace("/", ".")
        try:
            await bot.load_extension(module)
            print(f"Loaded cog: {module}")
            cogs_loaded += 1
        except Exception as e:
            print(f"Failed to load cog {module}: {e}")
    # Load any top-level cogs (e.g. welcome_handler.py)
    for py_file in pathlib.Path(__file__).parent.glob("*.py"):
        if py_file.name.endswith("_handler.py"):
            module = py_file.stem
            try:
                await bot.load_extension(module)
                print(f"Loaded cog: {module}")
                cogs_loaded += 1
            except Exception as e:
                print(f"Failed to load cog {module}: {e}")
    print(f"Total cogs loaded: {cogs_loaded}")

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print('Please set the DISCORD_BOT_TOKEN environment variable.')
    else:
        async def main():
            await load_cogs()
            await bot.start(TOKEN)
        asyncio.run(main())





































































































