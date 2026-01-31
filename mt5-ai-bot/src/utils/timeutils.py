from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Iterable, List
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class SessionWindow:
    name: str
    start: time
    end: time


def parse_sessions(timezone: str, windows: Iterable[dict]) -> tuple[ZoneInfo, List[SessionWindow]]:
    tz = ZoneInfo(timezone)
    parsed: List[SessionWindow] = []
    for window in windows:
        start = _parse_time(window["start"])
        end = _parse_time(window["end"])
        parsed.append(SessionWindow(name=window.get("name", "session"), start=start, end=end))
    return tz, parsed


def is_in_session(dt: datetime, tz: ZoneInfo, windows: List[SessionWindow]) -> bool:
    local_dt = dt.astimezone(tz)
    current = local_dt.time()
    for window in windows:
        if window.start <= window.end:
            if window.start <= current <= window.end:
                return True
        else:
            if current >= window.start or current <= window.end:
                return True
    return False


def _parse_time(value: str) -> time:
    hour, minute = value.split(":")
    return time(int(hour), int(minute))
