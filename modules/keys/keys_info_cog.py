import discord
import json
from discord.ext import commands
from discord import app_commands

class KeysCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("arc_keys.json", "r", encoding="utf-8") as f:
            self.keys = json.load(f)

    def build_key_embed(self, key):
        desc = key.get("description", "No information available for this key yet.")
        embed = discord.Embed(
            title=key["name"],
            description=desc,
            color=0xFFD700
        )
        # Add rewards/loot if present
        if key.get("loot"):
            embed.add_field(name="Rewards / Loot", value=key["loot"], inline=False)
        embed.set_footer(text="ARC Raiders Key Info")
        return embed

    @app_commands.command(name="keyinfo", description="Show info for a specific ARC Raiders key.")
    @app_commands.describe(key_name="Name of the key to look up")
    async def keyinfo(self, interaction: discord.Interaction, key_name: str):
        key = next((k for k in self.keys if key_name.lower() in k["name"].lower()), None)
        if key:
            await interaction.response.send_message(embed=self.build_key_embed(key))
        else:
            await interaction.response.send_message("Key not found. Please check the name and try again.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(KeysCog(bot))
