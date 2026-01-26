
import discord
import datetime
import requests

ARC_EVENT_COLORS = {
    "major": 0xB7322C,  # Red
    "minor": 0x1A4B63,  # Blue
    "default": 0x2B2B2B
}

def build_live_event_embed(events, upcoming=None):
    now = datetime.datetime.utcnow()
    # Try to get current hour from API for more accurate countdown
    current_api_hour = None
    try:
        api_data = requests.get('https://arctracker.io/api/map-events', timeout=10).json()
        current_api_hour = api_data.get('currentHour')
    except Exception:
        pass
    embed = discord.Embed(
        title="ARC Raiders Map Events",
        description=None,
        color=ARC_EVENT_COLORS["default"]
    )
    # Set thumbnail: use icon from first event if available, else fallback
    thumbnail_url = None
    if events and isinstance(events, list):
        first_icon = events[0].get('iconPath')
        if first_icon:
            thumbnail_url = first_icon
    if not thumbnail_url:
        # Fallback to a generic ARC Raiders icon (replace with a real URL if you have one)
        thumbnail_url = "https://arctracker.io/favicon.ico"
    embed.set_thumbnail(url=thumbnail_url)
    # Current Events
    if events:
        current_lines = []
        for event in events:
            name = event.get('eventLocalizations', {}).get('en', event.get('eventType', 'Unknown'))
            map_name = event.get('mapLocalizations', {}).get('en', event.get('mapName', 'Unknown'))
            category = event.get('eventCategory', 'default')
            # Calculate minutes left in the hour for current events
            mins_left = None
            event_hour = event.get('hour')
            if current_api_hour is not None and event_hour == current_api_hour:
                mins_left = 60 - now.minute
            elif event_hour is not None:
                # If event hour is in the future, show as upcoming, not current
                mins_left = None
            left_str = f"{mins_left}m" if mins_left is not None and mins_left >= 0 else '?'
            current_lines.append(f"• {map_name} — {name} ({category}) ({left_str} left)")
        embed.add_field(name="Current Events:", value="\n".join(current_lines), inline=False)
        embed.color = ARC_EVENT_COLORS.get(events[0].get('eventCategory', 'default'), ARC_EVENT_COLORS['default'])
    else:
        embed.add_field(name="Current Events:", value="None", inline=False)

    # Upcoming Events (next 2 hours)
    if upcoming:
        filtered = []
        for e in upcoming:
            # Show events within the next 2 hours
            event_hour = e.get('hour')
            event_minute = e.get('minute', 0)
            if isinstance(event_hour, int):
                event_dt = now.replace(hour=event_hour, minute=event_minute, second=0, microsecond=0)
                if event_dt < now:
                    event_dt += datetime.timedelta(days=1)
                mins_until = int((event_dt - now).total_seconds() // 60)
                if 0 <= mins_until <= 120:
                    filtered.append((e, mins_until))
        if filtered:
            upcoming_lines = []
            for e, mins_until in filtered:
                name = e.get('eventLocalizations', {}).get('en', e.get('eventType', 'Unknown'))
                map_name = e.get('mapLocalizations', {}).get('en', e.get('mapName', 'Unknown'))
                category = e.get('eventCategory', 'default')
                hour = e.get('hour', '?')
                minute = e.get('minute', 0)
                left_str = f"{mins_until}m"
                upcoming_lines.append(f"• {map_name} — {name} ({category}) at {hour:02}:{minute:02} (in {left_str})")
            embed.add_field(name="Upcoming Events (Next 2 Hours):", value="\n".join(upcoming_lines), inline=False)
        else:
            embed.add_field(name="Upcoming Events (Next 2 Hours):", value="None", inline=False)
    embed.set_footer(text="ARC Uplink • Live Events")
    return embed

def fetch_live_events():
    url = 'https://arctracker.io/api/map-events'
    response = requests.get(url, timeout=10)
    data = response.json()
    current = data.get('currentEvents', [])
    upcoming = data.get('upcomingEvents', [])
    return current, upcoming
