
import discord
from discord import app_commands
from discord.ext import commands

from modules.quests.quests import fetch_quests
from modules.quests.quests_search import search_by_name, search_by_id, get_chain
from modules.quests.quests_embed import build_quest_embed


class QuestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quest_cache = None

    async def load_quests(self):
        if not self.quest_cache:
            self.quest_cache = await fetch_quests()
        return self.quest_cache

    @app_commands.command(name="quest_list", description="List all quest IDs and names (paginated)")
    async def quest_list(self, interaction: discord.Interaction, page: str = "1"):
        await interaction.response.defer()
        quests = await self.load_quests()
        if not quests:
            await interaction.followup.send("No quests found.")
            return
        # Accept page as string, allow case-insensitive and strip spaces
        page_str = str(page).strip().lower()
        if not page_str.isdigit():
            await interaction.followup.send("Page must be a number.")
            return
        page_num = int(page_str)
        # Pagination
        quests_per_page = 20
        # Filter out quests with missing or suspicious names/descriptions
        quest_items = [
            (qid, q) for qid, q in quests.items()
            if isinstance(q.get('name'), dict) and 'en' in q['name'] and q['name']['en'].strip() and isinstance(q.get('description'), dict) and 'en' in q['description'] and q['description']['en'].strip() and not qid.startswith(('test', 'placeholder', 'code', '_'))
        ]
        total_pages = (len(quest_items) + quests_per_page - 1) // quests_per_page
        if page_num < 1 or page_num > total_pages:
            await interaction.followup.send(f"Page {page_num} is out of range. There are {total_pages} pages.")
            return
        start = (page_num - 1) * quests_per_page
        end = start + quests_per_page
        lines = [f"`{qid}`: {q['name']['en']}" for qid, q in quest_items[start:end]]
        embed = discord.Embed(
            title=f"Quest List (Page {page_num}/{total_pages})",
            description="\n".join(lines),
            color=0x00AEEF
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="quest", description="Look up a quest by name or ID")
    async def quest_lookup(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        quests = await self.load_quests()
        quest = search_by_name(quests, query) or search_by_id(quests, query)
        if not quest:
            return await interaction.followup.send("Quest not found.")
        embed = build_quest_embed(quest)
        await interaction.followup.send(embed=embed)



async def setup(bot):
    await bot.add_cog(QuestCommands(bot))
