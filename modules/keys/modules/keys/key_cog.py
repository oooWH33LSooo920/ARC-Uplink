import json
import discord
from discord import app_commands
from discord.ext import commands

KEYS_PATH = "modules/keys/keys.json"

LOOT_TIER_COLORS = {
    1: 0x9E9E9E,  # grey
    2: 0x4CAF50,  # green
    3: 0x2196F3,  # blue
    4: 0x9C27B0,  # purple
    5: 0xFFC107   # gold
}

DANGER_COLORS = {
    "Low": 0x4CAF50,
    "Medium": 0x2196F3,
    "High": 0xFF9800,
    "Extreme": 0xF44336
}

class KeyLookup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open(KEYS_PATH, "r", encoding="utf-8") as f:
            self.keys = json.load(f)

    def get_key_names(self):
        return list(self.keys.keys())

    def build_embed(self, key_name: str, data: dict) -> discord.Embed:
        loot_tier = data.get("lootTier", 0)
        danger = data.get("danger", "Unknown")

        base_color = LOOT_TIER_COLORS.get(loot_tier, 0x00AEEF)
        danger_color = DANGER_COLORS.get(danger, base_color)
        color = danger_color or base_color

        embed = discord.Embed(
            title=key_name,
            description=f"Unlocks a location in **{data.get('map', 'Unknown Map')}**",
            color=color
        )

        embed.add_field(
            name="Building / Area",
            value=data.get("building", "Unknown"),
            inline=True
        )
        embed.add_field(
            name="Floor / Level",
            value=data.get("floor", "Unknown"),
            inline=True
        )

        coords = data.get("coordinates")
        if coords and isinstance(coords, (list, tuple)) and len(coords) == 2:
            embed.add_field(
                name="Map Coordinates",
                value=f"X: `{coords[0]:.1f}`  |  Y: `{coords[1]:.1f}`\n*(Matches ARCTracker map)*",
                inline=False
            )

        loot_list = data.get("loot", [])
        if loot_list:
            loot_str = "\n".join(f"• {item}" for item in loot_list)
            embed.add_field(
                name=f"Loot (Tier {loot_tier})",
                value=loot_str,
                inline=False
            )

        danger_display = danger if danger != "Unknown" else "Not rated"
        embed.add_field(
            name="Danger",
            value=danger_display,
            inline=True
        )

        route = data.get("recommendedRoute")
        if route:
            embed.add_field(
                name="Recommended Route",
                value=route,
                inline=False
            )

        notes = data.get("notes")
        if notes:
            embed.add_field(
                name="Notes",
                value=notes,
                inline=False
            )

        return embed

    @app_commands.command(
        name="key",
        description="Look up what an ARC Raiders key unlocks."
    )
    @app_commands.describe(name="The exact name of the key you found")
    async def key_lookup(self, interaction: discord.Interaction, name: str):
        key_data = self.keys.get(name)
        if not key_data:
            await interaction.response.send_message(
                f"I couldn't find **{name}** in the key database.",
                ephemeral=True
            )
            return

        embed = self.build_embed(name, key_data)
        await interaction.response.send_message(embed=embed)

    @key_lookup.autocomplete("name")
    async def key_name_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        names = self.get_key_names()
        current_lower = current.lower()

        matches = [
            app_commands.Choice(name=n, value=n)
            for n in names
            if current_lower in n.lower()
        ][:25]

        return matches

async def setup(bot: commands.Bot):
    await bot.add_cog(KeyLookup(bot))
