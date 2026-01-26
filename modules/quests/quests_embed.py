import discord
from datetime import datetime

def build_quest_embed(quest: dict):
    embed = discord.Embed(
        title=f"🗲 {quest['name']['en']}",
        description=quest["description"]["en"],
        color=0x00AEEF
    )

    # Trader
    if quest.get("trader"):
        embed.add_field(name="Trader", value=quest["trader"], inline=True)

    # Maps
    if quest.get("map"):
        embed.add_field(name="Map", value=", ".join(quest["map"]), inline=True)

    # Objectives
    if quest.get("objectives"):
        obj_text = "\n".join(f"• {o['en']}" for o in quest["objectives"])
        embed.add_field(name="Objectives", value=obj_text, inline=False)

    # Rewards
    if quest.get("rewardItemIds"):
        rewards = "\n".join(
            f"• `{r['itemId']}` × {r['quantity']}"
            for r in quest["rewardItemIds"]
        )
        embed.add_field(name="Rewards", value=rewards, inline=False)


    # Video
    if quest.get("videoUrl"):
        embed.add_field(name="Video", value=quest["videoUrl"], inline=False)

    embed.set_footer(text=f"Quest ID: {quest['id']} • Slug: {quest['slug']}")
    return embed
