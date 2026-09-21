from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from instrumentation.request_correlated_trace import JsonlRuntimeTrace


class JsonlRuntimeTraceTest(unittest.TestCase):
    def test_records_expected_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.jsonl"

            with JsonlRuntimeTrace(path, flush_every=1) as trace:
                trace.record(
                    "request_scheduled",
                    request_id="req-1",
                    iteration_id=7,
                    scheduled_tokens=32,
                    running_count=2,
                    waiting_count=1,
                    token_budget_remaining=96,
                    preempted=False,
                )

            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(rows), 1)

            row = rows[0]
            self.assertEqual(row["event"], "request_scheduled")
            self.assertEqual(row["request_id"], "req-1")
            self.assertEqual(row["iteration_id"], 7)
            self.assertEqual(row["scheduled_tokens"], 32)
            self.assertEqual(row["running_count"], 2)
            self.assertEqual(row["waiting_count"], 1)
            self.assertEqual(row["token_budget_remaining"], 96)
            self.assertFalse(row["preempted"])
            self.assertIsInstance(row["timestamp_ns"], int)


if __name__ == "__main__":
    unittest.main()
