from channel_settings import load_channels, save_channels
import asyncio

class ChannelSettingsDB:
    def __init__(self):
        self._lock = asyncio.Lock()

    async def get(self, key):
        async with self._lock:
            channels = load_channels()
            return channels.get(str(key))

    async def set(self, key, value):
        async with self._lock:
            channels = load_channels()
            channels[str(key)] = value
            save_channels(channels)
