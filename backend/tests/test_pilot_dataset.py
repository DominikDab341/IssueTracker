"""Format pilotażu, decyzje przeglądu i ochrona przed przeciekiem parafraz."""
from copy import deepcopy
import json
import unittest

from scripts.evaluate_pilot import (
    DEFAULT_DATASET, CATEGORIES, classification_metrics, evaluate_vectors,
    majority, select_labels, validate_dataset,
)


class PilotDatasetTests(unittest.TestCase):
    def setUp(self):
        self.dataset = json.loads(DEFAULT_DATASET.read_text(encoding="utf-8"))

    def test_pilot_has_40_pending_examples_and_four_paraphrase_pairs(self):
        examples = validate_dataset(self.dataset)
        self.assertEqual(len(examples), 40)
        self.assertEqual(len({item["group_id"] for item in examples}), 36)
        self.assertTrue(all(item["review"]["status"] == "pending" for item in examples))
        self.assertEqual({label: sum(item["proposed_category"] == label for item in examples)
                          for label in CATEGORIES}, dict.fromkeys(CATEGORIES, 10))

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
                                reviewer="autor-test", reviewed_at="2026-10-28T18:00:00+01:00")
        with self.assertRaisesRegex(ValueError, "uzasadnienia"):
            validate_dataset(self.dataset)
        example["review"]["notes"] = "Po przeglądzie zaklasyfikowano objaw jako błąd wyświetlania aplikacji."
        validate_dataset(self.dataset)
        self.assertEqual(example["proposed_category"], "accounts_access")

    def test_review_requires_author_date_and_timezone(self):
        review = self.dataset["examples"][0]["review"]
        review.update(status="approved", category="accounts_access", base_priority="low")
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
        self.assertEqual(len(examples), 39)
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
