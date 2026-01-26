# ui.py
import discord

from arc_uplink.expedition import get_expedition_state, progress_bar
from arc_uplink.utils.time_utils import now_utc
import arc_uplink.config as config
from datetime import timedelta

def format_timedelta(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        total_seconds = 0
    days, rem = divmod(total_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes and not days:
        parts.append(f"{minutes}m")
    return " ".join(parts) if parts else "0m"

def build_expedition_embed() -> discord.Embed:
    state = get_expedition_state()
    now = now_utc()
    title = config.RELAY_NAME if hasattr(config, 'RELAY_NAME') else "ARC Uplink — Sector Relay 07"
    embed = discord.Embed(title=title, color=getattr(config, 'EMBED_COLOR', 0x00FFFF))
    # Add a thumbnail icon (same as events or a unique one for expeditions)
    embed.set_thumbnail(url="https://i.postimg.cc/RV6vwTdW/image.webp")
    embed.add_field(
        name="Expedition",
        value=f"Expedition #{state.expedition_number}",
        inline=False,
    )
    if state.phase == "PREP":
        time_until_window = state.window_start - now
        embed.add_field(
            name="Expedition Window Telemetry",
            value="INACTIVE",
            inline=False,
        )
        embed.add_field(
            name="Next Expedition Window",
            value=f"Opens in {format_timedelta(time_until_window)}",
            inline=False,
        )
        time_until_expedition = state.expedition_start - now
        embed.add_field(
            name="Cycle Countdown",
            value=f"Expedition begins in {format_timedelta(time_until_expedition)}",
            inline=False,
        )
        embed.add_field(
            name="Progress",
            value=f"{'▱' * 20} 0%",
            inline=False,
        )
    elif state.phase == "WINDOW":
        time_left = state.window_end - now
        bar, pct = progress_bar(state.window_start, state.window_end)
        embed.add_field(
            name="Expedition Window Telemetry",
            value="ACTIVE — Departure Registration Open",
            inline=False,
        )
        embed.add_field(
            name="Window Closes In",
            value=format_timedelta(time_left),
            inline=False,
        )
        embed.add_field(
            name="Progress",
            value=f"{bar} {pct}%",
            inline=False,
        )
    elif state.phase == "EXPEDITION":
        time_left = state.expedition_end - now
        bar, pct = progress_bar(state.expedition_start, state.expedition_end)
        embed.add_field(
            name="Expedition Window Telemetry",
            value="EXPEDITION ACTIVE",
            inline=False,
        )
        embed.add_field(
            name="Cycle Ends In",
            value=format_timedelta(time_left),
            inline=False,
        )
        embed.add_field(
            name="Progress",
            value=f"{bar} {pct}%",
            inline=False,
        )
        # Next window (next cycle)
        next_window_start = state.window_start + (state.expedition_end - state.window_start)
        embed.add_field(
            name="Next Departure Window",
            value=f"Begins after this cycle concludes",
            inline=False,
        )
    return embed
