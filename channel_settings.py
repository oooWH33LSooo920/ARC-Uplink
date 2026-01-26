import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'channels.json')

def load_channels():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_channels(channels):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(channels, f)

# Usage:
# channels = load_channels()
# channels[str(guild_id)] = {"weekly_trials": channel_id, "map_events": channel_id}
# save_channels(channels)
