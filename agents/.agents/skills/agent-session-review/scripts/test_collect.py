from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from opencode import collect
from common import day_bounds, split_chunks


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "sessions.db"
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE session (id TEXT, parent_id TEXT, title TEXT, project_id TEXT, directory TEXT);
            CREATE TABLE message (id TEXT, session_id TEXT, time_created INTEGER, data TEXT);
            CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, time_created INTEGER, data TEXT);
        """)
        _, self.start, self.end = day_bounds("2026-10-06", "Europe/London")
        self.start_ms = int(self.start.timestamp() * 1000)
        self.end_ms = int(self.end.timestamp() * 1000)
        self.db.execute("INSERT INTO session VALUES ('root', NULL, 'Work', 'project', '/project')")

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def message(self, id, timestamp, text="hello", session="root"):
        self.db.execute("INSERT INTO message VALUES (?, ?, ?, ?)",
                        (id, session, timestamp, json.dumps({"role": "user"})))
        self.part(id + "-text", id, timestamp, {"type": "text", "text": text}, session)

    def part(self, id, message, timestamp, data, session="root"):
        self.db.execute("INSERT INTO part VALUES (?, ?, ?, ?, ?)",
                        (id, message, session, timestamp, json.dumps(data)))

    def results(self, db=None, project=None):
        return collect(db or self.db, self.start, self.end, project, 100, 10000)

    def test_midnight_selection_and_preceding_context(self):
        self.message("before", self.start_ms - 1)
        self.message("start", self.start_ms)
        self.message("last", self.end_ms - 1)
        self.message("after", self.end_ms)
        result = self.results()[0]
        self.assertEqual(result["message_count"], 2)
        entries = [entry for chunk in result["chunks"] for entry in chunk]
        self.assertEqual([e["message_id"] for e in entries], ["before", "start", "last"])
        self.assertEqual([e["context_only"] for e in entries], [True, False, False])

    def test_new_part_on_old_message_is_included(self):
        self.message("old", self.start_ms - 1000)
        self.part("continued", "old", self.start_ms + 1000,
                  {"type": "text", "text": "continuation"})
        result = self.results()[0]
        entries = result["chunks"][0]
        self.assertEqual(result["message_count"], 1)
        self.assertTrue(entries[0]["context_only"])
        self.assertFalse(entries[1]["context_only"])

    def test_existing_tool_completed_in_range_is_activity(self):
        self.message("old", self.start_ms - 1000)
        self.part("tool", "old", self.start_ms - 500, {
            "type": "tool", "tool": "bash", "state": {"status": "completed",
            "time": {"end": self.start_ms + 100}, "output": "3 passed"},
        })
        result = self.results()[0]
        entries = [e for chunk in result["chunks"] for e in chunk]
        self.assertEqual(result["message_count"], 1)
        self.assertTrue(entries[0]["context_only"])
        self.assertFalse(entries[1]["context_only"])
        self.assertEqual(result["stats"]["tool_calls"], 1)

    def test_existing_text_updated_in_range_is_activity(self):
        self.db.execute("ALTER TABLE message ADD COLUMN time_updated INTEGER")
        self.db.execute("ALTER TABLE part ADD COLUMN time_updated INTEGER")
        self.db.execute("INSERT INTO message VALUES (?, 'root', ?, ?, ?)",
                        ("edited", self.start_ms - 1000, '{"role":"user"}', self.start_ms + 10))
        self.db.execute("INSERT INTO part VALUES (?, ?, 'root', ?, ?, ?)",
                        ("text", "edited", self.start_ms - 1000,
                         '{"type":"text","text":"updated"}', self.start_ms + 10))
        result = self.results()[0]
        self.assertEqual(result["message_count"], 1)
        self.assertFalse(result["chunks"][0][0]["context_only"])

    def test_child_grouping_and_project_filter(self):
        self.db.execute("INSERT INTO session VALUES ('child', 'root', 'Research', 'project', '/elsewhere')")
        self.message("child-message", self.start_ms, session="child")
        result = self.results(project=Path("/project"))[0]
        self.assertEqual(result["root_session_id"], "root")
        self.assertEqual(result["directory"], "/project")
        self.assertEqual(self.results(project=Path("/other")), [])

    def test_text_is_preserved_and_tools_are_explicitly_excerpted(self):
        text = "important correction " * 1000
        self.message("long", self.start_ms, text)
        self.part("tool", "long", self.start_ms, {
            "type": "tool", "tool": "bash",
            "state": {"status": "error", "input": {"command": "test"}, "error": "x" * 1000},
        })
        result = self.results()[0]
        entries = [e for chunk in result["chunks"] for e in chunk]
        fragments = sorted((e for e in entries if e["type"] == "text"), key=lambda e: e["text_offset"])
        self.assertEqual("".join(e["text"] for e in fragments), text)
        tool = next(e for e in entries if e["type"] == "tool")
        self.assertEqual(tool["error"]["omitted_chars"], 900)
        self.assertEqual(result["stats"]["tool_errors"], 1)
        self.assertGreater(len(result["chunks"]), 1)
        self.assertEqual(sum(map(len, split_chunks(entries, 10000))), len(entries))

    def test_read_only_database_and_review_exclusion(self):
        self.message("work", self.start_ms)
        self.db.execute("INSERT INTO session VALUES ('review', NULL, '[session-review] yesterday', 'project', '/project')")
        self.message("review-message", self.start_ms, session="review")
        self.db.commit()
        with closing(sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)) as readonly:
            readonly.row_factory = sqlite3.Row
            readonly.execute("BEGIN")
            self.assertEqual([r["session_id"] for r in self.results(readonly)], ["root"])
            with self.assertRaises(sqlite3.OperationalError):
                readonly.execute("DELETE FROM message")
        self.assertEqual(self.db.execute("SELECT count(*) FROM message").fetchone()[0], 2)

    def test_dst_uses_calendar_day_not_fixed_24_hours(self):
        _, start, end = day_bounds("2026-03-29", "Europe/London")
        self.assertEqual(end.timestamp() - start.timestamp(), 23 * 3600)
        _, start, end = day_bounds("2026-10-25", "Europe/London")
        self.assertEqual(end.timestamp() - start.timestamp(), 25 * 3600)

    def test_cli_writes_complete_manifest_and_refuses_existing_output(self):
        self.message("work", self.start_ms)
        self.db.commit()
        output = Path(self.temp.name) / "output"
        command = [
            sys.executable, "-B", str(Path(__file__).with_name("collect.py")),
            "--source", "opencode", "--db", str(self.path), "--date", "2026-10-06", "--timezone", "Europe/London",
            "--output", str(output),
        ]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        info = json.loads(result.stdout)
        manifest = json.loads(Path(info["manifest"]).read_text())
        self.assertEqual(manifest["message_count"], 1)
        self.assertEqual(json.loads((output / manifest["evidence_file"]).read_text()), [])
        self.assertEqual(manifest["start"], "2026-10-06T00:00:00+01:00")
        chunk = json.loads((output / manifest["sessions"][0]["chunk_files"][0]).read_text())
        self.assertEqual(chunk["entries"][0]["message_id"], "work")
        original_manifest = (output / "manifest.json").read_bytes()
        rerun = subprocess.run(command, text=True, capture_output=True)
        self.assertNotEqual(rerun.returncode, 0)
        self.assertEqual((output / "manifest.json").read_bytes(), original_manifest)

    def test_incomplete_database_reports_missing_table_set(self):
        with closing(sqlite3.connect(":memory:")) as db:
            db.execute("CREATE TABLE session_v2 (id TEXT)")
            with self.assertRaisesRegex(ValueError, "No complete supported"):
                self.results(db)

    def test_empty_day_has_explicit_zero_coverage(self):
        self.assertEqual(self.results(), [])


if __name__ == "__main__":
    unittest.main()
