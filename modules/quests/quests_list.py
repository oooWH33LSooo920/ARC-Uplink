import asyncio
from modules.quests.quests import fetch_quests

def list_quest_ids_and_names(quests: dict):
    for quest_id, quest in quests.items():
        name = quest['name']['en']
        print(f"{quest_id}: {name}")

if __name__ == "__main__":
    async def main():
        quests = await fetch_quests()
        if quests:
            list_quest_ids_and_names(quests)
        else:
            print("Failed to fetch quests.")
    asyncio.run(main())
