"""Read OpenCode v1/v2 history and deduplicate migrated messages."""

from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path

from common import encode, excerpt, root_id, split_chunks
from evidence import attach, bound_entries, media_reference, structured_results
import opencode_v2


def normalize_message(db, message, start_ms, end_ms, tool_chars, stats, directory="/"):
    data = json.loads(message["data"])
    base = {
        "message_id": message["id"],
        "storage_schema": "opencode_v1",
        "stored_after_cutoff": "time_updated" in message.keys() and message["time_updated"] >= end_ms,
        "role": data.get("role", "unknown"),
        "summary": data.get("summary", False),
        "model": data.get("modelID"),
        "provider": data.get("providerID"),
        "timestamp": datetime.fromtimestamp(message["time_created"] / 1000).astimezone().isoformat(),
        "context_only": message["time_created"] < start_ms and (dict(message).get("time_updated") or 0) < start_ms,
    }
    entries = []
    if data.get("error"):
        entries.append({**base, "type": "message_error", "error": excerpt(data["error"], tool_chars)})
    parts = db.execute(
        "SELECT * FROM part WHERE message_id = ? AND time_created < ? ORDER BY time_created, id",
        (message["id"], end_ms),
    )
    for row in parts:
        part = json.loads(row["data"])
        kind = part.get("type", "unknown")
        updated = dict(row).get("time_updated") or 0
        completed = (part.get("state", {}).get("time", {}).get("end") or 0) if kind == "tool" else 0
        item = {
            **base,
            "part_id": row["id"],
            "part_timestamp": datetime.fromtimestamp(row["time_created"] / 1000).astimezone().isoformat(),
            "type": kind,
            "context_only": message["time_created"] < start_ms and max(row["time_created"], updated, completed) < start_ms,
            "stored_after_cutoff": base["stored_after_cutoff"] or max(updated, completed) >= end_ms,
        }
        if kind == "text":
            text = part.get("text", "")
            for offset in range(0, len(text), 6000):
                entries.append(attach({
                    **item, "text": text[offset:offset + 6000], "text_offset": offset,
                    "text_length": len(text), "synthetic": part.get("synthetic", False),
                }, text if offset == 0 else "", directory))
        elif kind == "tool":
            state = part.get("state", {})
            item.update({"tool": part.get("tool"), "status": state.get("status", "unknown")})
            for field in ("input", "output", "error"):
                if field in state:
                    item[field] = excerpt(state[field], tool_chars)
                    stats["tool_chars_omitted"] += item[field]["omitted_chars"]
            attach(item, state.get("input", {}), directory)
            attach(item, state.get("output", ""), directory, results=True)
            facts = structured_results(state.get("metadata", {}))
            if facts:
                item.setdefault("evidence", {}).setdefault("reported_results", []).extend(facts)
            entries.append(item)
            if not item["context_only"]:
                stats["tool_calls"] += 1
                stats["tool_errors"] += item["status"] == "error"
        elif kind == "file":
            item.update(filename=part.get("filename"), mime=part.get("mime"))
            if part.get("url"):
                item["evidence"] = {"media": [media_reference(part["url"], directory)]}
            entries.append(item)
        elif kind == "patch":
            entries.append({**item, "files": excerpt(part.get("files", []), tool_chars)})
        elif kind == "compaction":
            entries.append({**item, "auto": part.get("auto")})
        else:
            stats[f"omitted_part_type:{kind}"] += 1
    return bound_entries(entries)


