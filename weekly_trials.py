import requests
from bs4 import BeautifulSoup
import discord
import random
from datetime import datetime, timedelta
import pytz

ARC_UPLINK_COLORS = {
    "rust": 0xC65F1A,
    "steel": 0x1A4B63,
    "amber": 0xD9A441,
    "critical": 0xB7322C,
    "neutral": 0x2B2B2B
}

ARC_UPLINK_MOTTOS = [
    "Signal Strong, Raiders Ready.",
    "Uplink Secure, Eyes Forward.",
    "Transmit. Engage. Survive.",
    "Raiders United, Uplink Online.",
    "No Signal Left Behind.",
    "From Static to Victory.",
    "Stay Synced. Stay Safe.",
    "Every Cycle, Every Signal."
]

DEXERTO_URL = "https://www.dexerto.com/wikis/arc-raiders/weekly-trials/"

def fetch_weekly_trials():
    response = requests.get(DEXERTO_URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    trials = []
    table = soup.find("table")
    if not table:
        return None
    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            trial_name = cols[0].get_text(strip=True)
            trial_desc = cols[1].get_text(strip=True)
            trials.append({
                "name": trial_name,
                "description": trial_desc
            })
    return trials

def build_weekly_trials_embed(trials):
    embed = discord.Embed(
        title="ARC Raiders Weekly Trials",
        description="Operational Directives for This Cycle",
        color=ARC_UPLINK_COLORS["rust"]
    )
    embed.set_author(name="ARC Uplink")
    # Add thumbnail (same as events)
    embed.set_thumbnail(url="https://i.postimg.cc/RV6vwTdW/image.webp")
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    days_ahead = (0 - now_utc.weekday() + 7) % 7
    if days_ahead == 0 and now_utc.hour >= 10:
        days_ahead = 7
    next_rotation_utc = (now_utc + timedelta(days=days_ahead)).replace(hour=10, minute=0, second=0, microsecond=0)
    next_rotation_utc = next_rotation_utc.astimezone(pytz.utc)
    us_timezones = [
        ("Eastern", "US/Eastern"),
        ("Central", "US/Central"),
        ("Mountain", "US/Mountain"),
        ("Pacific", "US/Pacific")
    ]
    tz_lines = [f"UTC: {next_rotation_utc.strftime('%A, %B %d, %Y %H:%M %Z')}"]
    
    for label, tzname in us_timezones:
        local_time = next_rotation_utc.astimezone(pytz.timezone(tzname))
        tz_lines.append(f"{label}: {local_time.strftime('%A, %B %d, %Y %I:%M %p %Z')}")
    embed.add_field(
        name="Next Weekly Trials Reset",
        value="\n".join(tz_lines),
        inline=False
    )
    for t in trials:
        embed.add_field(
            name=f"🔸 {t['name']}",
            value=f"```{t['description']}```",
            inline=False
        )
    embed.set_footer(
        text=f"{random.choice(ARC_UPLINK_MOTTOS)} • ARC Uplink • Updated {datetime.utcnow().strftime('%b %d, %Y')} UTC"
    )
    return embed

# Test block at end
if __name__ == "__main__":
    trials = fetch_weekly_trials()
    print("Fetched Trials:")
    for t in trials:
        print(f"- {t['name']}: {t['description']}")
    embed = build_weekly_trials_embed(trials)
    print("\nEmbed Title:", embed.title)
    print("Embed Description:", embed.description)
    print("Embed Author:", embed.author.name if embed.author else None)
    print("Embed Fields:")
    for field in embed.fields:
        print(f"- {field.name}: {field.value}")
import requests
from bs4 import BeautifulSoup
import discord
import random
from datetime import datetime, timedelta
import pytz

ARC_UPLINK_COLORS = {
    "rust": 0xC65F1A,
    "steel": 0x1A4B63,
    "amber": 0xD9A441,
    "critical": 0xB7322C,
    "neutral": 0x2B2B2B
}

ARC_UPLINK_MOTTOS = [
    "Hold the Line.",
    "Steel in the Storm.",
    "No Signal Left Behind.",
    "From Rust, Resolve.",
    "Alliance Above All.",
    "Stand Firm. Strike Hard.",
    "The Barrens Remember.",
    "Every Cycle Counts."
]

DEXERTO_URL = "https://www.dexerto.com/wikis/arc-raiders/weekly-trials/"

def fetch_weekly_trials():
    response = requests.get(DEXERTO_URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    trials = []
    table = soup.find("table")
    if not table:
        return None
    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            trial_name = cols[0].get_text(strip=True)
            trial_desc = cols[1].get_text(strip=True)
            trials.append({
                "name": trial_name,
                "description": trial_desc
            })
    return trials

def build_weekly_trials_embed(trials):
    embed = discord.Embed(
        title="ARC Raiders Weekly Trials",
        description="Operational Directives for This Cycle",
        color=ARC_UPLINK_COLORS["rust"]
    )
    embed.set_author(name="ARC Uplink")
    embed.set_thumbnail(url="https://arctracker.io/favicon.ico")
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    days_ahead = (0 - now_utc.weekday() + 7) % 7
    if days_ahead == 0 and now_utc.hour >= 10:
        days_ahead = 7
    next_rotation_utc = (now_utc + timedelta(days=days_ahead)).replace(hour=10, minute=0, second=0, microsecond=0)
    next_rotation_utc = next_rotation_utc.astimezone(pytz.utc)
    us_timezones = [
        ("Eastern", "US/Eastern"),
        ("Central", "US/Central"),
        ("Mountain", "US/Mountain"),
        ("Pacific", "US/Pacific")
    ]
    tz_lines = [f"UTC: {next_rotation_utc.strftime('%A, %B %d, %Y %H:%M %Z')}"]
    for label, tzname in us_timezones:
        local_time = next_rotation_utc.astimezone(pytz.timezone(tzname))
        tz_lines.append(f"{label}: {local_time.strftime('%A, %B %d, %Y %I:%M %p %Z')}")
    embed.add_field(
        name="Next Weekly Trials Reset",
        value="\n".join(tz_lines),
        inline=False
    )
    for t in trials:
        embed.add_field(
            name=f"🔸 {t['name']}",
            value=f"```{t['description']}```",
            inline=False
        )
    embed.set_footer(
        text=f"ARC Uplink • Updated {datetime.utcnow().strftime('%b %d, %Y')} UTC"
    )
    return embed
