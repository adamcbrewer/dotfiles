"""Optional T3 metadata joins for delegates absent from provider parent links."""

from contextlib import closing
import hashlib
import json
import sqlite3

from common import encode


def enrich(results, path, source):
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("BEGIN")
        threads = {row[0]: json.loads(row[1]) for row in db.execute(
            "SELECT thread_id, payload_json FROM orchestration_v2_projection_threads")}
        mapping = {}
        for tid, raw in db.execute(
                "SELECT thread_id, payload_json FROM orchestration_v2_projection_provider_threads"):
            native = json.loads(raw).get("nativeThreadRef") or {}
            if native.get("driver") == source and native.get("nativeId"):
                mapping[native["nativeId"]] = tid
    root_directories = {mapping[r["session_id"]]: r["directory"] for r in results if r["session_id"] in mapping}
    for result in results:
        tid = mapping.get(result["session_id"])
        if tid not in threads:
            continue
        thread = threads[tid]
        lineage = thread.get("lineage") or {}
        root = lineage.get("rootThreadId") or tid
        parent = lineage.get("parentThreadId")
        result.update(t3_thread_id=tid, root_session_id=f"t3:{root}",
                      title=thread.get("title", ""), project_id=thread.get("projectId") or result["project_id"])
        result["root_directory"] = (root_directories.get(root) or threads.get(root, {}).get("worktreePath")
                                    or result.get("root_directory", result["directory"]))
        if parent:
            result["parent_session_id"] = f"t3:{parent}"
            for chunk in result["chunks"]:
                for entry in chunk:
                    if entry["role"] == "user":
                        entry["agent_authored"] = True
        result["input_hash"] = hashlib.sha256(encode({
            "entries": [e for c in result["chunks"] for e in c],
            "root": result["root_session_id"], "project": result["project_id"],
        }).encode()).hexdigest()
    return [r for r in results if not threads.get(r.get("root_session_id", "").removeprefix("t3:"), {})
            .get("title", "").startswith("[session-review]")]
