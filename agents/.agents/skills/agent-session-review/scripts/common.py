import json
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


VERSION = 2


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def day_bounds(value, timezone=None):
    zone = ZoneInfo(timezone) if timezone else None
    today = datetime.now(zone).date()
    day = today - timedelta(days=1) if value == "yesterday" else date.fromisoformat(value)
    start = datetime.combine(day, time.min, zone)
    end = datetime.combine(day + timedelta(days=1), time.min, zone)
    if zone is None:
        start, end = start.astimezone(), end.astimezone()
    return day, start, end


def excerpt(value, limit):
    text = value if isinstance(value, str) else encode(value)
    if len(text) <= limit:
        return {"text": text, "omitted_chars": 0}
    half = limit // 2
    return {
        "text": text[:half] + "\n[... omitted ...]\n" + text[-half:],
        "omitted_chars": len(text) - 2 * half,
    }


def split_chunks(entries, max_chars):
    chunks, current, size = [], [], 0
    for entry in entries:
        length = len(encode(entry))
        if current and size + length > max_chars:
            chunks.append(current)
            current, size = [], 0
        current.append(entry)
        size += length
    if current:
        chunks.append(current)
    return chunks


def root_id(session_id, sessions):
    seen = set()
    while sessions.get(session_id, {}).get("parent_id"):
        if session_id in seen:
            raise ValueError("Cycle in session parent links")
        seen.add(session_id)
        session_id = sessions[session_id]["parent_id"]
    return session_id
