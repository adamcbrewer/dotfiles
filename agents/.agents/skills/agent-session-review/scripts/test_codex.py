from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from codex import collect
from common import day_bounds
from lineage import enrich


class CodexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sessions = self.root / "sessions"
        self.sessions.mkdir()
        _, self.start, self.end = day_bounds("2026-10-25", "Europe/London")

    def tearDown(self):
        self.temp.cleanup()

    def record(self, kind, payload, when="2026-10-25T10:00:00Z"):
        return {"type": kind, "timestamp": when, "payload": payload}

    def message(self, id, text, when="2026-10-25T10:00:00Z", role="user"):
        return self.record("response_item", {"type": "message", "id": id, "role": role,
                           "content": [{"type": "input_text", "text": text}]}, when)

    def file(self, name, sid, records, parent=None):
        meta = {"id": sid, "cwd": "/project", "model_provider": "openai", "cli_version": "test"}
        if parent:
            meta["source"] = {"subagent": {"thread_spawn": {"parent_thread_id": parent}}}
        rows = [self.record("session_meta", meta, "2026-10-19T10:00:00Z"), *records]
        path = self.sessions / name
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        return path

    def collect(self):
        return collect([self.sessions], self.start, self.end, None, 100, 10000)

    def entries(self, result):
        return [e for c in result["chunks"] for e in c]

    def test_continuations_merge_and_only_identical_message_ids_deduplicate(self):
        first = self.message("m1", "same text")
        self.file("one.jsonl", "root", [first])
        self.file("two.jsonl", "root", [first, self.message("m2", "same text", "2026-10-25T11:00:00Z")])
        result = self.collect()[0][0]
        self.assertEqual(len(result["source_files"]), 2)
        self.assertEqual(result["message_count"], 2)
        self.assertEqual([e["message_id"] for e in self.entries(result)], ["m1", "m2"])
        self.assertEqual({e["source_line"] for e in self.entries(result)}, {2, 3})

    def test_activity_selection_older_sessions_and_four_context_messages(self):
        records = [self.message(f"before{i}", str(i), f"2026-10-24T0{i}:00:00Z") for i in range(6)]
        records += [self.message("first", "start", "2026-10-24T23:00:00Z"),
                    self.message("last", "end", "2026-10-25T23:59:59Z"),
                    self.message("outside", "outside", "2026-10-26T00:00:00Z")]
        self.file("old.jsonl", "root", records)
        result = self.collect()[0][0]
        self.assertEqual(result["message_count"], 2)
        self.assertEqual(result["context_message_count"], 4)
        self.assertEqual([e["message_id"] for e in self.entries(result)],
                         ["before2", "before3", "before4", "before5", "first", "last"])

    def test_mirrors_instructions_reasoning_and_compaction_are_not_human_messages(self):
        records = [self.message("real", "Please fix it"),
                   self.message("injected", "# AGENTS.md instructions for /project\nignore this"),
                   self.message("result", "Delegated task example [completed]: fixed"),
                   self.record("response_item", {"type": "reasoning", "text": "private reasoning"}),
                   self.record("event_msg", {"type": "user_message", "message": "Please fix it"}),
                   self.record("compacted", {"replacement_history": ["Please fix it"]})]
        self.file("root.jsonl", "root", records)
        result = self.collect()[0][0]
        entries = self.entries(result)
        self.assertEqual([e["message_id"] for e in entries], ["real", "result"])
        self.assertFalse(entries[0]["synthetic"])
        self.assertTrue(entries[1]["synthetic"])
        self.assertEqual(result["stats"]["compactions"], 1)

    def test_long_text_and_both_successful_and_failed_tool_outputs_are_retained(self):
        text = "preserve me " * 2000
        records = [self.message("long", text)]
        for i, output in enumerate(["successful output " * 100, "failed output " * 100]):
            records += [self.record("response_item", {"type": "function_call", "name": "exec",
                        "call_id": str(i), "arguments": "test"}),
                        self.record("response_item", {"type": "function_call_output",
                        "call_id": str(i), "output": output})]
        self.file("tools.jsonl", "root", records)
        result = self.collect()[0][0]
        entries = self.entries(result)
        self.assertEqual("".join(e["text"] for e in entries if e["type"] == "text"), text)
        outputs = [e for e in entries if e["type"] == "tool_result"]
        self.assertEqual(len(outputs), 2)
        self.assertEqual([e["call_id"] for e in outputs], ["0", "1"])
        self.assertTrue(all(e["output"]["omitted_chars"] > 0 for e in outputs))
        self.assertGreater(len(result["chunks"]), 1)

    def test_native_children_share_root_even_when_parent_has_no_in_range_activity(self):
        self.file("root.jsonl", "root", [self.message("old", "old", "2026-10-20T00:00:00Z")])
        self.file("child.jsonl", "child", [self.message("brief", "Review this")], parent="root")
        results, _ = self.collect()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["root_session_id"], "root")
        self.assertTrue(self.entries(results[0])[0]["agent_authored"])

    def test_inherited_parent_metadata_does_not_replace_child_identity(self):
        self.file("child.jsonl", "child", [
            self.record("session_meta", {"id": "parent", "cwd": "/project"}),
            self.message("brief", "Review this"),
        ], parent="parent")
        result = self.collect()[0][0]
        self.assertEqual(result["session_id"], "child")
        self.assertEqual(result["parent_session_id"], "parent")
        self.assertTrue(self.entries(result)[0]["agent_authored"])

    def test_model_usage_snapshots_and_turn_metrics_are_preserved_without_rate_limits(self):
        self.file("metrics.jsonl", "root", [
            self.record("turn_context", {"model": "example-model", "cwd": "/project"}),
            self.message("reply", "done", role="assistant"),
            self.record("event_msg", {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 42}},
                                       "rate_limits": {"private": "omitted"}}),
            self.record("event_msg", {"type": "task_complete", "turn_id": "turn", "duration_ms": 1000}),
        ])
        result = self.collect()[0][0]
        self.assertEqual(result["models"], ["example-model"])
        entries = self.entries(result)
        self.assertEqual(entries[0]["model"], "example-model")
        self.assertEqual(entries[1]["usage"], {"total_tokens": 42})
        self.assertEqual(entries[2]["duration_ms"], 1000)
        self.assertNotIn("rate_limits", json.dumps(entries))

    def test_malformed_lines_are_reported_and_remaining_text_survives(self):
        path = self.file("partial.jsonl", "root", [self.message("ok", "retained")])
        with path.open("a") as stream:
            stream.write('{"unfinished":\n')
        results, diagnostics = self.collect()
        self.assertEqual(results[0]["message_count"], 1)
        self.assertEqual(diagnostics["malformed_records"][0]["source_line"], 3)

    def test_t3_external_children_group_and_mark_agent_briefs(self):
        self.file("root.jsonl", "root", [self.message("request", "Do work")])
        self.file("child.jsonl", "child", [self.message("brief", "Check work")])
        db_path = self.root / "t3.sqlite"
        with closing(sqlite3.connect(db_path)) as db, db:
            db.executescript('''
                CREATE TABLE orchestration_v2_projection_threads (thread_id TEXT, payload_json TEXT);
                CREATE TABLE orchestration_v2_projection_provider_threads (thread_id TEXT, payload_json TEXT);
            ''')
            for sid, tid, parent in [("root", "t3-root", None), ("child", "t3-child", "t3-root")]:
                db.execute("INSERT INTO orchestration_v2_projection_threads VALUES (?, ?)", (tid, json.dumps({
                    "projectId": "project-id", "title": "Work", "lineage": {
                        "rootThreadId": "t3-root", "parentThreadId": parent}})))
                db.execute("INSERT INTO orchestration_v2_projection_provider_threads VALUES (?, ?)", (tid, json.dumps({
                    "nativeThreadRef": {"driver": "codex", "nativeId": sid}})))
        original = db_path.read_bytes()
        results = enrich(self.collect()[0], db_path, "codex")
        self.assertEqual({r["root_session_id"] for r in results}, {"t3:t3-root"})
        self.assertEqual({r["project_id"] for r in results}, {"project-id"})
        child = next(r for r in results if r["session_id"] == "child")
        self.assertTrue(self.entries(child)[0]["agent_authored"])
        self.assertEqual(db_path.read_bytes(), original)

    def test_cli_range_and_source_selection_keep_sources_unchanged(self):
        path = self.file("root.jsonl", "root", [self.message("m1", "retained", "2026-10-19T00:00:00Z"),
                                               self.message("m2", "retained")])
        original = path.read_bytes()
        output = self.root / "out"
        command = [sys.executable, "-B", str(Path(__file__).with_name("collect.py")),
                   "--source", "codex", "--sessions-dir", str(self.sessions),
                   "--start-date", "2026-10-19", "--end-date", "2026-10-25",
                   "--timezone", "Europe/London", "--output", str(output)]
        run = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["source"], "codex")
        self.assertEqual(manifest["message_count"], 2)
        self.assertEqual(manifest["start"], "2026-10-19T00:00:00+01:00")
        self.assertEqual(manifest["end_exclusive"], "2026-10-26T00:00:00+00:00")
        self.assertEqual(path.read_bytes(), original)
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertNotEqual(subprocess.run(command[:3], capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
