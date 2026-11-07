"""Select review/duplicate policies on the approved EN pilot, without the application DB."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
from importlib.metadata import version

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer

from app.services.priority_classifier import make_priority_model
from scripts.evaluate_pilot import MODEL_ID, CATEGORIES, PRIORITIES, select_labels, validate_dataset

PILOT = Path(__file__).resolve().parent.parent / "data/pilot"
OUTPUT = PILOT / "decision-policies"
REVISION = "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
SEED = 20261107


def selective_metrics(expected, predicted, accepted, labels):
    matrix = {label: {"tp": 0, "fp": 0, "fn": 0} for label in labels}
    correct = 0
    for truth, guess, use in zip(expected, predicted, accepted):
        if use and truth == guess:
            correct += 1
            matrix[truth]["tp"] += 1
        else:
            matrix[truth]["fn"] += 1
            if use:
                matrix[guess]["fp"] += 1
    f1 = []
    for row in matrix.values():
        denominator = 2 * row["tp"] + row["fp"] + row["fn"]
        f1.append(2 * row["tp"] / denominator if denominator else 0)
    count, used = len(expected), int(sum(accepted))
    return {"count": count, "accepted": used, "coverage": used / count,
            "correct_accepted_over_all": correct / count,
            "accepted_accuracy": correct / used if used else None,
            "macro_f1_with_rejections_as_false_negatives": sum(f1) / len(f1), "per_class": matrix}


def pair_metrics(pairs, similarities, categories, threshold, same_category):
    tp = fp = fn = tn = 0
    for left, right, truth in pairs:
        guess = similarities[left, right] > threshold and (not same_category or categories[left] == categories[right])
        tp += bool(guess and truth)
        fp += bool(guess and not truth)
        fn += bool(not guess and truth)
        tn += bool(not guess and not truth)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision, "recall": recall,
            "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0,
            "positive_pairs": tp + fn, "negative_pairs": fp + tn}


def split_pair_groups(examples):
    """Separate incident groups; each part gets six existing paraphrase groups."""
    groups = {}
    for index, row in enumerate(examples):
        groups.setdefault(row["group_id"], []).append(index)
    rng = np.random.default_rng(SEED)
    repeated = sorted(group for group, ids in groups.items() if len(ids) > 1)
    single = sorted(group for group, ids in groups.items() if len(ids) == 1)
    rng.shuffle(repeated)
    rng.shuffle(single)
    val_groups = set(repeated[::2] + single[::2])
    parts = {"validation": [], "held_out_diagnostic": []}
    for group, indices in groups.items():
        parts["validation" if group in val_groups else "held_out_diagnostic"].extend(indices)
    pairs = {name: [(i, j, examples[i]["group_id"] == examples[j]["group_id"])
                    for i, j in combinations(sorted(indices), 2)] for name, indices in parts.items()}
    return parts, pairs


def main():
    path = PILOT / "tickets.en.json"
    payload = path.read_bytes()
    raw = validate_dataset(json.loads(payload))
    examples = select_labels([row for row in raw if row.get("reference_eligible", True)], "reviewed")
    snapshot = snapshot_download(MODEL_ID, revision=REVISION, local_files_only=True)
    model = SentenceTransformer(snapshot, device="cpu")
    vectors = model.encode([row["text"] for row in examples], normalize_embeddings=True, show_progress_bar=False)
    vectors = np.asarray(vectors, dtype=float)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    similarities = np.clip(vectors @ vectors.T, -1, 1)
    folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    decisions = [None] * len(examples)
    split_ids = []
    for train, query in folds.split(vectors, [row["base_priority"] for row in examples],
                                    [row["group_id"] for row in examples]):
        classifier = make_priority_model()
        classifier.fit([examples[i]["text"] for i in train], [examples[i]["base_priority"] for i in train])
        probabilities = classifier.predict_proba([examples[i]["text"] for i in query])
        split_ids.append({"train": [examples[i]["id"] for i in train], "query": [examples[i]["id"] for i in query]})
        for offset, index in enumerate(query):
            nearest = sorted(train, key=lambda i: (-similarities[index, i], examples[i]["id"]))[:3]
            category = Counter(examples[i]["category"] for i in nearest).most_common(1)[0][0]
            support = [i for i in nearest if examples[i]["category"] == category]
            winner = int(probabilities[offset].argmax())
            decisions[index] = {"id": examples[index]["id"], "category": category,
                                "category_score": float(max(similarities[index, i] for i in support)),
                                "vote_share": len(support) / len(nearest),
                                "priority": str(classifier.classes_[winner]),
                                "priority_score": float(probabilities[offset, winner])}
    category_grid, priority_grid = [], []
    for threshold in np.arange(.0, .86, .01):
        for vote_share in (0, 2 / 3, 1):
            accepted = [row["category_score"] >= threshold and row["vote_share"] >= vote_share for row in decisions]
            metric = selective_metrics([row["category"] for row in examples], [row["category"] for row in decisions], accepted, CATEGORIES)
            category_grid.append({"threshold": round(float(threshold), 2), "vote_share": vote_share, "metrics": metric})
    for threshold in np.arange(.0, .96, .01):
        accepted = [row["priority_score"] >= threshold for row in decisions]
        metric = selective_metrics([row["base_priority"] for row in examples], [row["priority"] for row in decisions], accepted, PRIORITIES)
        priority_grid.append({"threshold": round(float(threshold), 2), "metrics": metric})
    def select(grid):
        return max((item for item in grid if item["metrics"]["coverage"] >= .7),
                   key=lambda item: (item["metrics"]["macro_f1_with_rejections_as_false_negatives"],
                                     item["metrics"]["correct_accepted_over_all"], item["threshold"]))
    category_choice, priority_choice = select(category_grid), select(priority_grid)
    parts, pairs = split_pair_groups(examples)
    predicted_categories = [row["category"] if row["category_score"] >= category_choice["threshold"]
                            and row["vote_share"] >= category_choice["vote_share"] else "unknown" for row in decisions]
    pair_grid = []
    for threshold in np.arange(.5, .961, .01):
        for same_category in (False, True):
            metric = pair_metrics(pairs["validation"], similarities, predicted_categories, threshold, same_category)
            pair_grid.append({"threshold": round(float(threshold), 2), "same_category": same_category, "metrics": metric})
    pair_choice = max(pair_grid, key=lambda item: (item["metrics"]["f1"], item["metrics"]["precision"], item["threshold"]))
    selected = {"category_min_similarity": category_choice["threshold"],
                "category_min_vote_share": category_choice["vote_share"],
                "priority_min_score": priority_choice["threshold"],
                "duplicate_min_similarity": pair_choice["threshold"],
                "duplicate_same_category": pair_choice["same_category"]}
    # The held-out diagnostic exposes a regression in precision. Keep the existing
    # duplicate policy rather than claiming that the validation winner generalizes.
    deployment = {**selected, "duplicate_min_similarity": .75, "duplicate_same_category": True}
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "seed": SEED,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "packages": {name: version(name) for name in ("numpy", "scikit-learn", "sentence-transformers", "torch")},
              "model_id": MODEL_ID, "model_revision": REVISION, "dataset_sha256": hashlib.sha256(payload).hexdigest(),
              "selected": selected, "deployment": deployment,
              "deployment_note": "Keep duplicate baseline .75/same-category: the validation winner regressed on held-out diagnostics. No tuning on held-out pairs.",
              "selection_policy": "OOF grouped 5-fold; macro-F1 with rejection FN; minimum coverage 0.70",
              "category": category_choice, "priority": priority_choice, "folds": split_ids, "decisions": decisions,
              "category_grid": category_grid, "priority_grid": priority_grid,
              "duplicates": {"label_provenance": "same/different group_id in the existing approved pilot; no new human approval claimed",
                             "selection": pair_choice, "validation_grid": pair_grid,
                             "parts": {name: [examples[i]["id"] for i in indices] for name, indices in parts.items()},
                             "pairs": {name: [{"left": examples[i]["id"], "right": examples[j]["id"], "duplicate": truth}
                                              for i, j, truth in rows] for name, rows in pairs.items()},
                             "results": {name: {
                                 "old": pair_metrics(rows, similarities, predicted_categories, .75, True),
                                 "selected": pair_metrics(rows, similarities, predicted_categories, selected["duplicate_min_similarity"], selected["duplicate_same_category"]),
                                 "without_category": pair_metrics(rows, similarities, predicted_categories, selected["duplicate_min_similarity"], False),
                                 "with_category": pair_metrics(rows, similarities, predicted_categories, selected["duplicate_min_similarity"], True)} for name, rows in pairs.items()}}}
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "policy.json").write_text(json.dumps({"schema_version": 1, "selected": selected, "deployment": deployment,
        "model_revision": REVISION, "dataset_sha256": report["dataset_sha256"]}, indent=2) + "\n", encoding="utf-8")
    lines = ["# Polityki weryfikacji i sugestii duplikatów", "", f"Pomiar: {report['generated_at']}", "",
             "120 zatwierdzonych EN; progi klasyfikacji wybrane wyłącznie z przewidywań poza własną grupą (5 foldów).",
             "Maksymalizujemy macro-F1 z odmowami liczonymi jako FN; minimum 70% pokrycia jest przyjętym ograniczeniem użytkowym.",
             "Wynik TF-IDF jest niekalibrowanym wynikiem modelu, nie potwierdzonym prawdopodobieństwem poprawności.", "",
             "| Decyzja | Próg | Pokrycie | Accuracy zaakceptowanych |", "|---|---:|---:|---:|"]
    for name, choice in (("Kategoria", category_choice), ("Priorytet", priority_choice)):
        metric = choice["metrics"]
        lines.append(f"| {name} | {choice['threshold']:.2f} | {metric['coverage']:.1%} | {metric['accepted_accuracy']:.1%} |")
    lines += ["", f"Minimalny udział głosów kategorii: {selected['category_min_vote_share']:.3f}.",
              f"Próg podobieństwa duplikatów: >{selected['duplicate_min_similarity']}; filtr kategorii: {selected['duplicate_same_category']}.", "",
              "## Pary duplikatów", "", "Etykiety wyprowadzono z istniejących group_id, bez dopisywania nowego zatwierdzenia przez człowieka.",
              "Grupy incydentów walidacji i wydzielonej próby diagnostycznej są rozłączne. Wszystkie pary w każdej części są oceniane, w tym trudne podobne pary ujemne.",
              "Filtr kategorii używa kategorii operacyjnych przewidywanych poza własną grupą po zastosowaniu polityki weryfikacji, nie etykiet wzorcowych.", "",
              "| Część | Wariant | TP | FP | FN | Precision | Recall | F1 |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for name, results in report["duplicates"]["results"].items():
        for variant, metric in results.items():
            lines.append(f"| {name} | {variant} | {metric['tp']} | {metric['fp']} | {metric['fn']} | {metric['precision']:.1%} | {metric['recall']:.1%} | {metric['f1']:.3f} |")
    lines += ["", "## Ograniczenia", "", "To diagnostyka na znanym, syntetycznym pilotażu; nie niezależny test końcowy ani wynik na danych organizacji.",
              "Kandydat 0.67 / bez filtra kategorii pogorszył precision na wydzielonej próbie. W aplikacji zachowujemy 0.75 i filtr kategorii; nie dostrajamy nowego progu do wyników tej próby.",
              "W każdej części jest niewiele par dodatnich; dobór progu może być niestabilny. Podobny tekst nie dowodzi wspólnej awarii.",
              "Podział, wszystkie pary, surowe przewidywania i siatki są zapisane w [report.json](report.json).",
              "50 słabych pending nie bierze udziału w doborze progów ani treningu.", ""]
    (OUTPUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(selected))
    print(json.dumps(report["duplicates"]["results"], indent=2))


if __name__ == "__main__":
    main()
