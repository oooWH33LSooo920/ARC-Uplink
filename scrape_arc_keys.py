import requests
from bs4 import BeautifulSoup
import json

URL = "https://skycoach.gg/blog/arc-raiders/articles/all-keys-and-doors-locations"

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

# Template fields for each key
TEMPLATE = {
    "name": "",
    "description": "",
    "building_area": "",
    "floor_level": "",
    "map_coordinates": "",
    "danger": "",
    "recommended_route": "",
    "notes": ""
}

keys = []
for heading in soup.find_all(['h2', 'h3', 'h4']):
    title = heading.get_text(strip=True)
    if "Key" in title or "Access Card" in title or "Storage" in title or "Checkpoint" in title:
        desc = []
        next_node = heading.find_next_sibling()
        while next_node and next_node.name in ['p', 'ul', 'ol']:
            desc.append(next_node.get_text(strip=True))
            next_node = next_node.find_next_sibling()
        key = TEMPLATE.copy()
        key["name"] = title
        key["description"] = desc[0] if desc else ""
        # The rest of the fields are left blank for manual filling
        key["building_area"] = ""
        key["floor_level"] = ""
        key["map_coordinates"] = ""
        key["danger"] = ""
        key["recommended_route"] = ""
        key["notes"] = ""
        keys.append(key)

with open("arc_keys.json", "w", encoding="utf-8") as f:
    json.dump(keys, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(keys)} keys/doors to arc_keys.json with detailed template fields.")
