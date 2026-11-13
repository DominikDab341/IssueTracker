import unittest

from app.services.priority_information import needs_priority_information


class PriorityInformationTests(unittest.TestCase):
    def test_sparse_symptom_or_failed_attempt_requires_review(self):
        for description in (
            "The printer keeps jamming.",
            "The print job failed. The backup never works.",
            "The tool froze. I’m not sure if I can work normally.",
        ):
            with self.subTest(description=description):
                self.assertTrue(needs_priority_information(description))

    def test_short_descriptions_with_impact_or_workaround_can_pass(self):
        for description in (
            "The case is scratched. I can work normally.",
            "The scanner jammed. The spare scanner works.",
            "I cannot complete the job and there is no other route.",
        ):
            with self.subTest(description=description):
                self.assertFalse(needs_priority_information(description))

    def test_conditional_workaround_does_not_confirm_impact(self):
        for description in (
            "The portal crashed. I can work using the web version, if IT gives me access.",
            "If IT gives me access, I can work using the web version.",
            "The portal crashed. I can work using the web version once IT grants access.",
        ):
            with self.subTest(description=description):
                self.assertTrue(needs_priority_information(description))
        self.assertFalse(needs_priority_information("I can work using the web version. If it fails, I will call IT."))

    def test_negated_outage_does_not_confirm_blocked_work(self):
        for description in (
            "The service is not down. No workaround has been documented.",
            "The service isn't down. No workaround has been documented.",
            "The service is no longer down. No workaround has been documented.",
        ):
            with self.subTest(description=description):
                self.assertTrue(needs_priority_information(description))
        self.assertFalse(needs_priority_information("The service is not down and the work is blocked. No workaround."))

    def test_longer_description_needs_no_specific_english_phrase(self):
        description = (
            "Every courier is waiting for a dispatch barcode. The encoder is empty, "
            "and our courier service rejects handwritten labels under the collection agreement."
        )
        self.assertFalse(needs_priority_information(description))
