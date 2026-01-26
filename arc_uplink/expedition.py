
# expedition.py -- ARC Uplink Expedition State Logic
#
# This module provides the state machine and helpers for ARC Raiders expeditions.
#
# - Expedition numbering increments at the start of each new window.
# - Phases: PREP (before window), WINDOW (sign-up), EXPEDITION (active period).
# - Configurable via FIRST_EXPEDITION_ISO, WINDOW_DAYS, EXPEDITION_DAYS, CYCLE_DAYS, FIRST_EXPEDITION_NUMBER.

from datetime import timedelta
from dataclasses import dataclass
from arc_uplink.utils.time_utils import now_utc, parse_iso_utc
import arc_uplink.config as config

@dataclass
class ExpeditionState:
    expedition_number: int
    window_start: object
    window_end: object
    expedition_start: object
    expedition_end: object
    phase: str          # "PREP", "WINDOW", "EXPEDITION"
    active: bool        # True only during EXPEDITION
    icon: str           # Emoji or icon for phase

def get_next_window_dates(state: ExpeditionState):
    """Returns the start and end datetime for the next expedition window."""
    next_window_start = state.window_start + CYCLE
    next_window_end = next_window_start + WINDOW
    return next_window_start, next_window_end

def expedition_summary() -> str:
    state = get_expedition_state()
    now = now_utc()
    if state.phase == "WINDOW":
        bar, pct = progress_bar(state.window_start, state.window_end)
        phase_label = "Sign-Up Window"
        status = "ACTIVE"
        countdown = f"Expedition begins in {(state.expedition_start - now).days}d {(state.expedition_start - now).seconds//3600}h"
    elif state.phase == "EXPEDITION":
        bar, pct = progress_bar(state.expedition_start, state.expedition_end)
        phase_label = "Expedition Active"
        status = "ACTIVE"
        countdown = f"Expedition ends in {(state.expedition_end - now).days}d {(state.expedition_end - now).seconds//3600}h"
    else:
        # PREP phase
        bar, pct = progress_bar(now, state.window_start)
        phase_label = "Preparation"
        status = "INACTIVE"
        countdown = f"Window opens in {(state.window_start - now).days}d {(state.window_start - now).seconds//3600}h"

    summary = (
        f"{state.icon} **Expedition #{state.expedition_number}** — **{phase_label}**\n"
        f"🗓️ **Window:** {state.window_start:%d %b %Y} — {state.window_end:%d %b %Y}\n"
        f"🚀 **Expedition:** {state.expedition_start:%d %b %Y} — {state.expedition_end:%d %b %Y}\n"
        f"Status: {status}\n"
        f"{countdown}"
    )
    if bar:
        summary += f"\nProgress\n{bar} {pct}%"
    return summary

# Base configuration
FIRST_EXPEDITION = parse_iso_utc(config.FIRST_EXPEDITION_ISO)
WINDOW = timedelta(days=config.WINDOW_DAYS)
EXPEDITION = timedelta(days=config.EXPEDITION_DAYS)
CYCLE = timedelta(days=config.CYCLE_DAYS)
FIRST_EXPEDITION_NUMBER = getattr(config, "FIRST_EXPEDITION_NUMBER", 1)

def _phase_icon(phase: str) -> str:
    if phase == "WINDOW":
        return "🟩"
    if phase == "EXPEDITION":
        return "🟧"
    return "🟦"


def get_expedition_state() -> ExpeditionState:

    now = now_utc()
    start = FIRST_EXPEDITION
    expedition_number = FIRST_EXPEDITION_NUMBER

    while True:
        window_start = start
        window_end = window_start + WINDOW
        expedition_start = window_end
        expedition_end = expedition_start + EXPEDITION

        if now < window_start:
            phase = "PREP"
            break
        elif window_start <= now < window_end:
            phase = "WINDOW"
            break
        elif expedition_start <= now < expedition_end:
            phase = "EXPEDITION"
            break
        # Advance to next cycle
        start += CYCLE
        expedition_number += 1

    # Expedition number should increment at the start of the window for both window and expedition phases
    if now >= window_start:
        expedition_number += 1

    return ExpeditionState(
        expedition_number=expedition_number,
        window_start=window_start,
        window_end=window_end,
        expedition_start=expedition_start,
        expedition_end=expedition_end,
        phase=phase,
        active=(phase == "EXPEDITION"),
        icon=_phase_icon(phase),
    )


def progress_bar(start, end, length: int = 20):
    now = now_utc()
    total = (end - start).total_seconds()
    elapsed = max(0, min((now - start).total_seconds(), total))

    if total <= 0:
        return "▱" * length, 0

    percent = elapsed / total
    filled = int(percent * length)
    empty = length - filled
    bar = "▰" * filled + "▱" * empty

    return bar, int(percent * 100)
