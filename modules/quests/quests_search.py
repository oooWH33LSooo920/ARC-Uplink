def normalize(text: str) -> str:
    return text.lower().strip().replace("-", " ").replace("_", " ")

def search_by_name(quests: dict, query: str):
    q = normalize(query)
    for quest_id, quest in quests.items():
        name = quest["name"]["en"]
        if q in normalize(name):
            return quest
    return None

def search_by_id(quests: dict, quest_id: str):
    return quests.get(quest_id)

def search_by_slug(quests: dict, slug: str):
    for quest in quests.values():
        if quest.get("slug") == slug:
            return quest
    return None

def get_chain(quests: dict, quest_id: str):
    chain = []
    current = quests.get(quest_id)
    if not current:
        return []
    # Walk backwards
    prev_ids = current.get("previousQuestIds", [])
    while prev_ids:
        prev_id = prev_ids[0]
        prev_quest = quests.get(prev_id)
        if not prev_quest:
            break
        chain.insert(0, prev_quest)
        prev_ids = prev_quest.get("previousQuestIds", [])
    # Add current
    chain.append(current)
    # Walk forwards
    next_ids = current.get("nextQuestIds", [])
    while next_ids:
        next_id = next_ids[0]
        next_quest = quests.get(next_id)
        if not next_quest:
            break
        chain.append(next_quest)
        next_ids = next_quest.get("nextQuestIds", [])
    return chain
