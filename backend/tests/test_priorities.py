import unittest

from app.domain import Priority, PrioritySource
from app.services.priorities import determine_priority


class PriorityDecisionTests(unittest.TestCase):
    def test_manual_decision_wins_over_checkbox_and_automatic_priority(self):
        for manual in Priority:
            for automatic in [None, *Priority]:
                for blocked in [False, True]:
                    decision = determine_priority(manual_priority=manual, work_blocked=blocked,
                                                  automatic_priority=automatic)
                    self.assertEqual(decision.priority, manual)
                    self.assertEqual(decision.source, PrioritySource.ADMINISTRATOR)

    def test_checkbox_is_critical_without_manual_decision(self):
        for automatic in [None, *Priority]:
            decision = determine_priority(manual_priority=None, work_blocked=True,
                                          automatic_priority=automatic)
            self.assertEqual(decision.priority, Priority.CRITICAL)
            self.assertEqual(decision.source, PrioritySource.WORK_BLOCKED)

    def test_automatic_priority_is_preserved_without_overrides(self):
        for automatic in Priority:
            decision = determine_priority(manual_priority=None, work_blocked=False,
                                          automatic_priority=automatic)
            self.assertEqual(decision.priority, automatic)
            self.assertEqual(decision.source, PrioritySource.AUTOMATIC)

    def test_missing_or_unknown_predictions_use_explicit_fallback(self):
        for automatic in [None, "unknown", "invalid"]:
            decision = determine_priority(manual_priority=None, work_blocked=False,
                                          automatic_priority=automatic)
            self.assertEqual(decision.priority, Priority.MEDIUM)
            self.assertEqual(decision.source, PrioritySource.FALLBACK)
