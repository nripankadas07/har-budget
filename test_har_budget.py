import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from har_budget import evaluate, summarize, read_json


def capture(entries):
    return {'log': {'version': '1.2', 'entries': entries}}


def entry(url='https://example.test/path?token=secret', time=10, body=100, headers=20):
    return {'request': {'url': url, 'cookies': [{'value': 'secret-cookie'}]}, 'response': {'bodySize': body, 'headersSize': headers, 'content': {'text': 'secret-body', 'size': 5000}}, 'time': time}


class HarBudgetTests(unittest.TestCase):
    def test_origin_normalization_privacy_and_actual_bytes(self):
        groups = summarize(capture([entry('https://user:pass@EXAMPLE.test:443/x?secret=1#fragment'), entry()]))
        self.assertEqual(groups[0]['origin'], 'https://example.test')
        self.assertEqual(groups[0]['transfer_bytes'], 240)
        for secret in ['pass', 'user', 'secret', 'fragment', 'path']:
            self.assertNotIn(secret, json.dumps(groups))

    def test_unknown_is_not_zero_and_gates(self):
        groups = summarize(capture([entry(body=-1)]))
        self.assertEqual(groups[0]['unknown_sizes'], 1)
        self.assertEqual(len(evaluate(groups, {})['violations']), 1)
        self.assertEqual(evaluate(groups, {}, True)['violations'], [])

    def test_cache_transfer_extension_and_p95(self):
        entries = [entry(time=i) for i in range(1, 21)]
        entries[0]['response']['_transferSize'] = 0
        groups = summarize(capture(entries))
        self.assertEqual(groups[0]['p95_ms'], 19)
        self.assertEqual(groups[0]['transfer_bytes'], 19 * 120)

    def test_budget_defaults_origin_override_boundary(self):
        groups = summarize(capture([entry()]))
        self.assertEqual(evaluate(groups, {'*': {'requests': 0}, 'https://example.test': {'requests': 1, 'transfer_bytes': 120}})['violations'], [])
        self.assertEqual(evaluate(groups, {'*': {'transfer_bytes': 119}})['violations'][0]['metric'], 'transfer_bytes')

    def test_invalid_numeric_scheme_and_policy(self):
        for value in [float('nan'), True, -2, 1.5]:
            with self.assertRaises(ValueError):
                summarize(capture([entry(body=value)]))
        with self.assertRaises(ValueError):
            summarize(capture([entry('file:///private/path')]))
        for policy in [{'https://example.test/path': {'requests': 1}}, {'*': {'misspelled': 1}}, {'*': {'requests': -1}}]:
            with self.assertRaises(ValueError):
                evaluate([], policy)

    def test_duplicate_json_and_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.json'
            for content in ['{"a":1,"a":2}', '{"a":NaN}']:
                path.write_text(content)
                with self.assertRaises(ValueError):
                    read_json(path)

    def test_empty_capture_not_success(self):
        self.assertTrue(evaluate(summarize(capture([])), {})['empty_capture'])

    def test_cli_error_does_not_leak_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.har'
            path.write_text(json.dumps(capture([entry('https://user:secret@x:bad/private')])) )
            run = subprocess.run([sys.executable, '-m', 'har_budget', str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertNotIn('secret', run.stderr + run.stdout)


if __name__ == '__main__':
    unittest.main()
