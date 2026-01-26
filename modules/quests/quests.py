import aiohttp
import asyncio

QUESTS_URL = "https://arctracker.io/api/quests"

async def fetch_quests():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(QUESTS_URL, headers={"User-Agent": "ARC-Uplink"}) as resp:
                if resp.status != 200:
                    print(f"[ARC Uplink] Quest fetch failed: {resp.status}")
                    return None

                data = await resp.json()

                # The actual quests are inside data["quests"]
                return data.get("quests", {})

        except Exception as e:
            print(f"[ARC Uplink] Error fetching quests: {e}")
            return None
