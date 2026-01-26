import asyncio
from modules.quests.quests import fetch_daily_quests
from modules.quests.quests_embed import build_quests_embed

async def post_daily_quests(bot, channel_id):
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("[ARC Uplink] Quests channel not found.")
        return

    data = await fetch_daily_quests()
    if not data:
        print("[ARC Uplink] No quest data available.")
        return

    embed = build_quests_embed(data)
    await channel.send(embed=embed)
