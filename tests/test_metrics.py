from __future__ import annotations

import unittest

from experiments.streaming_benchmark import make_prompt
from scripts.analyze_benchmark import percentile, summarize


class MetricsTest(unittest.TestCase):
    def test_percentile_interpolates(self) -> None:
        values = [1.0, 2.0, 3.0, 4.0]
        self.assertAlmostEqual(percentile(values, 0.5), 2.5)

    def test_summary_contains_expected_statistics(self) -> None:
        stats = summarize([1.0, 2.0, 3.0])
        self.assertEqual(stats["min"], 1.0)
        self.assertEqual(stats["max"], 3.0)
        self.assertEqual(stats["median"], 2.0)

    def test_prompt_contains_request_identity(self) -> None:
        prompt = make_prompt(3, 2)
        self.assertIn("request_id=3", prompt)
        self.assertIn("runtime runtime", prompt)


if __name__ == "__main__":
    unittest.main()