def collect_v1(db, start, end, project, tool_chars, chunk_chars):
    start_ms, end_ms = int(start.timestamp() * 1000), int(end.timestamp() * 1000)
    sessions = {row["id"]: dict(row) for row in db.execute("SELECT * FROM session")}
    activity = {}
    for table in ("message", "part"):
        columns = {r["name"] for r in db.execute("PRAGMA table_info(" + table + ")")}
        times = ["time_created"] + (["time_updated"] if "time_updated" in columns else [])
        if table == "part":
            times.append("json_extract(data, '$.state.time.end')")
        activity[table] = "(" + " OR ".join(f"({t} >= :start AND {t} < :end)" for t in times) + ")"
    bounds = {"start": start_ms, "end": end_ms}
    active = db.execute(
        "SELECT DISTINCT session_id FROM message WHERE " + activity["message"] +
        " UNION SELECT session_id FROM part WHERE " + activity["part"], bounds,
    ).fetchall()
    results = []
    for active_session in active:
        session = sessions[active_session["session_id"]]
        root_key = root_id(session["id"], sessions)
        root = sessions.get(root_key, session)
        if root["title"].startswith("[session-review]"):
            continue
        if project and Path(root["directory"]).resolve() != project:
            continue
        messages = db.execute(
            "SELECT * FROM message WHERE session_id = :session AND time_created < :end AND (" + activity["message"] +
            " OR id IN (SELECT message_id FROM part WHERE session_id = :session AND " + activity["part"] +
            ")) ORDER BY time_created, id", {**bounds, "session": session["id"]},
        ).fetchall()
        if not messages:
            continue
        context = db.execute(
            """SELECT * FROM message WHERE session_id = ? AND time_created < ?
               ORDER BY time_created DESC, id DESC LIMIT 4""",
            (session["id"], messages[0]["time_created"]),
        ).fetchall()[::-1]
        stats = Counter()
        entries = []
        for message in [*context, *messages]:
            entries.extend(normalize_message(db, message, start_ms, end_ms, tool_chars, stats, session["directory"]))
        results.append({
            "session_id": session["id"], "root_session_id": root_key,
            "parent_session_id": session["parent_id"], "title": session["title"],
            "project_id": root["project_id"], "directory": root["directory"],
            "message_count": len(messages), "context_message_count": len(context),
            "stats": dict(stats),
            "input_hash": hashlib.sha256(encode(entries).encode()).hexdigest(),
            "chunks": split_chunks(entries, chunk_chars),
        })
    return results


def collect(db, start, end, project, tool_chars, chunk_chars):
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    adapters = []
    if {"session", "message", "part"} <= tables:
        adapters.append(collect_v1)
    if {"session_v2", "session_message"} <= tables:
        adapters.append(opencode_v2.collect)
    if not adapters:
        raise ValueError("No complete supported OpenCode v1 or v2 table set found")
    sessions = {}
    for table in ("session", "session_v2"):
        if table in tables:
            sessions.update({r["id"]: dict(r) for r in db.execute("SELECT * FROM " + table)})
    merged = {}
    for adapter in adapters:
        for result in adapter(db, start, end, None, tool_chars, chunk_chars):
            previous = merged.get(result["session_id"])
            if previous:
                entries = [e for c in result["chunks"] for e in c]
                ids = {e["message_id"] for e in entries}
                entries += [e for c in previous["chunks"] for e in c if e["message_id"] not in ids]
                entries.sort(key=lambda e: (e["timestamp"], e["message_id"], e.get("text_offset", 0)))
                result["chunks"] = split_chunks(entries, chunk_chars)
                result["message_count"] = len({e["message_id"] for e in entries if not e["context_only"]})
                result["context_message_count"] = len({e["message_id"] for e in entries if e["context_only"]})
                result["input_hash"] = hashlib.sha256(encode(entries).encode()).hexdigest()
                result["stats"] = dict(Counter({
                    "tool_calls": sum(e["type"] == "tool" and not e["context_only"] for e in entries),
                    "tool_errors": sum(e["type"] == "tool" and e.get("status") == "error" and not e["context_only"] for e in entries),
                }))
            merged[result["session_id"]] = result
    results = []
    for result in merged.values():
        root_key = root_id(result["session_id"], sessions)
        root = sessions.get(root_key, sessions[result["session_id"]])
        if (root["title"] or "").startswith("[session-review]"):
            continue
        if project and Path(root["directory"]).resolve() != project:
            continue
        result.update(root_session_id=root_key, root_directory=root["directory"], project_id=root["project_id"])
        result["input_hash"] = hashlib.sha256(encode({
            "entries": [e for c in result["chunks"] for e in c], "root": root_key, "project": root["project_id"],
        }).encode()).hexdigest()
        results.append(result)
    return sorted(results, key=lambda r: r["session_id"])
