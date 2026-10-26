"""Read observed OpenCode v2 session/message storage."""

from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path

from common import encode, excerpt, root_id, split_chunks
from evidence import attach, bound_entries, media_reference, structured_results


def normalize(row, session, start_ms, end_ms, tool_chars, stats):
    data = json.loads(row["data"])
    role = row["type"]
    model = data.get("model") or {}
    base = {
        "message_id": row["id"], "role": role, "storage_schema": "opencode_v2",
        "timestamp": datetime.fromtimestamp(row["time_created"] / 1000).astimezone().isoformat(),
        "context_only": row["time_created"] < start_ms and row["time_updated"] < start_ms,
        "stored_after_cutoff": row["time_updated"] >= end_ms,
        "model": model.get("id"), "provider": model.get("providerID"),
        "agent_authored": role == "user" and bool(session["parent_id"]),
    }
    entries = []
    if role not in ("user", "assistant"):
        stats[f"omitted_message_type:{role}"] += 1
        return entries
    content = list(data.get("content") or [])
    if data.get("text"):
        content.insert(0, {"type": "text", "text": data["text"]})
    for number, part in enumerate(content):
        kind = part.get("type")
        times = part.get("time") or {}
        created = times.get("created", row["time_created"])
        completed = times.get("completed", row["time_updated"])
        if created >= end_ms:
            continue
        item = {**base, "type": kind, "part_id": part.get("id") or f"{row['id']}:{number}",
                "part_timestamp": datetime.fromtimestamp(created / 1000).astimezone().isoformat(),
                "context_only": created < start_ms and completed < start_ms,
                "stored_after_cutoff": base["stored_after_cutoff"] or completed >= end_ms}
        if kind == "text":
            text = part.get("text", "")
            for offset in range(0, len(text), 6000):
                entries.append(attach({**item, "text": text[offset:offset + 6000], "text_offset": offset,
                                       "text_length": len(text), "synthetic": part.get("synthetic", data.get("synthetic", False))},
                                      text if offset == 0 else "", session["directory"]))
        elif kind == "tool":
            state = part.get("state") or {}
            item.update(tool=part.get("name"), call_id=part.get("id"), status=state.get("status", "unknown"))
            values = {"input": state.get("input", {}), "output": state.get("content", state.get("output", ""))}
            if "error" in state:
                values["error"] = state["error"]
            for field, value in values.items():
                item[field] = excerpt(value, tool_chars)
                stats["tool_chars_omitted"] += item[field]["omitted_chars"]
            metadata = state.get("metadata") or {}
            attach(item, values["input"], session["directory"])
            attach(item, values["output"], session["directory"], results=True)
            if "error" in values:
                attach(item, values["error"], session["directory"], results=True)
            facts = structured_results(metadata) + structured_results(values["output"])
            if facts:
                item.setdefault("evidence", {}).setdefault("reported_results", []).extend(facts)
            entries.append(item)
            if not item["context_only"]:
                stats["tool_calls"] += 1
                stats["tool_errors"] += item["status"] == "error"
        elif kind in ("file", "image", "video"):
            item.update(filename=part.get("filename"), mime=part.get("mime") or part.get("mediaType"))
            ref = part.get("url") or part.get("path")
            if ref:
                item["evidence"] = {"media": [media_reference(ref, session["directory"])]}
            entries.append(item)
        else:
            stats[f"omitted_part_type:{kind}"] += 1
    if any(key in data for key in ("tokens", "cost", "finish", "error")):
        entries.append({**base, "type": "message_metadata",
                        **{key: data[key] for key in ("tokens", "cost", "finish") if key in data},
                        **({"error": excerpt(data["error"], tool_chars)} if data.get("error") else {})})
    return bound_entries(entries)


def collect(db, start, end, project, tool_chars, chunk_chars):
    start_ms, end_ms = int(start.timestamp() * 1000), int(end.timestamp() * 1000)
    sessions = {r["id"]: dict(r) for r in db.execute("SELECT * FROM session_v2")}
    active = db.execute(
        """SELECT DISTINCT session_id FROM session_message WHERE
           (time_created >= ? AND time_created < ?) OR (time_updated >= ? AND time_updated < ?)""",
        (start_ms, end_ms, start_ms, end_ms)).fetchall()
    results = []
    for selected in active:
        session = sessions[selected["session_id"]]
        root_key = root_id(session["id"], sessions)
        root = sessions.get(root_key, session)
        if (root["title"] or "").startswith("[session-review]"):
            continue
        if project and Path(root["directory"]).resolve() != project:
            continue
        rows = db.execute(
            """SELECT * FROM session_message WHERE session_id=? AND time_created < ?
               ORDER BY seq, id""", (session["id"], end_ms)).fetchall()
        messages = [r for r in rows if r["time_created"] >= start_ms or start_ms <= r["time_updated"] < end_ms]
        if not messages:
            continue
        context = [r for r in rows if r["seq"] < messages[0]["seq"] and r["type"] in ("user", "assistant")][-4:]
        stats, entries = Counter(), []
        for row in [*context, *messages]:
            entries.extend(normalize(row, session, start_ms, end_ms, tool_chars, stats))
        if not entries:
            continue
        results.append({
            "session_id": session["id"], "root_session_id": root_key, "parent_session_id": session["parent_id"],
            "fork_session_id": session.get("fork_session_id"), "title": session["title"],
            "project_id": root["project_id"], "directory": session["directory"], "root_directory": root["directory"],
            "message_count": len(messages), "context_message_count": len(context), "stats": dict(stats),
            "input_hash": hashlib.sha256(encode(entries).encode()).hexdigest(),
            "chunks": split_chunks(entries, chunk_chars),
        })
    return results
