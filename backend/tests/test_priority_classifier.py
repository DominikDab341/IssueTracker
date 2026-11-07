"""Runtime TF-IDF: model reuse, data versions and separation from KNN."""
import unittest
from unittest.mock import patch

from app.services import priority_classifier as priority


class PriorityClassifierTests(unittest.TestCase):
    def setUp(self):
        self.references = [
            {"source_key": "low", "text": "Cosmetic display issue, all work is possible", "category": "software", "base_priority": "low"},
            {"source_key": "medium", "text": "Work is slower but a working workaround is available", "category": "hardware", "base_priority": "medium"},
            {"source_key": "high", "text": "Important task is blocked, no working workaround", "category": "accounts_access", "base_priority": "high"},
            {"source_key": "critical", "text": "Essential service unavailable, entire company cannot work", "category": "network", "base_priority": "critical"},
        ]
        self.options = dict(source="unit-v1", model_name="MiniLM", model_revision="fixed")

    def test_runtime_learns_priorities_and_reuses_the_same_version(self):
        with patch.object(priority, "_cached_version", None), patch.object(priority, "_cached_model", None):
            with patch.object(priority, "make_priority_model", wraps=priority.make_priority_model) as build:
                versions = set()
                for row in self.references:
                    result, version = priority.predict_priority(row["text"], self.references, **self.options)
                    self.assertEqual(result, row["base_priority"])
                    versions.add(version)
                self.assertEqual(len(versions), 1)
                build.assert_called_once()
                self.references[0]["base_priority"] = "high"
                result, changed_version = priority.predict_priority(self.references[0]["text"], self.references, **self.options)
                self.assertEqual(result, "high")
                self.assertNotIn(changed_version, versions)
                self.assertEqual(build.call_count, 2)

    def test_empty_and_single_class_reference_sets(self):
        result, version = priority.predict_priority("Any new ticket", [], **self.options)
        self.assertIsNone(result)
        self.assertTrue(version.startswith("helpdesk-v1:"))
        result, _ = priority.predict_priority("Any new ticket", self.references[:1], **self.options)
        self.assertEqual(result, "low")
