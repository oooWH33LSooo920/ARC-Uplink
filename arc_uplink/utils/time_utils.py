# utils/time_utils.py
from datetime import datetime, timezone

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def parse_iso_utc(iso_str: str) -> datetime:
    return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def to_unix(dt: datetime) -> int:
    return int(dt.timestamp())
