"""Check holdout denominators, review penalties, replay ranking and immutable seals."""
import asyncio
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.evaluate_final_classification import (
    CATEGORIES, DEFAULT, MemoryReferences, classification_metrics, seal, summarize,
)


def prediction(**overrides):
    row = {"expected_category": "software", "expected_priority": "high", "raw_category": "software",
           "raw_priority": "high", "accepted_category": "software", "accepted_priority": "high"}
    return {**row, **overrides}


class FinalClassificationMetricsTests(unittest.TestCase):
    def test_rejecting_known_answers_is_not_perfect_accuracy(self):
        rows = [prediction(accepted_category=None), prediction(expected_category="network", raw_category="network", accepted_category=None)]
        result = summarize(rows, "category")
        self.assertEqual(result["raw"]["accuracy"], 1)
        self.assertEqual(result["operational"]["accuracy"], 0)
        self.assertEqual(result["operational"]["macro_f1"], 0)
        self.assertEqual(result["known_coverage"], 0)
        self.assertIsNone(result["accepted_accuracy"])
        self.assertEqual(result["operational"]["confusion_matrix"][2][-1], 1)

    def test_unknown_labels_do_not_enter_accuracy_or_become_medium(self):
        rows = [prediction(), prediction(expected_category=None, expected_priority=None)]
        for dimension in ("category", "priority"):
            result = summarize(rows, dimension)
            self.assertEqual(result["identifiable"], 1)
            self.assertEqual(result["unidentifiable"], 1)
            self.assertEqual(result["raw"]["accuracy"], 1)
            self.assertEqual(result["unidentifiable_automatic_count"], 1)
            self.assertEqual(result["unidentifiable_review_rate"], 0)

    def test_independent_category_and_priority_denominators_and_review(self):
        rows = [prediction(expected_category=None, accepted_category=None)]
        category, priority = summarize(rows, "category"), summarize(rows, "priority")
        self.assertEqual(category["identifiable"], 0)
        self.assertIsNone(category["raw"]["accuracy"])
        self.assertEqual(category["unidentifiable_review_rate"], 1)
        self.assertEqual(priority["identifiable"], 1)
        self.assertEqual(priority["operational"]["accuracy"], 1)

    def test_urgent_deferral_is_distinct_from_accepted_low_priority(self):
        rows = [prediction(raw_priority="medium", accepted_priority=None),
                prediction(expected_priority="critical", raw_priority="low", accepted_priority="low")]
        result = summarize(rows, "priority")
        self.assertEqual(result["urgent"]["raw_as_low_medium"], 2)
        self.assertEqual(result["urgent"]["accepted_as_low_medium"], 1)
        self.assertEqual(result["urgent"]["deferred"], 1)
        self.assertEqual(result["urgent"]["critical_raw_underestimated"], 1)
        self.assertEqual(result["always_medium_baseline"]["accuracy"], 0)

    def test_metrics_reject_unknown_truth_instead_of_silently_dropping_it(self):
        with self.assertRaises(ValueError):
            classification_metrics([None], ["software"], CATEGORIES)

    def test_cosine_replay_normalizes_vectors_and_breaks_ties_by_reference_id(self):
        from sqlalchemy import literal, select
        refs = [{"id": ident, "embedding_vector": [scale] + [0.0] * 383,
                 "source_key": str(ident), "source": "pilot", "category": "hardware", "text": "fixture", "base_priority": "low"}
                for ident, scale in ((9, 2.0), (2, 20.0))]
        adapter = MemoryReferences(refs)
        result = asyncio.run(adapter.execute(select(literal([5.0] + [0.0] * 383))))
        rows = result.mappings().all()
        self.assertEqual([row["source_key"] for row in rows], ["2", "9"])
        self.assertTrue(all(abs(row["distance"]) < 1e-12 for row in rows))

    def test_seal_refuses_pending_data_and_never_overwrites_existing_holdout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(DEFAULT / "frozen", root / "frozen")
            data = json.loads((DEFAULT / "candidates.json").read_bytes())
            data["examples"][0]["review"] = {"status": "pending", "category": None, "base_priority": None,
                                             "reviewer": None, "reviewed_at": None, "notes": ""}
            (root / "candidates.json").write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "All 100 cases"):
                seal(root)
            self.assertFalse((root / "sealed").exists())
            (root / "sealed").mkdir()
            with self.assertRaisesRegex(ValueError, "will not be overwritten"):
                seal(root)
