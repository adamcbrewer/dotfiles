"""Normalize local Codex rollout JSONL without executing transcript contents."""

from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path

from common import encode, excerpt, root_id, split_chunks
from evidence import attach, bound_entries, media_reference


INJECTED = ("# AGENTS.md instructions", "<environment_context>", "<permissions instructions>")
SYNTHETIC = (
    "<turn_aborted>", "<subagent_notification>", "You are performing a CONTEXT CHECKPOINT",
    "[Request interrupted", "Delegated task ", "Update on pull request ",
    "Continue the user's", "Continue user request", "Continue the authorized",
    "Continue implementing GitHub issue", "Worktree handoff continuation", "[Worktree",
)


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Codex record has no timezone")
    return parsed


def text_content(content):
    if isinstance(content, str):
        return content
    return "\n".join(part.get("text", "") for part in content if isinstance(part, dict))


def load_sessions(paths, end):
    sessions, diagnostics = {}, {"files_scanned": 0, "malformed_records": [], "unrecognized_files": [], "files_after_cutoff": 0}
    files = sorted({f.resolve() for p in paths for f in p.rglob("*.jsonl")})
    for path in files:
        diagnostics["files_scanned"] += 1
        session = None
        recognized_meta = False
        with path.open() as stream:
            for line_number, line in enumerate(stream, 1):
                try:
                    record = json.loads(line)
                    payload = record["payload"]
                    stamp = timestamp(record["timestamp"])
                    if not isinstance(payload, dict):
                        raise ValueError("Non-object payload")
                    if record["type"] == "session_meta":
                        if recognized_meta:
                            continue
                        recognized_meta = True
                        if stamp >= end:
                            diagnostics["files_after_cutoff"] += 1
                            break
                        sid = payload.get("id") or payload["session_id"]
                        source = payload.get("source")
                        subagent = source.get("subagent", {}) if isinstance(source, dict) else {}
                        spawn = subagent.get("thread_spawn", {}) if isinstance(subagent, dict) else {}
                        parent = payload.get("parent_thread_id") or spawn.get("parent_thread_id")
                        session = sessions.setdefault(sid, {
                            "id": sid, "parent_id": parent, "directory": payload.get("cwd", "unknown"),
                            "records": [], "source_files": [], "seen": set(),
                            "provider": payload.get("model_provider"), "cli_version": payload.get("cli_version"),
                        })
                        session["source_files"].append(str(path))
                    elif session is not None and stamp < end:
                        identity = (record["type"], payload.get("id") or record["timestamp"], encode(payload))
                        if identity not in session["seen"]:
                            session["seen"].add(identity)
                            session["records"].append((stamp, str(path), line_number, record))
                except (ValueError, KeyError, TypeError, AttributeError) as error:
                    diagnostics["malformed_records"].append({
                        "source_file": str(path), "source_line": line_number, "error": type(error).__name__,
                    })
        if not recognized_meta:
            diagnostics["unrecognized_files"].append(str(path))
    return sessions, diagnostics


