from channel_settings_db import ChannelSettingsDB
import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
from dotenv import load_dotenv
from updater import StaticMessageUpdater, WeeklyRotationUpdater, LiveEventsUpdater, ExpeditionUpdater
from channel_settings import load_channels, save_channels
import asyncio
import subprocess
import sys
from discord.ext import tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # Loaded from .env

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def version(ctx):
    """Get ARC Raiders API version info."""
    url = 'https://arctracker.io/api/version'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        await ctx.send(f"ARC API Version: {data}")
    except Exception as e:
        await ctx.send(f"Error fetching version: {e}")

# Add more commands here for other endpoints


# --- Static Message Updater ---
channels = load_channels()
arc_map_event_updaters = {}
weekly_rotation_updaters = {}
live_events_updaters = {}
expedition_updaters = {}

# --- Self-update Command ---
@bot.command()
@commands.is_owner()
async def selfupdate(ctx):
    """Pull latest code from git and restart the bot."""
    await ctx.send("Updating bot from git and restarting...")
    try:
        subprocess.check_call(['git', 'pull'])
        await ctx.send("Update complete. Restarting...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        await ctx.send(f"Update failed: {e}")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    global arc_map_event_updater
    global weekly_rotation_updater
    # Sync slash commands once per session
    if not bot.synced:
        await bot.tree.sync()
        bot.synced = True
        print("Slash commands synced.")
    # For each guild, start updaters if a channel is set
    for guild in bot.guilds:
        guild_channels = channels.get(str(guild.id), {})
        # Map Events Updater (legacy/static)
        map_events_channel = guild_channels.get("map_events")
        if map_events_channel:
            # Stop any existing updater for this guild
            if guild.id in live_events_updaters:
                try:
                    live_events_updaters[guild.id].task.cancel()
                except Exception:
                    pass
            updater = LiveEventsUpdater(
                bot=bot,
                channel_id=int(map_events_channel),
                guild_id=guild.id,
                interval=60
            )
            updater.start()
            live_events_updaters[guild.id] = updater
        # Weekly Trials Updater
        weekly_trials_channel = guild_channels.get("weekly_trials")
        if weekly_trials_channel:
            # Stop any existing updater for this guild
            if guild.id in weekly_rotation_updaters:
                try:
                    weekly_rotation_updaters[guild.id].task.cancel()
                except Exception:
                    pass
            updater = WeeklyRotationUpdater(
                bot=bot,
                channel_id=int(weekly_trials_channel),
                label="ARC Weekly Trials",
                reset_hour=10,
                reset_minute=0,
                reset_weekday=0  # Monday
            )
            updater.start()
            weekly_rotation_updaters[guild.id] = updater
        # Expedition Updater
        expedition_channel = guild_channels.get("expedition")
        expedition_message_id = guild_channels.get("expedition_message_id")
        if expedition_channel and expedition_message_id:
            # Stop any existing updater for this guild
            if guild.id in expedition_updaters:
                try:
                    expedition_updaters[guild.id].task.cancel()
                except Exception:
                    pass
            updater = ExpeditionUpdater(
                bot=bot,
                channel_id=int(expedition_channel),
                message_id=int(expedition_message_id)
            )
            updater.start()
            expedition_updaters[guild.id] = updater
        if not map_events_channel and not weekly_trials_channel and not expedition_channel:
            print(f'No update channels set for guild {guild.name} ({guild.id})')





# --- Slash Command: setweeklytrials ---
@bot.tree.command(name="setweeklytrials", description="Set this channel for ARC Weekly Trials rotation updates.")
@app_commands.checks.has_permissions(administrator=True)
async def setweeklytrials(interaction: discord.Interaction):
    channels = load_channels()
    guild_id = str(interaction.guild.id)
    if guild_id not in channels:
        channels[guild_id] = {}
    channels[guild_id]["weekly_trials"] = interaction.channel_id
    save_channels(channels)
    await interaction.response.send_message("This channel is now set for ARC Weekly Trials rotation updates.", ephemeral=True)
    # Start or update the weekly trials updater for this guild
    updater = WeeklyRotationUpdater(
        bot=bot,
        channel_id=interaction.channel_id,
        label="ARC Weekly Trials",
        reset_hour=10,
        reset_minute=0,
        reset_weekday=0  # Monday
    )
    updater.start()
    weekly_rotation_updaters[interaction.guild.id] = updater

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
        guild_id=interaction.guild.id,
        interval=60
    )
    updater.start()
    live_events_updaters[interaction.guild.id] = updater

