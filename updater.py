import discord
from discord.ext import tasks
from arc_uplink.ui import build_expedition_embed
import arc_uplink.config as config

class ExpeditionUpdater:
    def __init__(self, bot: discord.Client, channel_id=None, message_id=None):
        self.bot = bot
        self.channel_id = channel_id or config.CHANNEL_ID
        self.message_id = message_id or config.MESSAGE_ID
        self.task = self._create_task()

    def _create_task(self):
        @tasks.loop(minutes=config.UPDATE_INTERVAL_MINUTES)
        async def loop():
            channel = self.bot.get_channel(self.channel_id)
            if channel is None:
                return
            try:
                message = await channel.fetch_message(self.message_id)
            except discord.NotFound:
                return
            embed = build_expedition_embed()
            await message.edit(embed=embed)
        @loop.before_loop
        async def before_loop():
            await self.bot.wait_until_ready()
        return loop

    def start(self):
        self.task.start()
import discord
from live_events import fetch_live_events, build_live_event_embed
class LiveEventsUpdater:
    def __init__(self, bot, channel_id, guild_id=None, interval=60):
        from channel_settings import load_channels, save_channels
        self.bot = bot
        self.channel_id = channel_id
        self.guild_id = str(guild_id) if guild_id is not None else None
        self.interval = interval
        self.static_message_id = None
        self.task = tasks.loop(seconds=self.interval)(self.update_message)
        # Load static_message_id from channels.json if available
        if self.guild_id:
            channels = load_channels()
            if self.guild_id in channels and 'map_events_message_id' in channels[self.guild_id]:
                self.static_message_id = channels[self.guild_id]['map_events_message_id']
                print(f"[LiveEventsUpdater] Loaded message ID {self.static_message_id} for guild {self.guild_id} channel {self.channel_id}")

    async def find_existing_message(self, channel):
        # Look for a recent message sent by the bot with the expected embed title
        async for msg in channel.history(limit=100):
            if msg.author.id == self.bot.user.id and msg.embeds:
                embed = msg.embeds[0]
                if embed.title and "ARC Raiders Live Events" in embed.title:
                    return msg.id
        return None

    async def update_message(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print('Channel not found or not set.')
            return
        try:
            current, upcoming = fetch_live_events()
            embed = build_live_event_embed(current, upcoming)
            if self.static_message_id is None:
                self.static_message_id = await self.find_existing_message(channel)
                if self.static_message_id:
                    print(f"[LiveEventsUpdater] Found existing message ID {self.static_message_id} in channel {self.channel_id}")
            if self.static_message_id:
                try:
                    msg = await channel.fetch_message(self.static_message_id)
                    await msg.edit(embed=embed)
                    return
                except discord.NotFound:
                    print(f"[LiveEventsUpdater] Message ID {self.static_message_id} not found in channel {self.channel_id}, will post new message.")
                    self.static_message_id = None
                except Exception as e:
                    print(f"Error editing live events message: {e}")
            sent = await channel.send(embed=embed)
            self.static_message_id = sent.id
            print(f"[LiveEventsUpdater] Posted new message ID {self.static_message_id} in channel {self.channel_id}")
            # Save static_message_id to channels.json
            if self.guild_id:
                from channel_settings import load_channels, save_channels
                channels = load_channels()
                if self.guild_id not in channels:
                    channels[self.guild_id] = {}
                channels[self.guild_id]['map_events_message_id'] = self.static_message_id
                save_channels(channels)
        except Exception as e:
            print(f"Error updating live events message: {e}")

    def start(self):
        if not self.task.is_running():
            self.task.start()
from weekly_trials import fetch_weekly_trials, build_weekly_trials_embed

class WeeklyRotationUpdater:
    def __init__(self, bot, channel_id, label="ARC Weekly Trials", reset_hour=10, reset_minute=0, reset_weekday=0):
        self.bot = bot
        self.channel_id = channel_id
        self.label = label
        self.reset_hour = reset_hour
        self.reset_minute = reset_minute
        self.reset_weekday = reset_weekday  # 0=Monday
        self.static_message_id = None
        self.task = tasks.loop(minutes=5)(self.update_message)

    async def find_existing_message(self, channel):
        async for msg in channel.history(limit=20):
            if msg.author.id == self.bot.user.id and msg.embeds:
                embed = msg.embeds[0]
                # Match both possible titles for compatibility
                if embed.title and (
                    "ARC Raiders Weekly Trials" in embed.title or
                    "ARC Uplink Weekly Trials" in embed.title
                ):
                    return msg.id
        return None

    def get_next_reset(self):
        import pytz
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        days_ahead = (self.reset_weekday - now.weekday() + 7) % 7
        if days_ahead == 0 and now.hour >= self.reset_hour:
            days_ahead = 7
        next_reset = (now + datetime.timedelta(days=days_ahead)).replace(hour=self.reset_hour, minute=self.reset_minute, second=0, microsecond=0)
        return next_reset

    async def update_message(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print('Channel not found or not set.')
            return
        try:
            trials = fetch_weekly_trials()
            embed = build_weekly_trials_embed(trials) if trials else None
            if not embed:
                print('Could not build weekly trials embed.')
                return
            if self.static_message_id is None:
                self.static_message_id = await self.find_existing_message(channel)
            if self.static_message_id:
                try:
                    msg = await channel.fetch_message(self.static_message_id)
                    await msg.edit(embed=embed)
                    return
                except discord.NotFound:
                    self.static_message_id = None
                except Exception as e:
                    print(f"Error editing weekly trials message: {e}")
            sent = await channel.send(embed=embed)
            self.static_message_id = sent.id
        except Exception as e:
            print(f"Error updating weekly trials message: {e}")

    def start(self):
        if not self.task.is_running():
            self.task.start()
import requests
import datetime
from discord.ext import tasks

class StaticMessageUpdater:
    def __init__(self, bot, channel_id, api_url, label="ARC Map Event", interval=60):
        self.bot = bot
        self.channel_id = channel_id
        self.api_url = api_url
        self.label = label
        self.interval = interval
        self.static_message_id = None
        self.task = tasks.loop(seconds=self.interval)(self.update_message)

    async def find_existing_message(self, channel):
        async for msg in channel.history(limit=20):
            if msg.author.id == self.bot.user.id and msg.content and self.label in msg.content:
                return msg.id
        return None

    def format_event(self, event, next_update):
        name = event.get('name', 'Unknown Event')
        start = event.get('startTime', 'N/A')
        end = event.get('endTime', 'N/A')
        now = datetime.datetime.utcnow()
        countdown = (next_update - now).total_seconds()
        countdown_str = str(datetime.timedelta(seconds=int(countdown))) if countdown > 0 else 'Updating...'
        return f"**{self.label}**\nName: {name}\nStart: {start}\nEnd: {end}\nNext update in: {countdown_str}"

    async def update_message(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print('Channel not found or not set.')
            return
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and data:
                latest_event = data[0]
                now = datetime.datetime.utcnow()
                next_update = now + datetime.timedelta(seconds=self.interval)
                content = self.format_event(latest_event, next_update)
                if self.static_message_id is None:
                    self.static_message_id = await self.find_existing_message(channel)
                if self.static_message_id:
                    try:
                        msg = await channel.fetch_message(self.static_message_id)
                        await msg.delete()
                    except discord.NotFound:
                        pass
                    except Exception as e:
                        print(f"Error deleting static event message: {e}")
                    self.static_message_id = None
                sent = await channel.send(content)
                self.static_message_id = sent.id
        except Exception as e:
            print(f"Error updating static message: {e}")

    def start(self):
        if not self.task.is_running():
            self.task.start()
