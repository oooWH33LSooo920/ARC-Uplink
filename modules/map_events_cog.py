import discord
from discord.ext import commands
from discord import app_commands
import requests

API_URL = "https://arctracker.io/api/map-events"

class MapEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="map-events", description="Show current ARC map events.")
    async def map_events(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        try:
            resp = requests.get(API_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not data or not isinstance(data, list):
                await interaction.followup.send("No map events found.")
                return
            embed = discord.Embed(title="Current ARC Map Events", color=0x00AEEF)
            for event in data:
                name = event.get("name", "Unknown Event")
                location = event.get("location", "Unknown Location")
                start = event.get("startTime", "?")
                end = event.get("endTime", "?")
                desc = event.get("description", "")
                embed.add_field(
                    name=f"{name} @ {location}",
                    value=f"Start: {start}\nEnd: {end}\n{desc}",
                    inline=False
                )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Error fetching map events: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(MapEvents(bot))