# --- Slash Command: setexpedition ---
@bot.tree.command(name="setexpedition", description="Set this channel for ARC Expedition progress updates.")
@app_commands.checks.has_permissions(administrator=True)
async def setexpedition(interaction: discord.Interaction):
    await interaction.response.send_message("Setting up ARC Expedition progress panel...", ephemeral=True)
    try:
        from arc_uplink.ui import build_expedition_embed
        from channel_settings import load_channels, save_channels
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id not in channels:
            channels[guild_id] = {}
        # Send the embed and save the message ID
        embed = build_expedition_embed()
        sent = await interaction.channel.send(embed=embed)
        channels[guild_id]["expedition"] = interaction.channel_id
        channels[guild_id]["expedition_message_id"] = sent.id
        save_channels(channels)
        # Start or update the expedition updater for this guild
        if interaction.guild.id in expedition_updaters:
            try:
                expedition_updaters[interaction.guild.id].task.cancel()
            except Exception:
                pass
        updater = ExpeditionUpdater(
            bot=bot,
            channel_id=interaction.channel_id,
            message_id=sent.id
        )
        updater.start()
        expedition_updaters[interaction.guild.id] = updater
    except Exception as e:
        print(f"Error in /setexpedition: {e}")
        # Optionally, send a followup error message
        try:
            await interaction.followup.send(f"Error setting up expedition panel: {e}", ephemeral=True)
        except Exception:
            pass


# --- Unlink Command ---
@bot.command()
@commands.has_permissions(administrator=True)
async def unlink(ctx, command_name: str):
    """Disable a command by name (prefix or slash)."""
    command = bot.get_command(command_name)
    if command:
        command.enabled = False
        await ctx.send(f"Command '{command_name}' has been disabled.")
    else:
        # Try disabling a slash command
        try:
            bot.tree.remove_command(command_name)
            await ctx.send(f"Slash command '{command_name}' has been disabled.")
        except Exception:
            await ctx.send(f"Command '{command_name}' not found.")

@bot.command()
@commands.has_permissions(administrator=True)
async def relink(ctx, command_name: str):
    """Re-enable a previously disabled command by name."""
    command = bot.get_command(command_name)
    if command:
        command.enabled = True
        await ctx.send(f"Command '{command_name}' has been re-enabled.")
    else:
        await ctx.send(f"Command '{command_name}' not found or is a slash command.")

@bot.tree.command(name="unlink", description="Disable a command by name (admin only)")
@app_commands.describe(command_name="Name of the command to disable")
@app_commands.checks.has_permissions(administrator=True)
async def unlink_slash(interaction: discord.Interaction, command_name: str):
    command = bot.get_command(command_name)
    if command:
        command.enabled = False
        await interaction.response.send_message(f"Command '{command_name}' has been disabled.", ephemeral=True)
    else:
        try:
            bot.tree.remove_command(command_name)
            await interaction.response.send_message(f"Slash command '{command_name}' has been disabled.", ephemeral=True)
        except Exception:
            await interaction.response.send_message(f"Command '{command_name}' not found.", ephemeral=True)

@bot.tree.command(name="relink", description="Re-enable a previously disabled command (admin only)")
@app_commands.describe(command_name="Name of the command to re-enable")
@app_commands.checks.has_permissions(administrator=True)
async def relink_slash(interaction: discord.Interaction, command_name: str):
    command = bot.get_command(command_name)
    if command:
        command.enabled = True
        await interaction.response.send_message(f"Command '{command_name}' has been re-enabled.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Command '{command_name}' not found or is a slash command.", ephemeral=True)

@bot.command()
async def prefix(ctx):
    """Show the current bot command prefix."""
    await ctx.send(f"The current bot prefix is: '{bot.command_prefix}'")

@bot.tree.command(name="prefix", description="Show the current bot command prefix.")
async def prefix_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f"The current bot prefix is: '{bot.command_prefix}'", ephemeral=True)

@bot.command()
async def help(ctx):
    """Show all available bot commands with invocation style."""
    prefix = bot.command_prefix
    # Only show user-facing commands
    user_prefix_cmds = [cmd for cmd in bot.commands if cmd.enabled and cmd.name not in ["unlink", "relink"]]
    prefix_cmds = [f"{prefix}{cmd.name}" for cmd in user_prefix_cmds]
    # Only show user-facing slash commands
    user_slash_cmds = [cmd for cmd in bot.tree.get_commands() if cmd.name not in ["unlink", "relink"]]
    slash_cmds = [f"/{cmd.name}" for cmd in user_slash_cmds]
    help_text = "Available commands:\n" + \
        ("Prefix commands:\n" + "\n".join(f"- {name}" for name in prefix_cmds) + "\n\n" if prefix_cmds else "") + \
        ("Slash commands:\n" + "\n".join(f"- {name}" for name in slash_cmds) if slash_cmds else "")
    await ctx.send(help_text)

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
    if not TOKEN:
        print('Please set the DISCORD_BOT_TOKEN environment variable.')
    else:
        async def main():
            await load_cogs()
            await bot.start(TOKEN)
        asyncio.run(main())





































































































