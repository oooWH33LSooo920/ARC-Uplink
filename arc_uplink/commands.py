# commands.py
import discord
from discord.ext import commands
from arc_uplink.ui import build_expedition_embed

class ExpeditionCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild_channels = {}  # guild_id: channel_id

    @commands.command(name="expedition")
    async def expedition_command(self, ctx: commands.Context):
        embed = build_expedition_embed()
        await ctx.send(embed=embed)

    @discord.app_commands.command(name="setexpedition", description="Set this channel for expedition updates.")
    async def set_expedition_slash(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return
        guild_id = interaction.guild.id
        channel_id = interaction.channel.id
        self.guild_channels[guild_id] = channel_id
        await interaction.response.send_message(f"Expedition channel set to <#{channel_id}> for this server.", ephemeral=True)

    def get_channel_for_guild(self, guild_id):
        return self.guild_channels.get(guild_id, None)

def setup(bot: commands.Bot):
    cog = ExpeditionCommands(bot)
    bot.add_cog(cog)
    # Register slash command with the app command tree
    if hasattr(bot, 'tree'):
        bot.tree.add_command(cog.set_expedition_slash)
