"""Format pilotażu, decyzje przeglądu i ochrona przed przeciekiem parafraz."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.evaluate_pilot import (
    DEFAULT_DATASET, CATEGORIES, classification_metrics, evaluate_vectors,
    majority, select_labels, summarize_predictions, validate_dataset, write_report,
)


class PilotDatasetTests(unittest.TestCase):
    def setUp(self):
        self.dataset = json.loads(DEFAULT_DATASET.read_text(encoding="utf-8"))

    def test_expanded_pilot_has_120_approved_references_and_50_weak_queries(self):
        examples = validate_dataset(self.dataset)
        references = [row for row in examples if row.get("reference_eligible", True)]
        weak = [row for row in examples if not row.get("reference_eligible", True)]
        self.assertEqual(len(examples), 170)
        self.assertEqual(len({item["group_id"] for item in examples}), 158)
        self.assertEqual(len(references), 120)
        self.assertEqual(len(weak), 50)
        self.assertTrue(all(row["review"]["status"] == "approved" for row in references))
        self.assertTrue(all(row["review"]["status"] == "pending" for row in weak))
        self.assertEqual(sum(row["proposed_category"] is not None for row in weak), 30)
        self.assertEqual(sum(row["proposed_base_priority"] is not None for row in weak), 10)
        self.assertEqual(len(select_labels(references, "reviewed")), 120)
        self.assertEqual({label: sum(item["proposed_category"] == label for item in references)
                          for label in CATEGORIES}, dict.fromkeys(CATEGORIES, 30))
        snapshot = json.loads((DEFAULT_DATASET.parent / "snapshots/tickets.pl.40.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(len(validate_dataset(snapshot)), 40)
        current = {row["id"]: row for row in examples}
        for original in snapshot["examples"]:
            row = current[original["id"]]
            for field in ("text", "group_id", "proposed_category", "proposed_base_priority", "work_blocked"):
                self.assertEqual(row[field], original[field])
            self.assertEqual(row["review"]["category"], original["proposed_category"])
            self.assertEqual(row["review"]["base_priority"], original["proposed_base_priority"])

    def test_english_translation_preserves_the_paired_experiment(self):
        english = json.loads(DEFAULT_DATASET.with_name("tickets.en.json").read_text(encoding="utf-8"))
        translated = validate_dataset(english)
        self.assertEqual(english["language"], "en")
        self.assertNotEqual(english["dataset_id"], self.dataset["dataset_id"])
        source = english["provenance"]["translation"]
        self.assertEqual(source["source_sha256"], hashlib.sha256(DEFAULT_DATASET.read_bytes()).hexdigest())
        self.assertFalse(source["human_verified"])
        self.assertEqual({row["id"] for row in translated}, {row["id"] for row in self.dataset["examples"]})
        originals = {row["id"]: row for row in self.dataset["examples"]}
        for row in translated:
            with self.subTest(id=row["id"]):
                original = originals[row["id"]]
                for field in ("group_id", "proposed_category", "proposed_base_priority", "work_blocked"):
                    self.assertEqual(row[field], original[field])
                self.assertNotEqual(row["text"], original["text"])
                self.assertEqual(row["review"]["status"], original["review"]["status"])
                for field in ("category", "base_priority"):
                    self.assertEqual(row["review"][field], original["review"][field])

    def test_truncated_expansion_is_rejected(self):
        self.dataset["examples"].pop()
        with self.assertRaisesRegex(ValueError, "170"):
            validate_dataset(self.dataset)

    def test_unlabelled_reference_is_rejected(self):
        self.dataset["examples"][0]["proposed_category"] = None
        with self.assertRaisesRegex(ValueError, "etykiety"):
            validate_dataset(self.dataset)

    def test_unavailable_labels_are_not_scored_as_errors_or_successes(self):
        rows = [dict(expected_category="network", predicted_category="network",
                     expected_base_priority=None, predicted_base_priority="high"),
                dict(expected_category=None, predicted_category="software",
                     expected_base_priority="low", predicted_base_priority="low")]
        summary = summarize_predictions(rows)
        for task in ("category", "base_priority"):
            self.assertEqual(summary["metrics"][task]["accuracy"], 1.0)
            self.assertEqual(summary["scoring"][task], {"scored": 1, "unscored": 1, "coverage": .5})
            self.assertEqual(summary["insufficient_information"][task]["forced_predictions"], 1)
        missing = summarize_predictions([dict(expected_category=None, predicted_category="network",
                                              expected_base_priority=None, predicted_base_priority="high")])
        self.assertEqual(missing["metrics"], {"category": None, "base_priority": None})
        self.assertIsNone(missing["fixed_medium_baseline"])

    def test_weak_query_never_becomes_another_examples_neighbor(self):
        examples = [dict(id="a", group_id="a", category="network", base_priority="low"),
                    dict(id="b", group_id="b", category="software", base_priority="high"),
                    dict(id="weak", group_id="weak", category=None, base_priority=None,
                         reference_eligible=False, cohort="weak")]
        rows = evaluate_vectors(examples, [[1, 0], [0, 1], [1, 0]], k=1)
        self.assertEqual(rows[0]["neighbors"][0]["id"], "b")
        self.assertEqual(rows[2]["predicted_category"], "network")
        self.assertTrue(all(n["id"] != "weak" for row in rows for n in row["neighbors"]))

    def test_reports_append_markdown_and_archive_previous_json(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            previous = b'{"previous": true}\n'
            prefix = b'# Previous result\r\n\r\n40 examples\r\n'
            (output / "report.json").write_bytes(previous)
            (output / "report.md").write_bytes(prefix)
            first = {"count": 120, "generated_at": "2026-11-01T14:00:00+01:00"}
            first_path = write_report(first, output, "# Result\n\n120 examples\n")
            self.assertTrue((output / "report.md").read_bytes().startswith(prefix))
            self.assertTrue(any(path.read_bytes() == previous for path in (output / "runs").glob("*.json")))
            first_bytes = first_path.read_bytes()
            first_markdown = (output / "report.md").read_bytes()
            second = dict(first, generated_at="2026-11-01T15:00:00+01:00")
            write_report(second, output, "# Next result\n\nAnother run\n")
            self.assertTrue((output / "report.md").read_bytes().startswith(first_markdown))
            self.assertEqual(first_path.read_bytes(), first_bytes)
            self.assertEqual(json.loads((output / "report.json").read_text()), second)

    def test_unsupported_language_is_rejected(self):
        self.dataset["language"] = "de"
        with self.assertRaisesRegex(ValueError, "pl lub en"):
            validate_dataset(self.dataset)

    def test_duplicate_ids_and_invalid_boolean_are_rejected(self):
        for mutation in (lambda rows: rows[1].update(id=rows[0]["id"]),
                         lambda rows: rows[0].update(work_blocked="false")):
            with self.subTest(mutation=mutation):
                data = deepcopy(self.dataset)
                mutation(data["examples"])
                with self.assertRaises(ValueError):
                    validate_dataset(data)

    def test_reviewed_evaluation_refuses_proposed_labels(self):
        with self.assertRaisesRegex(ValueError, "ręczny przegląd"):
            select_labels(self.dataset["examples"], "reviewed")

    def test_corrections_preserve_proposals_and_require_a_reason(self):
        example = self.dataset["examples"][0]
        example["review"].update(status="approved", category="software", base_priority="low",
                                reviewer="autor-test", reviewed_at="2026-10-28T18:00:00+01:00", notes=None)
        with self.assertRaisesRegex(ValueError, "uzasadnienia"):
            validate_dataset(self.dataset)
        example["review"]["notes"] = "Po przeglądzie zaklasyfikowano objaw jako błąd wyświetlania aplikacji."
        validate_dataset(self.dataset)
        self.assertEqual(example["proposed_category"], "accounts_access")

    def test_review_requires_author_date_and_timezone(self):
        review = self.dataset["examples"][0]["review"]
        review.update(status="approved", category="accounts_access", base_priority="low", reviewer=None, reviewed_at=None)
        with self.assertRaisesRegex(ValueError, "autora i daty"):
            validate_dataset(self.dataset)
        review.update(reviewer="autor-test", reviewed_at="2026-10-28T18:00:00")
        with self.assertRaisesRegex(ValueError, "strefę"):
            validate_dataset(self.dataset)

    def test_reviewed_labels_and_exclusion_are_used(self):
        for item in self.dataset["examples"]:
            item["review"].update(status="approved", category=item["proposed_category"],
                                  base_priority=item["proposed_base_priority"], reviewer="autor-test",
                                  reviewed_at="2026-10-28T18:00:00+01:00")
        self.dataset["examples"][0]["review"].update(category="software", notes="Korekta kategorii po przeglądzie.")
        self.dataset["examples"][1]["review"].update(status="excluded", notes="Za mało informacji w treści.")
        examples = select_labels(validate_dataset(self.dataset), "reviewed")
        self.assertEqual(len(examples), 169)
        self.assertEqual(examples[0]["category"], "software")
        self.assertNotIn("ACC-02", [item["id"] for item in examples])

    def test_nearest_paraphrase_is_excluded_with_its_entire_group(self):
        examples = [
            dict(id="a", group_id="same", category="hardware", base_priority="low"),
            dict(id="b", group_id="same", category="hardware", base_priority="low"),
            dict(id="c", group_id="other", category="software", base_priority="high"),
            dict(id="d", group_id="third", category="network", base_priority="medium"),
        ]
        predictions = evaluate_vectors(examples, [[1, 0], [1, 0], [.9, .1], [0, 1]], k=1)
        self.assertEqual(predictions[0]["neighbors"][0]["id"], "c")
        for row in predictions:
            self.assertTrue(all(item["group_id"] != row["group_id"] for item in row["neighbors"]))

    def test_vote_ties_choose_nearest_label_and_equal_similarity_uses_id(self):
        self.assertEqual(majority(["high", "low", "medium"]), "high")
        examples = [dict(id=ident, group_id=ident, category=category, base_priority="low")
                    for ident, category in (("z", "network"), ("b", "hardware"), ("a", "software"))]
        rows = evaluate_vectors(examples, [[1, 0], [1, 0], [1, 0]], k=1)
        self.assertEqual(rows[0]["predicted_category"], "software")
        with self.assertRaisesRegex(ValueError, "za mało"):
            evaluate_vectors(examples, [[1, 0], [1, 0], [1, 0]], k=3)

    def test_metrics_include_missing_classes_with_zero_f1(self):
        metrics = classification_metrics(["low", "high"], ["low", "low"], ("low", "high", "critical"))
        self.assertEqual(metrics["accuracy"], .5)
        self.assertEqual(metrics["confusion_matrix"], [[1, 0, 0], [1, 0, 0], [0, 0, 0]])
        self.assertAlmostEqual(metrics["macro_f1"], 2 / 9)
        with self.assertRaises(ValueError):
            classification_metrics(["low"], [], ("low",))
        with self.assertRaises(ValueError):
            classification_metrics(["unknown"], ["low"], ("low",))


if __name__ == "__main__":
    unittest.main()
