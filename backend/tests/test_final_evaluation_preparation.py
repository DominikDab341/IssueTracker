"""Guard the frozen references and prohibit scoring unreviewed test candidates."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.prepare_final_evaluation import (
    DEFAULT, TARGET_COUNT, candidate_summary, digest, json_bytes, validate_candidates, verify_freeze,
)


class FinalEvaluationPreparationTests(unittest.TestCase):
    def setUp(self):
        self.dataset = json.loads((DEFAULT / "candidates.json").read_bytes())
        # Keep a pending eight-case fixture even after the real collection grows
        # and receives human reviews; tests must not undo or assume those reviews.
        self.dataset["examples"] = self.dataset["examples"][:8]
        for row in self.dataset["examples"]:
            row["review"] = {"status": "pending", "category": None, "base_priority": None,
                             "reviewer": None, "reviewed_at": None, "notes": ""}
        self.references = json.loads((DEFAULT / "frozen/references.json").read_bytes())
        self.pilot = json.loads((DEFAULT / "frozen/known-pilot.en.json").read_bytes())["examples"]

    def validate(self, dataset=None, **options):
        return validate_candidates(dataset or self.dataset, self.references, self.pilot, **options)

    def test_initial_sample_is_pending_and_cannot_be_used_as_final_assessment(self):
        self.assertEqual(self.validate(), {"pending": 8})
        self.assertTrue(verify_freeze(DEFAULT / "frozen")["no_test_predictions_generated"])
        with self.assertRaisesRegex(ValueError, "complete 100-case"):
            self.validate(require_approved=True)

    def test_no_training_flags_or_known_queries_allowed_in_test(self):
        for mutation in (lambda row: row.update(reference_eligible=True),
                         lambda row: row.update(text=self.references[0]["text"]),
                         lambda row: row.update(text=self.pilot[-1]["text"]),
                         lambda row: row.update(group_id=self.pilot[0]["group_id"])):
            data = deepcopy(self.dataset)
            mutation(data["examples"][0])
            with self.assertRaises(ValueError):
                self.validate(data)

    def test_hundred_pending_cases_still_do_not_pass_the_human_review_gate(self):
        data = deepcopy(self.dataset)
        data["examples"] = []
        for index in range(TARGET_COUNT):
            row = deepcopy(self.dataset["examples"][index % 8])
            row.update(id=f"test-{index}", group_id=f"incident-{index}", text=row["text"] + f" Test location {index}.")
            data["examples"].append(row)
        with self.assertRaisesRegex(ValueError, "All 100 cases must be approved"):
            self.validate(data, require_approved=True)

    def test_review_cannot_be_fabricated_by_copying_a_proposed_label_to_pending(self):
        self.dataset["examples"][0]["review"]["category"] = "accounts_access"
        with self.assertRaisesRegex(ValueError, "Pending cases"):
            self.validate()

    def test_human_label_correction_requires_a_reason(self):
        review = self.dataset["examples"][0]["review"]
        review.update(status="approved", category="network", base_priority="high", reviewer="test-reviewer",
                      reviewed_at="2026-11-07T20:00:00+01:00")
        with self.assertRaisesRegex(ValueError, "corrections require a reason"):
            self.validate()
        review["notes"] = "Fixture only: reviewer corrected the category."
        self.assertEqual(self.validate()["approved"], 1)

    def test_weak_labels_can_be_independently_unidentifiable(self):
        full = json.loads((DEFAULT / "candidates.json").read_bytes())
        weak = next(row for row in full["examples"] if row.get("description_quality") == "weak")
        for category, priority in (("accounts_access", None), (None, "high"), (None, None)):
            data = deepcopy(self.dataset)
            row = deepcopy(weak)
            row.update(proposed_category=category, proposed_base_priority=priority)
            row["review"] = {"status": "approved", "category": category, "base_priority": priority,
                             "reviewer": "fixture-only", "reviewed_at": "2026-11-07T20:00:00+01:00",
                             "notes": "Fixture: explicitly reviewed missing information; no live human approval."}
            data["examples"] = [row]
            self.assertEqual(self.validate(data), {"approved": 1})
            del row["review"]["category"]
            with self.assertRaisesRegex(ValueError, "explicit human-reviewed labels"):
                self.validate(data)

    def test_missing_information_is_not_a_new_category_or_a_medium_default(self):
        data = deepcopy(self.dataset)
        data["examples"][0]["proposed_base_priority"] = None
        with self.assertRaisesRegex(ValueError, "Invalid proposed labels"):
            self.validate(data)
        row = data["examples"][0]
        row.update(description_quality="weak", missing_information="No impact or workaround provided.")
        self.validate(data)
        row["proposed_category"] = "unknown"
        with self.assertRaisesRegex(ValueError, "Invalid proposed labels"):
            self.validate(data)

    def test_reviewed_hundred_case_fixture_requires_the_70_30_design(self):
        data = json.loads((DEFAULT / "candidates.json").read_bytes())
        for row in data["examples"]:
            row["review"] = {"status": "approved", "category": row["proposed_category"],
                             "base_priority": row["proposed_base_priority"], "reviewer": "fixture-only",
                             "reviewed_at": "2026-11-07T20:00:00+01:00", "notes": "Fixture approval, not a real review."}
        self.assertEqual(self.validate(data, require_approved=True), {"approved": TARGET_COUNT})
        row = data["examples"][0]
        row.update(description_quality="weak", missing_information="Fixture only.")
        with self.assertRaisesRegex(ValueError, "70 complete and 30 weak"):
            self.validate(data, require_approved=True)

    def test_previous_sixty_case_collection_cannot_be_scored_as_the_final_hundred(self):
        data = json.loads((DEFAULT / "reviews/candidates-before-100.json").read_bytes())
        with self.assertRaisesRegex(ValueError, "complete 100-case"):
            self.validate(data, require_approved=True)

    def test_quality_summary_keeps_unidentifiable_denominators_explicit(self):
        data = deepcopy(self.dataset)
        row = data["examples"][0]
        row.update(description_quality="weak", proposed_category=None, proposed_base_priority="high",
                   missing_information="The source of failure is not described.")
        data["examples"] = [row]
        summary = candidate_summary(data)
        self.assertEqual(summary["quality"], {"weak": 1})
        self.assertEqual(summary["proposed_identifiable"]["weak"], {"category": 0, "priority": 1})

    def test_changed_frozen_content_and_paths_outside_snapshot_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b"reference snapshot"
            (root / "references.json").write_bytes(payload)
            manifest = {"files_sha256": {"references.json": digest(payload)}}
            (root / "manifest.json").write_bytes(json_bytes(manifest))
            verify_freeze(root)
            (root / "references.json").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "Frozen artifact changed"):
                verify_freeze(root)
            manifest["files_sha256"] = {"../outside.json": "unused"}
            (root / "manifest.json").write_bytes(json_bytes(manifest))
            with self.assertRaises(ValueError):
                verify_freeze(root)
