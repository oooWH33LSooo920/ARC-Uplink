import discord
from discord.ext import commands
from discord import app_commands
from channel_settings import load_channels, save_channels
from updater import ExpeditionUpdater

class ExpeditionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setexpedition", description="Set this channel for ARC Expedition updates.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setexpedition(self, interaction: discord.Interaction):
        import traceback
        from bot import expedition_updaters
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id not in channels:
            channels[guild_id] = {}
        channels[guild_id]["expedition"] = interaction.channel_id
        save_channels(channels)
        await interaction.response.send_message("This channel is now set for ARC Expedition updates.")
        try:
            updater = ExpeditionUpdater(
                bot=self.bot,
                channel_id=interaction.channel_id
            )
            updater.start()
            expedition_updaters[interaction.guild.id] = updater
            print(f"[ExpeditionCog] Started ExpeditionUpdater for guild {interaction.guild.id} channel {interaction.channel_id}")
            try:
                # Immediately post the expedition embed after setting the channel
                from arc_uplink.ui import build_expedition_embed
                channel = self.bot.get_channel(interaction.channel_id)
                if channel:
                    embed = build_expedition_embed()
                    await channel.send(embed=embed)
                    print(f"[ExpeditionCog] Posted initial expedition embed for guild {interaction.guild.id} channel {interaction.channel_id}")
                else:
                    print(f"[ExpeditionCog] Channel {interaction.channel_id} not found for immediate post.")
            except Exception as e:
                print(f"[ExpeditionCog] Error posting initial expedition embed: {e}")
                traceback.print_exc()
        except Exception as e:
            print(f"[ExpeditionCog] Error starting ExpeditionUpdater: {e}")
            traceback.print_exc()

    @app_commands.command(name="expedition", description="Show the current ARC Expedition status.")
    async def expedition(self, interaction: discord.Interaction):
        from arc_uplink.expedition import get_expedition_state, progress_bar
        import arc_uplink.config as config
        state = get_expedition_state()
        now = state.window_start.tzinfo and state.window_start or None
        # Title and icon
        title = f"{state.icon} Expedition #{state.expedition_number} — "
        if state.phase == "WINDOW":
            phase_label = "Sign-Up Window"
            status = "ACTIVE"
            countdown = f"Expedition begins in {(state.expedition_start - state.window_start).days}d"
            bar, pct = progress_bar(state.window_start, state.window_end)
        elif state.phase == "EXPEDITION":
            phase_label = "Expedition Active"
            status = "ACTIVE"
            countdown = f"Expedition ends in {(state.expedition_end - state.expedition_start).days}d"
            bar, pct = progress_bar(state.expedition_start, state.expedition_end)
        else:
            phase_label = "Preparation"
            status = "INACTIVE"
            countdown = f"Window opens in {(state.window_start - state.window_start).days}d"
            bar, pct = progress_bar(state.window_start, state.window_end)

        embed = discord.Embed(
            title=f"{state.icon} Expedition #{state.expedition_number} — {phase_label}",
            color=getattr(config, "EMBED_COLOR", 0x00E5FF)
        )
        embed.set_thumbnail(url="https://i.postimg.cc/RV6vwTdW/image.webp")
        embed.add_field(
            name="🗓️ Window",
            value=f"{state.window_start:%d %b %Y} — {state.window_end:%d %b %Y}",
            inline=False
        )
        embed.add_field(
            name="🚀 Expedition",
            value=f"{state.expedition_start:%d %b %Y} — {state.expedition_end:%d %b %Y}",
            inline=False
        )
        embed.add_field(
            name="Status",
            value=status,
            inline=True
        )
        embed.add_field(
            name="Countdown",
            value=countdown,
            inline=True
        )
        embed.add_field(
            name="Progress",
            value=f"{bar} {pct}%",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ExpeditionCog(bot))
