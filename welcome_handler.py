import discord
from discord.ext import commands
from discord import app_commands
import random


class WelcomeHandler(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @app_commands.command(name="testwelcome", description="Test the ARC welcome message in the configured channel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def test_welcome_message(self, interaction: discord.Interaction):
        """Send a test welcome message as if a new member joined."""
        channel_id = await self.db.get(f"{interaction.guild.id}.welcomeChannel")
        if not channel_id:
            await interaction.response.send_message("No welcome channel set. Use /setwelcome first.", ephemeral=True)
            return
        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message("Configured welcome channel not found.", ephemeral=True)
            return
        # Use the command invoker as the 'member' for testing
        member = interaction.user
        message = (
            "🗲 ARC Uplink Transmission\n"
            "═══════════════════════════════\n\n"
            f"Identity confirmed: {member.mention}\n\n"
            "Signal lock stable.\n"
            "Relay sync complete.\n\n"
            "Glad to have you linked in — settle in and enjoy your stay.\n\n"
            "═══════════════════════════════"
        )
        embed = discord.Embed(
            title=None,
            description=message,
            color=0x00A3FF
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="ARC Network Node Online")
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Test welcome message sent to {channel.mention}.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel_id = await self.db.get(f"{member.guild.id}.welcomeChannel")
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return
        message = (
            "🗲 ARC Uplink Transmission\n"
            "═══════════════════════════════\n\n"
            f"Identity confirmed: {member.mention}\n\n"
            "Signal lock stable.\n"
            "Relay sync complete.\n\n"
            "Glad to have you linked in — settle in and enjoy your stay.\n\n"
            "═══════════════════════════════"
        )
        embed = discord.Embed(
            title=None,
            description=message,
            color=0x00A3FF
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="ARC Network Node Online")
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

    @app_commands.command(name="setwelcome", description="Set this channel for ARC welcome messages.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """Set the welcome channel for this server."""
        if channel is None:
            channel = interaction.channel
        await self.db.set(f"{interaction.guild.id}.welcomeChannel", channel.id)
        await interaction.response.send_message(f"Welcome channel set to {channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WelcomeHandler(bot, bot.db))
