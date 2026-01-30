
import discord
from discord.ext import commands
from discord import app_commands
import json

with open("modules/maps/map_data.json", "r", encoding="utf-8") as f:
    MAPS = json.load(f)

class MapsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="map", description="Show ARC Raiders maps and get info or a preview.")
    @app_commands.describe(map_name="Name of the map to preview (optional)")
    async def map(self, interaction: discord.Interaction, map_name: str = None):
        if not map_name:
            maps_list = "\n".join(f"• {m['name']}" for m in MAPS)
            embed = discord.Embed(
                title="ARC Raiders Maps",
                description=f"Available maps:\n{maps_list}\n\nUse `/map <map name>` to get a preview and info.",
                color=0x00BFFF
            )
            await interaction.response.send_message(embed=embed)
            return
        # Find the map
        m = next((m for m in MAPS if map_name.lower() in m["name"].lower()), None)
        if not m:
            await interaction.response.send_message("Map not found. Please check the name and try again.", ephemeral=True)
            return
        embed = discord.Embed(
            title=m["name"],
            description=f"[View on ARCTracker]({m['url']})",
            color=0x00BFFF
        )
        embed.set_image(url=m["image"])
        # Add points of interest
        if m.get("points_of_interest"):
            pois = "\n".join(f"• {poi}" for poi in m["points_of_interest"])
            embed.add_field(name="Points of Interest", value=pois, inline=False)
        # Add events
        if m.get("events"):
            events = "\n".join(f"• {event}" for event in m["events"])
            embed.add_field(name="Events", value=events, inline=False)
        # Add keys
        if m.get("keys"):
            keys = "\n".join(f"• {key}" for key in m["keys"])
            embed.add_field(name="Keys", value=keys, inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MapsCog(bot))