def normalize(session, start, end, tool_chars):
    entries, stats, models = [], Counter(), set()
    model = None
    for stamp, path, line, record in sorted(session["records"]):
        payload, kind = record["payload"], record["type"]
        active = start <= stamp < end
        base = {
            "message_id": payload.get("id") or f"{session['id']}:{Path(path).name}:{line}",
            "timestamp": stamp.isoformat(), "source_file": path, "source_line": line,
            "context_only": not active, "model": model, "provider": session["provider"],
        }
        if kind == "turn_context":
            model = payload.get("model", model)
            if active and model:
                models.add(model)
            continue
        if kind == "compacted":
            stats["compactions"] += int(active)
            continue
        if kind == "event_msg":
            event_type = payload.get("type")
            if active and event_type == "token_count":
                info = payload.get("info") or {}
                usage = {k: v for k, v in (info.get("total_token_usage") or {}).items()
                         if isinstance(v, (int, float)) and not isinstance(v, bool)}
                entries.append({**base, "role": "metadata", "type": "usage_snapshot", "usage": usage})
            elif active and event_type in ("task_complete", "task_started"):
                entries.append({**base, "role": "metadata", "type": event_type,
                                "turn_id": payload.get("turn_id") or payload.get("root_turn_id"),
                                **{k: payload[k] for k in ("duration_ms", "time_to_first_token_ms")
                                   if isinstance(payload.get(k), (int, float))}})
            continue
        if kind != "response_item":
            stats[f"omitted_record_type:{kind}"] += int(active)
            continue
        item_type = payload.get("type")
        if item_type == "message" and payload.get("role") in ("user", "assistant"):
            role = payload["role"]
            content = payload.get("content", [])
            text = text_content(content)
            if text.startswith(INJECTED) or payload.get("phase") == "analysis":
                stats["injected_or_analysis_messages"] += int(active)
                continue
            synthetic = role == "user" and (text.startswith(SYNTHETIC) or "Message Type: FINAL_ANSWER" in text[:100])
            for offset in range(0, len(text), 6000):
                entries.append(attach({**base, "role": role, "type": "text", "text": text[offset:offset + 6000],
                                "text_offset": offset, "text_length": len(text),
                                "phase": payload.get("phase"), "synthetic": synthetic,
                                "agent_authored": role == "user" and bool(session["parent_id"])},
                                      text if offset == 0 else "", session["directory"]))
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") in ("input_image", "image", "input_audio"):
                        item = {**base, "role": role, "type": "file", "media_type": part["type"]}
                        ref = part.get("image_url") or part.get("url") or part.get("path")
                        if isinstance(ref, dict):
                            ref = ref.get("url")
                        if isinstance(ref, str):
                            item["evidence"] = {"media": [media_reference(ref, session["directory"])]}
                        entries.append(item)
            stats["messages"] += int(active)
        elif active and item_type in ("function_call", "custom_tool_call"):
            field = "arguments" if item_type == "function_call" else "input"
            value = excerpt(payload.get(field, ""), tool_chars)
            entries.append(attach({**base, "role": "assistant", "type": "tool_call", "tool": payload.get("name"),
                                   "call_id": payload.get("call_id"), "input": value},
                                  payload.get(field, ""), session["directory"]))
            stats["tool_calls"] += 1
            stats["tool_chars_omitted"] += value["omitted_chars"]
        elif active and item_type in ("function_call_output", "custom_tool_call_output"):
            output = payload.get("output", "")
            value = excerpt(output, tool_chars)
            entries.append(attach({**base, "role": "tool", "type": "tool_result",
                                   "call_id": payload.get("call_id"), "output": value},
                                  output, session["directory"], results=True))
            stats["tool_chars_omitted"] += value["omitted_chars"]
        else:
            stats[f"omitted_item_type:{item_type}"] += int(active)
    active_entries = [e for e in entries if not e["context_only"]]
    context_ids = list(dict.fromkeys(e["message_id"] for e in entries if e["context_only"]))[-4:]
    context = [e for e in entries if e["context_only"] and e["message_id"] in context_ids]
    return bound_entries(context + active_entries), stats, sorted(models)


def collect(paths, start, end, project, tool_chars, chunk_chars):
    sessions, diagnostics = load_sessions(paths, end)
    results = []
    for sid, session in sorted(sessions.items()):
        root_key = root_id(sid, sessions)
        root = sessions.get(root_key, session)
        if project and Path(root["directory"]).resolve() != project:
            continue
        entries, stats, models = normalize(session, start, end, tool_chars)
        if not any(not e["context_only"] for e in entries):
            continue
        results.append({
            "session_id": sid, "root_session_id": root_key, "parent_session_id": session["parent_id"],
            "project_id": root["directory"], "directory": session["directory"], "root_directory": root["directory"],
            "source_files": session["source_files"], "models": models, "cli_version": session["cli_version"],
            "message_count": stats.pop("messages", 0),
            "context_message_count": len({e["message_id"] for e in entries if e["context_only"]}),
            "stats": dict(stats), "input_hash": hashlib.sha256(encode(entries).encode()).hexdigest(),
            "chunks": split_chunks(entries, chunk_chars),
        })
    return results, diagnostics
