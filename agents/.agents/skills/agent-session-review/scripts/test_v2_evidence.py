import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from common import day_bounds, encode
from evidence import scan, media_reference, bound_entries
from opencode import collect


class V2Tests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
            CREATE TABLE session_v2 (id TEXT, parent_id TEXT, fork_session_id TEXT, title TEXT, project_id TEXT, directory TEXT);
            CREATE TABLE session_message (id TEXT, session_id TEXT, type TEXT, seq INTEGER, time_created INTEGER, time_updated INTEGER, data TEXT);
            INSERT INTO session_v2 VALUES ('root', NULL, NULL, 'Work', 'project', '/project');
        ''')
        _, self.start, self.end = day_bounds("2026-10-25", "Europe/London")
        self.start_ms, self.end_ms = int(self.start.timestamp()*1000), int(self.end.timestamp()*1000)

    def tearDown(self):
        self.db.close()

    def message(self, id, seq, data, role="assistant", created=None, updated=None, sid="root"):
        created = self.start_ms if created is None else created
        self.db.execute('INSERT INTO session_message VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (id, sid, role, seq, created, updated if updated is not None else created, json.dumps(data)))

    def collect(self, project=None):
        return collect(self.db, self.start, self.end, project, 100, 10000)

    def entries(self, result):
        return [e for chunk in result['chunks'] for e in chunk]

    def test_v2_text_tool_metadata_and_reasoning_omission(self):
        self.message('user', 0, {'text': 'Please check'}, role='user')
        self.message('reply', 1, {'model': {'id': 'model', 'providerID': 'provider'}, 'tokens': {'output': 20}, 'content': [
            {'type': 'reasoning', 'text': 'omit me'},
            {'type': 'text', 'text': 'Checking'},
            {'type': 'tool', 'id': 'call', 'name': 'bash', 'state': {'status': 'completed',
             'input': {'command': 'pytest'}, 'content': [{'type': 'text', 'text': '3 passed'}], 'metadata': {'exit': 0}}},
        ]})
        entries = self.entries(self.collect()[0])
        self.assertNotIn('omit me', json.dumps(entries))
        tool = next(e for e in entries if e['type'] == 'tool')
        self.assertEqual(tool['tool'], 'bash')
        self.assertIn({'kind': 'process_exit', 'exit_code': 0}, tool['evidence']['reported_results'])
        self.assertEqual(next(e for e in entries if e['type'] == 'message_metadata')['tokens'], {'output': 20})

    def test_updated_tool_on_old_message_and_cutoff_exclusion(self):
        self.message('old', 0, {'content': [
            {'type': 'tool', 'id': 'call', 'name': 'bash', 'time': {'created': self.start_ms-10, 'completed': self.start_ms+10},
             'state': {'status': 'completed', 'content': [{'type': 'text', 'text': 'OK'}]}}]},
            created=self.start_ms-10, updated=self.start_ms+10)
        self.message('future', 1, {'text': 'too late'}, role='user', created=self.end_ms)
        result = self.collect()[0]
        self.assertEqual(result['message_count'], 1)
        self.assertFalse(self.entries(result)[0]['context_only'])
        self.assertNotIn('too late', json.dumps(result))

    def test_state_updated_after_cutoff_is_flagged(self):
        self.message('reply', 0, {'content': [{'type': 'text', 'text': 'later state'}]}, updated=self.end_ms+100)
        self.assertTrue(self.entries(self.collect()[0])[0]['stored_after_cutoff'])

    def test_native_child_grouping_and_project_filter(self):
        self.db.execute("INSERT INTO session_v2 VALUES ('child', 'root', NULL, 'Review', 'project', '/other')")
        self.message('brief', 0, {'text': 'Review'}, role='user', sid='child')
        result = self.collect(Path('/project'))[0]
        self.assertEqual(result['root_session_id'], 'root')
        self.assertTrue(self.entries(result)[0]['agent_authored'])
        self.assertEqual(self.collect(Path('/unknown')), [])

    def test_mixed_database_prefers_migrated_v2_message_and_keeps_v1_only_message(self):
        self.db.executescript('''
            CREATE TABLE session (id TEXT, parent_id TEXT, title TEXT, project_id TEXT, directory TEXT);
            CREATE TABLE message (id TEXT, session_id TEXT, time_created INTEGER, data TEXT);
            CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, time_created INTEGER, data TEXT);
            INSERT INTO session VALUES ('root', NULL, 'Work', 'project', '/project');
        ''')
        for id, text in [('shared', 'old copy'), ('legacy', 'legacy only')]:
            self.db.execute('INSERT INTO message VALUES (?, ?, ?, ?)', (id, 'root', self.start_ms, '{"role":"user"}'))
            self.db.execute('INSERT INTO part VALUES (?, ?, ?, ?, ?)',
                            (id+'-part', id, 'root', self.start_ms, json.dumps({'type':'text','text':text})))
        self.message('shared', 0, {'text': 'new copy'}, role='user')
        self.message('modern', 1, {'text': 'v2 only'}, role='user')
        results = self.collect()
        self.assertEqual(len(results), 1)
        texts = [e['text'] for e in self.entries(results[0]) if e['type']=='text']
        self.assertCountEqual(texts, ['new copy', 'legacy only', 'v2 only'])
        self.assertEqual(results[0]['message_count'], 3)

    def test_parent_in_v1_still_groups_and_filters_v2_child(self):
        self.db.executescript('''
            CREATE TABLE session (id TEXT, parent_id TEXT, title TEXT, project_id TEXT, directory TEXT);
            CREATE TABLE message (id TEXT, session_id TEXT, time_created INTEGER, data TEXT);
            CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, time_created INTEGER, data TEXT);
            INSERT INTO session VALUES ('parent', NULL, 'Parent', 'project', '/parent');
            UPDATE session_v2 SET parent_id='parent', directory='/child' WHERE id='root';
        ''')
        self.message('brief', 0, {'text': 'Review'}, role='user')
        result = self.collect(Path('/parent'))[0]
        self.assertEqual(result['root_session_id'], 'parent')
        self.assertEqual(result['root_directory'], '/parent')

    def test_v2_attachment_and_updated_old_text_are_retained(self):
        self.message('edited', 0, {'text': 'updated text', 'content': [
            {'type': 'file', 'url': 'file:///missing/recording.mp4', 'mime': 'video/mp4'}]},
            role='user', created=self.start_ms-100, updated=self.start_ms+10)
        entries = self.entries(self.collect()[0])
        self.assertFalse(entries[0]['context_only'])
        attachment = next(e for e in entries if e['type']=='file')
        self.assertEqual(attachment['evidence']['media'][0]['availability'], 'missing_or_unreadable')

    def test_long_text_survives_with_source_ids(self):
        text = 'long text ' * 2500
        self.message('long', 0, {'text': text}, role='user')
        entries = self.entries(self.collect()[0])
        self.assertEqual(''.join(e['text'] for e in entries), text)
        self.assertEqual({e['message_id'] for e in entries}, {'long'})
        self.assertEqual({e['storage_schema'] for e in entries}, {'opencode_v2'})

    def test_structured_tool_summary_survives_long_output(self):
        self.message('tool', 0, {'content': [{'type': 'tool', 'id': 'call', 'name': 'bash',
            'state': {'status': 'completed', 'input': {'command': 'pytest'},
                      'content': [{'type': 'text', 'text': 'noise '*500+'\n3 passed\n'}]}}]})
        tool = self.entries(self.collect()[0])[0]
        self.assertEqual(tool['evidence']['result_lines'], ['3 passed'])
        self.assertGreater(tool['output']['omitted_chars'], 0)

    def test_large_evidence_lists_remain_bounded_and_report_omissions(self):
        refs = ' '.join(f'https://example.com/screen-{i}.png' for i in range(1000))
        self.message('tool', 0, {'content': [{'type': 'tool', 'id': 'call', 'name': 'bash',
            'state': {'status': 'completed', 'content': [{'type': 'text', 'text': refs}]}}]})
        result = self.collect()[0]
        self.assertTrue(all(len(encode(chunk)) < 10000 for chunk in result['chunks']))
        evidence = self.entries(result)[0]['evidence']
        self.assertEqual(len(evidence['media']) + evidence['media_omitted'], 1000)
        self.assertGreater(evidence['media_omitted'], 0)


class EvidenceTests(unittest.TestCase):
    def test_nested_json_output_retains_individual_summary_lines(self):
        value = {'output': json.dumps([{'type': 'text', 'text': 'noise '*500+'\nRan 3 tests\nOK\n'}])}
        result = scan(json.dumps(value), '/', results=True)
        self.assertEqual(result['result_lines'], ['Ran 3 tests', 'OK'])

    def test_large_pr_check_list_keeps_state_and_reports_omissions(self):
        value = {'url': 'https://github.com/owner/repo/pull/12', 'state': 'MERGED',
                 'statusCheckRollup': [{'name': f'check-{i}', 'conclusion': 'SUCCESS'} for i in range(1000)]}
        entry = {'evidence': scan(value, '/', results=True)}
        evidence = bound_entries([entry])[0]['evidence']
        fact = evidence['reported_results'][0]
        self.assertEqual(fact['state'], 'MERGED')
        self.assertEqual(len(fact['checks']) + fact['checks_omitted'], 1000)
        self.assertLess(len(encode(entry)), 4000)

    def test_media_spaces_missing_recording_and_remote_without_fetching(self):
        with tempfile.TemporaryDirectory() as folder:
            image = Path(folder)/'screen shot.png'
            image.write_bytes(b'fixture')
            result = scan(f'![Screen]({image}) and {folder}/recording.webm and https://example.com/screen.png', folder)
            media = result['media']
            self.assertIn({'path': str(image), 'availability': 'local_file', 'size_bytes': 7, 'mtime_ns': image.stat().st_mtime_ns}, media)
            self.assertTrue(any(m['availability']=='missing_or_unreadable' for m in media))
            self.assertTrue(any(m['availability']=='remote_not_fetched' for m in media))

    def test_embedded_image_payload_is_not_copied(self):
        result = media_reference('data:image/png;base64,SECRET_BYTES', '/')
        self.assertEqual(result, {'availability': 'embedded_not_extracted', 'media_type': 'image/png'})

    def test_claim_and_pr_link_are_not_confirmed_outcomes(self):
        result = scan('3 passed; merged https://github.com/owner/repo/pull/12', '/', results=False)
        self.assertNotIn('reported_results', result)
        self.assertNotIn('result_lines', result)
        self.assertEqual(result['pull_requests'][0]['verification'], 'link_only')

    def test_structured_pr_state_and_process_exit_survive_bounded_output(self):
        value = {'exit_code': 0, 'output': json.dumps({'url': 'https://github.com/owner/repo/pull/12',
                 'state': 'MERGED', 'mergedAt': '2026-10-25T10:00:00Z', 'headRefOid': 'abc',
                 'statusCheckRollup': [{'name': 'tests', 'conclusion': 'SUCCESS'}]})}
        result = scan(json.dumps(value), '/', results=True)
        self.assertIn({'kind': 'process_exit', 'exit_code': 0}, result['reported_results'])
        pr = next(f for f in result['reported_results'] if f['kind']=='pull_request_state')
        self.assertEqual(pr['state'], 'MERGED')
        self.assertEqual(pr['headRefOid'], 'abc')
        self.assertEqual(pr['checks'], [{'name': 'tests', 'conclusion': 'SUCCESS'}])

    def test_test_summary_is_reported_evidence_not_a_verification_verdict(self):
        result = scan('Running tests\n3 passed, 1 skipped\n', '/', results=True)
        self.assertEqual(result['result_lines'], ['3 passed, 1 skipped'])
        self.assertNotIn('confirmed', result)


if __name__ == '__main__':
    unittest.main()
