"""Wagi, ochrona grup incydentów i izolacja treningu prostych metod priorytetu."""
from copy import deepcopy
import hashlib
import json
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from scripts import evaluate_priority_methods as methods
from scripts.evaluate_pilot import select_labels, validate_dataset


def example(ident, label, group=None, eligible=True):
    return {"id": ident, "group_id": group or ident, "base_priority": label,
            "category": "software", "reference_eligible": eligible,
            "text": f"description {ident}", "cohort": "reference" if eligible else "weak"}


class PriorityMethodsTests(unittest.TestCase):
    def test_distance_weighting_and_exact_matches(self):
        neighbors = [("high", .01), ("low", .2), ("low", .3)]
        self.assertEqual(methods.vote(neighbors, "uniform"), "low")
        self.assertEqual(methods.vote(neighbors, "distance"), "high")
        self.assertEqual(methods.vote([("high", 0), ("low", 0), ("low", .1)], "distance"), "high")
        self.assertEqual(methods.vote([("low", .2), ("high", .2)], "distance"), "low")
        with self.assertRaises(ValueError):
            methods.vote([], "uniform")

    def test_knn_excludes_paraphrases_weak_queries_and_nontraining_references(self):
        examples = [example("a", "high", "same"), example("b", "high", "same"),
                    example("c", "low"), example("d", "critical"),
                    example("weak", None, eligible=False)]
        rows = methods.predict(examples, np.ones((5, 5)), [0, 1, 2, 4], [0], {"k": 1, "weights": "uniform"})
        self.assertEqual(rows[0]["neighbor_ids"], ["c"])
        self.assertEqual(rows[0]["predicted"], "low")

    def test_tfidf_fits_only_training_texts_without_own_group_or_weak_queries(self):
        examples = [example("self", "high", "same"), example("paraphrase", "high", "same"),
                    example("low", "low"), example("high", "high"), example("weak", None, eligible=False)]
        examples[2]["text"] = "minor inconvenience workaround available"
        examples[3]["text"] = "important task blocked no workaround"
        observed = []

        class RecordingVectorizer(TfidfVectorizer):
            def fit_transform(self, raw_documents, y=None):
                observed.append(list(raw_documents))
                return super().fit_transform(raw_documents, y)

        with patch.object(methods, "TfidfVectorizer", RecordingVectorizer):
            rows = methods.predict(examples, np.ones((5, 5)), [0, 1, 2, 3, 4], [0],
                                   {"method": "tfidf_logistic", "C": 1})
        self.assertEqual(observed, [[examples[2]["text"], examples[3]["text"]]])
        self.assertEqual(len(rows), 1)

    def test_nested_splits_keep_incidents_together_and_cover_all_references_once(self):
        raw = json.loads((methods.PILOT / "tickets.en.json").read_text(encoding="utf-8"))
        refs = [row for row in validate_dataset(raw) if row.get("reference_eligible", True)]
        examples = select_labels(refs, "reviewed")
        tested = []
        for number, (train, query) in enumerate(methods.folds(examples, list(range(len(examples))), 5, methods.SEED)):
            tested.extend(query)
            train_groups = {examples[i]["group_id"] for i in train}
            query_groups = {examples[i]["group_id"] for i in query}
            self.assertFalse(train_groups & query_groups)
            for inner_train, inner_query in methods.folds(examples, train, 4, methods.SEED + number + 1):
                self.assertFalse(set(inner_train + inner_query) & set(query))
                self.assertFalse({examples[i]["group_id"] for i in inner_train}
                                 & {examples[i]["group_id"] for i in inner_query})
        self.assertEqual(sorted(tested), list(range(120)))

    def test_selection_does_not_use_labels_outside_inner_splits(self):
        examples = [example(str(i), "low" if i < 3 else "high") for i in range(6)]
        similarities = np.eye(6)
        splits = [([0, 1, 2], [3]), ([1, 2, 3], [0])]
        configs = [{"k": 1, "weights": "uniform"}, {"k": 3, "weights": "uniform"}]
        with patch.object(methods, "CONFIGS", configs):
            before = methods.select_config(examples, similarities, splits)
            examples[4]["base_priority"] = "critical"
            examples[5]["base_priority"] = "medium"
            self.assertEqual(methods.select_config(examples, similarities, splits), before)

    def test_missing_labels_are_not_successes_and_urgent_errors_are_explicit(self):
        metric = methods.metrics([{"expected": None, "predicted": "critical"},
                                  {"expected": "critical", "predicted": "medium"},
                                  {"expected": "high", "predicted": "critical"}])
        self.assertEqual((metric["scored"], metric["unscored"]), (2, 1))
        self.assertEqual(metric["classification"]["accuracy"], 0)
        self.assertEqual(metric["urgent_predicted_low_or_medium"], 1)
        self.assertEqual(metric["urgent_detection_recall"], .5)
        self.assertEqual(metric["critical_underestimated"], 1)

    def test_snapshot_verification_ignores_comments_but_detects_changed_model_inputs(self):
        snapshot = (methods.PILOT / "snapshots/tickets.en.170.v3.json").read_bytes()
        raw = json.loads((methods.PILOT / "tickets.en.json").read_text(encoding="utf-8"))
        examples = select_labels(validate_dataset(raw), "proposed")
        expected_hash = hashlib.sha256(snapshot.replace(b"\r\n", b"\n")).hexdigest()
        methods.verify_historical_inputs(examples, snapshot, expected_hash)
        changed = deepcopy(examples)
        changed[0]["text"] += " changed impact"
        with self.assertRaisesRegex(ValueError, "Wejścia"):
            methods.verify_historical_inputs(changed, snapshot, expected_hash)


if __name__ == "__main__":
    unittest.main()
