import discord
from discord.ext import commands
from discord import app_commands
from channel_settings import load_channels, save_channels


class UnsetChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unsetwelcome", description="Unset the ARC Welcome channel for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def unsetwelcome(self, interaction: discord.Interaction):
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id in channels and "welcome" in channels[guild_id]:
            del channels[guild_id]["welcome"]
            save_channels(channels)
            await interaction.response.send_message("ARC Welcome channel unset for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("No ARC Welcome channel is set for this server.", ephemeral=True)

    @app_commands.command(name="unsetquests", description="Unset the ARC Quests channel for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def unsetquests(self, interaction: discord.Interaction):
        from bot import quests_updaters
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id in channels and "quests" in channels[guild_id]:
            del channels[guild_id]["quests"]
            save_channels(channels)
            updater = quests_updaters.get(interaction.guild.id)
            if updater:
                try:
                    updater.task.cancel()
                except Exception:
                    pass
                del quests_updaters[interaction.guild.id]
            await interaction.response.send_message("ARC Quests channel unset for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("No ARC Quests channel is set for this server.", ephemeral=True)

    @app_commands.command(name="unsetexpedition", description="Unset the ARC Expedition channel for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def unsetexpedition(self, interaction: discord.Interaction):
        from bot import expedition_updaters
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id in channels and "expedition" in channels[guild_id]:
            del channels[guild_id]["expedition"]
            save_channels(channels)
            updater = expedition_updaters.get(interaction.guild.id)
            if updater:
                try:
                    updater.task.cancel()
                except Exception:
                    pass
                del expedition_updaters[interaction.guild.id]
            await interaction.response.send_message("ARC Expedition channel unset for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("No ARC Expedition channel is set for this server.", ephemeral=True)

    @app_commands.command(name="unsetliveevents", description="Unset the ARC Live Events channel for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def unsetliveevents(self, interaction: discord.Interaction):
        from bot import live_events_updaters
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id in channels and "map_events" in channels[guild_id]:
            del channels[guild_id]["map_events"]
            save_channels(channels)
            updater = live_events_updaters.get(interaction.guild.id)
            if updater:
                try:
                    updater.task.cancel()
                except Exception:
                    pass
                del live_events_updaters[interaction.guild.id]
            await interaction.response.send_message("ARC Live Events channel unset for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("No ARC Live Events channel is set for this server.", ephemeral=True)

    @app_commands.command(name="unsetstaticmessage", description="Unset the ARC Static Message channel for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def unsetstaticmessage(self, interaction: discord.Interaction):
        from bot import arc_map_event_updaters
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id in channels and "static_message" in channels[guild_id]:
            del channels[guild_id]["static_message"]
            save_channels(channels)
            updater = arc_map_event_updaters.get(interaction.guild.id)
            if updater:
                try:
                    updater.task.cancel()
                except Exception:
                    pass
                del arc_map_event_updaters[interaction.guild.id]
            await interaction.response.send_message("ARC Static Message channel unset for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("No ARC Static Message channel is set for this server.", ephemeral=True)

    @app_commands.command(name="unsetweeklytrials", description="Unset the ARC Weekly Trials channel for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def unsetweeklytrials(self, interaction: discord.Interaction):
        from bot import weekly_trials_updaters
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id in channels and "weekly_trials" in channels[guild_id]:
            del channels[guild_id]["weekly_trials"]
            save_channels(channels)
            updater = weekly_trials_updaters.get(interaction.guild.id)
            if updater:
                try:
                    updater.task.cancel()
                except Exception:
                    pass
                del weekly_trials_updaters[interaction.guild.id]
            await interaction.response.send_message("ARC Weekly Trials channel unset for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("No ARC Weekly Trials channel is set for this server.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnsetChannels(bot))
