"""Decision metrics penalize rejected true classes; duplicate incidents never cross splits."""
import json
import unittest

from scripts.evaluate_decision_policies import PILOT, selective_metrics, split_pair_groups
from scripts.evaluate_pilot import select_labels, validate_dataset


class PolicyEvaluationTests(unittest.TestCase):
    def test_rejecting_everything_cannot_create_a_perfect_score(self):
        result = selective_metrics(['low', 'high'], ['low', 'low'], [False, False], ('low', 'high'))
        self.assertEqual(result['coverage'], 0)
        self.assertEqual(result['macro_f1_with_rejections_as_false_negatives'], 0)
        self.assertIsNone(result['accepted_accuracy'])
        partial = selective_metrics(['low', 'high'], ['low', 'low'], [True, False], ('low', 'high'))
        self.assertEqual(partial['accepted_accuracy'], 1)
        self.assertEqual(partial['correct_accepted_over_all'], .5)
        self.assertEqual(partial['macro_f1_with_rejections_as_false_negatives'], .5)

    def test_duplicate_partitions_have_disjoint_incident_groups_and_both_labels(self):
        raw = validate_dataset(json.loads((PILOT / 'tickets.en.json').read_text(encoding='utf-8')))
        examples = select_labels([row for row in raw if row.get('reference_eligible', True)], 'reviewed')
        parts, pairs = split_pair_groups(examples)
        a, b = parts.values()
        self.assertFalse({examples[i]['group_id'] for i in a} & {examples[i]['group_id'] for i in b})
        for name, rows in pairs.items():
            self.assertEqual(sum(truth for _, _, truth in rows), 6)
            self.assertGreater(sum(not truth for _, _, truth in rows), 100)
            self.assertTrue(all(i in parts[name] and j in parts[name] for i, j, _ in rows))
