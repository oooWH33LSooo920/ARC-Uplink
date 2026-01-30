import discord
from discord.ext import commands
from discord import app_commands
from channel_settings import load_channels, save_channels

class QuestsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setquests", description="Set this channel for ARC Quests updates.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setquests(self, interaction: discord.Interaction):
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id not in channels:
            channels[guild_id] = {}
        channels[guild_id]["quests"] = interaction.channel_id
        save_channels(channels)
        await interaction.response.send_message("This channel is now set for ARC Quests updates.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QuestsCog(bot))
