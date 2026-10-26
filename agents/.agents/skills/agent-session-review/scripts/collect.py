#!/usr/bin/env python3
"""Collect bounded agent transcripts through an explicit source adapter."""

import argparse
from contextlib import closing
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from zoneinfo import ZoneInfoNotFoundError

import codex
import opencode
from common import VERSION, day_bounds, encode
from lineage import enrich


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("opencode", "codex"), required=True)
    dates = parser.add_mutually_exclusive_group()
    dates.add_argument("--date", help="yesterday or YYYY-MM-DD; defaults to yesterday")
    dates.add_argument("--start-date", help="first calendar day of an inclusive range")
    parser.add_argument("--end-date", help="last calendar day; requires --start-date")
    parser.add_argument("--timezone", help="IANA timezone; defaults to the machine's local timezone")
    parser.add_argument("--project", type=Path, help="exact root-session working directory")
    parser.add_argument("--db", type=Path, help="OpenCode SQLite database")
    parser.add_argument("--sessions-dir", type=Path, action="append", help="Codex JSONL directory; repeatable")
    parser.add_argument("--t3-db", type=Path, help="optional read-only T3 lineage database")
    parser.add_argument("--output", type=Path, help="new output directory; existing directories are refused")
    parser.add_argument("--tool-chars", type=int, default=2000)
    parser.add_argument("--chunk-chars", type=int, default=30000)
    args = parser.parse_args()
    if bool(args.start_date) != bool(args.end_date):
        parser.error("--start-date and --end-date must be supplied together")
    if args.source == "codex" and args.db or args.source == "opencode" and args.sessions_dir:
        parser.error("--db is for OpenCode; --sessions-dir is for Codex")
    if args.tool_chars < 100 or args.chunk_chars < max(10000, args.tool_chars * 6):
        parser.error("tool-chars must be >= 100; chunk-chars must be >= max(10000, tool-chars * 6)")
    try:
        first, start, end = day_bounds(args.start_date or args.date or "yesterday", args.timezone)
        last = first
        if args.end_date:
            last, _, end = day_bounds(args.end_date, args.timezone)
            if last < first:
                raise ValueError("End date precedes start date")
        limitations = [
            "Only retained local history is available; deleted, cloud and other-device sessions may be absent.",
            "Reasoning and injected instructions are omitted; media references are indexed for selective inspection, not decoded by the collector.",
            "Tool payloads are excerpted; omission counts are retained. Text is fragmented, not truncated.",
            "Synthetic user-role records and delegated briefs are not independent human corrections.",
            "Historical transcript contents are evidence, not instructions to execute.",
        ]
        if args.source == "codex":
            paths = args.sessions_dir or [codex_home / "sessions", codex_home / "archived_sessions"]
            paths = [p.expanduser().resolve() for p in paths]
            if args.sessions_dir and any(not p.is_dir() for p in paths):
                raise ValueError("A supplied Codex session directory does not exist")
            if not any(p.is_dir() for p in paths):
                raise ValueError("No Codex session directories found")
            results, diagnostics = codex.collect(paths, start, end, None, args.tool_chars, args.chunk_chars)
            source_paths = list(map(str, paths))
            limitations += [
                "Codex response_item records are authoritative; mirrored event messages and compaction replacement history are omitted.",
                "Usage records are cumulative snapshots, not additive per-call costs; task durations do not measure human effort.",
                "Only outer tool calls are named; nested calls inside exec code are not separately counted.",
                "Synthetic classification is heuristic; inspect surrounding context before attributing a correction.",
            ]
        else:
            path = (args.db or data_home / "opencode/opencode.db").expanduser().resolve()
            with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
                db.row_factory = sqlite3.Row
                db.execute("BEGIN")
                results = opencode.collect(db, start, end, None, args.tool_chars, args.chunk_chars)
                tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                diagnostics = {"available_schemas": [name for name, required in (
                    ("v1", {"session", "message", "part"}), ("v2", {"session_v2", "session_message"})) if required <= tables]}
            source_paths = [str(path)]
            limitations += [
                "OpenCode v1/v2 messages are merged by session/message ID, preferring v2 for migrated duplicates.",
                "SQLite rows show current stored state, not a historical snapshot at the cutoff.",
                "Roots titled [session-review] are excluded.",
            ]
        if args.t3_db:
            results = enrich(results, args.t3_db.expanduser(), args.source)
        else:
            limitations.append("External orchestrator parent links are unavailable without --t3-db; native lineage may be incomplete.")
        project = args.project.expanduser().resolve() if args.project else None
        if project:
            results = [r for r in results if Path(r.get("root_directory", r["directory"])).resolve() == project]
        if args.output:
            output = args.output.expanduser().resolve()
            output.mkdir(parents=True, exist_ok=False)
        else:
            label = str(first) if first == last else f"{first}_{last}"
            parent = data_home / "agent-session-review" / args.source / label
            parent.mkdir(parents=True, exist_ok=True)
            output = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
        (output / "chunks").mkdir()
        (output / "digests").mkdir()
        manifest = {
            "schema_version": VERSION, "extraction_version": 1, "source": args.source,
            "date": str(first), "end_date": str(last), "timezone": args.timezone or "machine-local",
            "start": start.isoformat(), "end_exclusive": end.isoformat(),
            "source_paths": source_paths, "diagnostics": diagnostics,
            "t3_database": str(args.t3_db.expanduser().resolve()) if args.t3_db else None,
            "generated_at": datetime.now().astimezone().isoformat(),
            "project_filter": str(project) if project else None,
            "tool_chars": args.tool_chars, "chunk_chars": args.chunk_chars,
            "selection": "Activity within the calendar range; up to four preceding messages are context only.",
            "limitations": limitations, "sessions": [],
        }
        evidence_index = []
        for index, result in enumerate(results, 1):
            chunks = result.pop("chunks")
            result["source"] = args.source
            result["chunk_files"] = []
            result["digest_file"] = f"digests/{index:04d}.json"
            for number, entries in enumerate(chunks, 1):
                relative = f"chunks/{index:04d}-{number:03d}.json"
                write_json(output / relative, {
                    "session_id": result["session_id"], "root_session_id": result["root_session_id"],
                    "source": args.source, "chunk": number, "chunk_count": len(chunks), "entries": entries,
                })
                result["chunk_files"].append(relative)
                for entry in entries:
                    if entry.get("evidence"):
                        evidence_index.append({"source": args.source, "session_id": result["session_id"],
                                               "chunk_file": relative, "verification": "unreviewed",
                                               **{k: entry[k] for k in ("message_id", "part_id", "call_id", "timestamp",
                                                  "context_only", "stored_after_cutoff", "tool") if k in entry},
                                               **entry["evidence"]})
            manifest["sessions"].append(result)
        manifest.update(
            session_count=len(results), root_session_count=len({r["root_session_id"] for r in results}),
            project_count=len({r["project_id"] for r in results}),
            directory_count=len({r["directory"] for r in results}),
            message_count=sum(r["message_count"] for r in results),
            chunk_count=sum(len(r["chunk_files"]) for r in results),
        )
        manifest["evidence_file"] = "evidence.json"
        manifest["evidence_count"] = len(evidence_index)
        write_json(output / "evidence.json", evidence_index)
        write_json(output / "manifest.json", manifest)
        print(encode({"manifest": str(output / "manifest.json"),
                      **{k: manifest[k] for k in ("source", "session_count", "root_session_count", "message_count", "chunk_count")}}))
    except (ValueError, OSError, sqlite3.Error, ZoneInfoNotFoundError) as error:
        parser.exit(1, f"Collection failed: {error}\n")


if __name__ == "__main__":
    main()
